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
       entropy.

    Args:
       f: A file object to write to
       n_bytes: Size in bytes of the target
    """
    if not (rservice == "random" or rservice == "urandom"):
        raise ValueError("rservice argument needs to be either" +
                         "random or urandom")
    n_Kbytes = n_bytes / KiB
    n_leftoverbytes = n_bytes - (n_Kbytes * KiB)
    # Make sure the HRNG is running
    os.system("/etc/init.d/rng-tools start")
    log("Generating {} random bytes".format(n_bytes) +
        " with OS service '{}'".format(rservice), 0)

    t1 = time.time()
    
    for i in range(n_Kbytes):
        with open("/dev/" + rservice, "rb") as rand:
            # So there's usually around 3000 bits of entropy
            #  available (4096 at most). That's 512 bytes.
            #  I don't know why but 1024 bytes at a time seems
            #  to work the best.
            randobytes = repr(rand.read(KiB))
            f.write(randobytes)
            log("Wrote kilobyte # {}".format(i), 1)
            log("Wrote megabyte # {}".format(i/KiB), 0, (i+1)%n_Kbytes==0)
            

    t2 = time.time()
    log()
    log("Random number generation complete!")
    log(" - amount random data: {} bytes".format(n_bytes) +
        " ({} KiB)".format(n_bytes, 1.0*n_bytes / KiB))
    log(" - time elapsed: {} seconds".format(t2 - t1))
    log(" - throughput: {} KiB/s".format((1.0*n_bytes/KiB) / (t2 - t1)))

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
    filepath = "random.blob"
    with open(filepath, "wb") as f:
        make_random_blob(f, n_bytes=KiB, rservice="urandom")
