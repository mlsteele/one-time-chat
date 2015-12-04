#!/usr/bin/env python
"""
Usage:
 storetool.py UID1 UID2
              (-b NBYTES | -k NKBYTES| -m NMBYTES)
              [-v | --verbose] [-s SVC]
 storetool.py (-h | --help)

Arguments:
 UID1   The User ID of the first person (e.g. alice)
 UID2   The User ID of the second person (e.g. bob)

Options:
-b NBYTES             Number of bytes to generate
-k NKBYTES            Number of kibibytes to generate
-m NMBYTES            Number of mebibytes to generate
-s SVC --service=SVC  RNG service to use; must be either random
                      or urandom. [default: random]
-v --verbose          Be verbose
-h --help             Show this screen and exit
"""

from metadata import *
from docopt import docopt
import hashlib
import os
import time
import json
import logging

KiB = 1024;
MiB = 1024 * KiB;
GiB = 1024 * MiB;

DEBUG = 2

# Benchmark: 106 seconds for 1 MiB. That's 
#  9.66 KiB / sec. With random.
# urandom is <1 sec per MiB.
def make_random_blob(f0, f1, uid0, uid1, n_bytes, rservice):
    """Make a random store blob. Uses hardware-RNG
       along with /dev/random so that there is high
       entropy. Unless the user specifies urandom in
       which case this uses urandom instead of
       random.

    Args:
       f0, f1: The file objects for the two users
       uid0, uid1: The ids of the two users
       n_bytes: Size in bytes of the target
       rservice: random or urandom
    """

    n_Kbytes = n_bytes / KiB
    n_leftoverbytes = n_bytes - (n_Kbytes * KiB)

    # Make sure the HRNG is running for service random
    if rservice == "random":
        os.system("/etc/init.d/rng-tools start")

    log()
    log("Generating {} random bytes".format(n_bytes) +
        " with OS service '{}'".format(rservice), 0)
    log("Target files: {} and {}".format(f0.name, f1.name))
    log()

    # Will store # of bytes generated
    n = 0
    # Time and execute random generation
    t1 = time.time()
    while(True):
        with open("/dev/" + rservice, "rb") as rand:
            # So there's usually around 3000 bits of entropy
            #  available (4096 at most). That's 512 bytes.
            #  I don't know why but 1024 bytes at a time seems
            #  to work the best.
            nbytes2write = KiB if n_bytes - n >= KiB else n_bytes - n
            randobytes = rand.read(nbytes2write)
            f0.write(randobytes)
            f1.write(randobytes)
            n += nbytes2write
            log("Wrote kilobyte chunk {}/{}"
                .format(n/KiB,(n_bytes+KiB-1)/KiB), 2, n%KiB==0)
            log("Wrote final {} bytes"
                .format(nbytes2write), 2, n%KiB!=0)
            log("Wrote megabyte chunk {}/{}"
                .format(n/MiB,(n_bytes+MiB-1)/MiB), 0, n%MiB==0)
            if n >= n_bytes:
                break

    t2 = time.time()

    log()
    log("Random number generation complete!")
    log(" - amount random data: {} bytes".format(n_bytes) +
        " ({} KiB)".format(1.0*n_bytes / KiB))
    log(" - time elapsed: {} seconds".format(t2 - t1))
    log(" - throughput: {} KiB/s".format((1.0*n_bytes/KiB) / (t2 - t1)))
    log()
    log("{} random bytes have been written to {} and {}"
        .format(n_bytes, f0.name, f1.name))

    make_metadata(uid0, uid1, n_bytes, rservice)

def make_metadata(uid0, uid1, n_bytes, rservice):
    def make_data(uid, rid, direction):
        assert direction in [1,-1]
        data = {}
        data["uid"] = uid
        data["rid"] = rid
        data["store_filename"] = get_storefile_name(uid, rid)
        data["metadata_filename"] = get_metadatafile_name(uid, rid)
        data["n_bytes"] = n_bytes
        data["rservice"] = rservice
        data["split_index"] = n_bytes / 2
        data["direction"] = direction
        data["encrypt_index"] = 0 if direction == 1 else n_bytes-1
        data["decrypt_log"] = ""
        data["decrypt_max"] = n_bytes-1 if direction == 1 else 0
        # These two must always go last, in this order
        data["n_eles"] = len(data.items())+2
        data["checksum"] = hash(frozenset(data.items()))
        return data

    data = [make_data(uid0, uid1, 1), make_data(uid1, uid0, -1)]

    mfile = [data[0]["metadata_filename"], data[1]["metadata_filename"]]
    sfile = [data[0]["store_filename"], data[1]["store_filename"]]

    with open(mfile[0], "w") as metadata0, open(mfile[1], "w") as metadata1:
        metadata0.write(json.dumps(data[0]))
        metadata1.write(json.dumps(data[1]))
    log("metadata for {} and {} have been written to {} and {}, respectively"
        .format(sfile[0], sfile[1], mfile[0], mfile[1]))

# d: 0 = production, 1 = status messages, 2 = full debug
def log(msg=-1, d=0, condition=True):
    if DEBUG >= d and condition:
        if msg == -1:
            print("")
            return
        header = "[]"
        if d == 0:
            header = "[INFO]"
            logging.info(msg)
        elif d == 1:
            header = "[STATUS]"
            logging.info(msg)
        elif d == 2:
            header = "[DEBUG]"
            logging.debug(msg)
        print(header + " " + msg)

if __name__ == "__main__":
    logging.basicConfig(filename='generate.log', 
                        level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    args = docopt(__doc__)
    
    uid0 = args["UID1"]
    uid1 = args["UID2"]
    rservice = args["--service"]
    verbose = args["--verbose"]
    
    _units = ""
    if args["-b"]:
        _units = "-b"
        _multFactor = 1
    elif args["-k"]:
        _units = "-k"
        _multFactor = KiB
    elif args["-m"]:
        _units = "-m"
        _multFactor = MiB

    # Input validation:
    try:
        n_bytes = int(args[_units]) * _multFactor
        if n_bytes < 0:
            raise ValueError("Can't be a negative number of bytes!")
    except:
        exit("Invalid value of NBYTES!")
    if rservice not in ["random","urandom"]:
        exit("'{}' is not a valid service. ".format(rservice) +
             "Service must be one of {random,urandom}")
    filepath1 = get_storefile_name(uid0, uid1)
    filepath2 = get_storefile_name(uid1, uid0)
    DEBUG = 2 if verbose else 0
    with open(filepath1, "wb") as f1, open(filepath2, 'wb') as f2:
        make_random_blob(f1, f2, uid0, uid1, n_bytes, rservice)

    logging.shutdown()
