#!/usr/bin/env python
"""
Usage:
 storetool.py (-b NBYTES | -k NKBYTES| -m NMBYTES)
              [-v | --verbose] [-s SVC] [-f FILE]
 storetool.py (-h | --help)

Options:
-b NBYTES             Number of bytes to generate
-k NKBYTES            Number of kibibytes to generate
-m NMBYTES            Number of mebibytes to generate
-s SVC --service=SVC  RNG service to use; must be either random
                      or urandom. [default: urandom]
-f FILE --file=FILE   Output file [default: random.store]
-v --verbose          Be verbose
-h --help             Show this screen and exit
"""

from docopt import docopt
import hashlib
import os
import time

KiB = 1024;
MiB = 1024 * KiB;
GiB = 1024 * MiB;

DEBUG = 2

# Benchmark: 106 seconds for 1 MiB. That's 
#  9.66 KiB / sec. With random.
# urandom is <1 sec per MiB.
def make_random_blob(f, n_bytes=KiB, rservice="random"):
    """Make a random store blob. Uses hardware-RNG
       along with /dev/random so that there is high
       entropy. Unless the user specifies urandom in
       which case this uses urandom instead of
       random.

    Args:
       f: A file object to write to
       n_bytes: Size in bytes of the target
       rservice: random or urandom
    """

    n_Kbytes = n_bytes / KiB
    n_leftoverbytes = n_bytes - (n_Kbytes * KiB)

    # Make sure the HRNG is running
    os.system("/etc/init.d/rng-tools start")

    log()
    log("Generating {} random bytes".format(n_bytes) +
        " with OS service '{}'".format(rservice), 0)
    log("Target file: {}".format(f.name))
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
            f.write(randobytes)
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
    log("{} random bytes have been written to {}".format(n_bytes, f.name))

# d: 0 = production, 1 = status messages, 2 = full debug
def log(msg=-1, d=0, condition=True):
    if DEBUG >= d and condition:
        if msg == -1:
            print("")
            return
        header = "[]"
        if d == 0:
            header = "[INFO]"
        elif d == 1:
            header = "[STATUS]"
        elif d == 2:
            header = "[DEBUG]"
        print(header + " " + msg)
    
def make_predictable_blob(f, n_bytes=1024):
    """Make a big predicatble store blob.

    Args:
        f: A file object to write to.
        n_bytes: Size in bytes of the target.
    """
    mebibyte = MiB
    for index in xrange(n_bytes):
        if index % mebibyte == 0 and index > 0:
            print "wrote mebibyte {}".format(index / mebibyte)
        index_hash = hashlib.sha256(str(index)).hexdigest()
        f.write(index_hash[0])

def predict_blob_value(index):
    """Predict the predictable blob value an the specified index."""
    index_hash = hashlib.sha256(str(index)).hexdigest()
    return index_hash[0]

if __name__ == "__main__":
    args = docopt(__doc__)
    
    filepath = args["--file"]
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

    DEBUG = 2 if verbose else 0
    with open(filepath, "wb") as f:
        make_random_blob(f, n_bytes=n_bytes, rservice=rservice)
