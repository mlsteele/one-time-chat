import hashlib

def make_predictable_blob(f, n_bytes=1024):
    """Make a big predicatble store blob.

    Args:
        f: A file object to write to.
        n_bytes: Size in bytes of the target.
    """
    mebibyte = 1024 * 1024
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
    filepath = "predictable.blob"
    with open(filepath, "wb") as f:
        mebibyte = 1024 * 1024
        gibibyte = mebibyte * 1024
        make_predictable_blob(f, n_bytes=gibibyte)
 
