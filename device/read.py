from metadata import *
import logging

# Returns the relevant portion of the pad
def read_decrypt_pad(sid, uid, decrypt_index, clen):
    """ Read the specified bytes from the pad for decryption.

    Args:
        sid: User ID of the sender.
        uid: User ID of the recipient.
        decrypt_index: The index to start reading.
        clen: Amount of pad to retrieve in BYTES.
    Returns:
        Returns (pad, ind) where pad is a string and ind
         is the next decryption index to decrypt from.
    Throws:
        AssertionError if any index goes out of bounds
    """
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)
    assert decrypt_index >= 0 and decrypt_index < metadata["n_bytes"]
    d = metadata["direction"]
    if d == 1:
        assert decrypt_index >= metadata["split_index"]
    if d == -1:
        assert decrypt_index < metadata["split_index"]

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        endIndex = decrypt_index - d * clen #exclusive
        assert endIndex >= 0 and endIndex < metadata["n_bytes"]
        if d == 1:
            assert endIndex >= metadata["split_index"]
        if d == -1:
            assert endIndex < metadata["split_index"]

        with open(metadataFile, "w") as mfile:
            updates = {"decrypt_log":
                       "{}{}-{},".format(metadata["decrypt_log"],
                                         decrypt_index,
                                         endIndex),
                       "decrypt_max":
                       max(metadata["decrypt_max"], endIndex)
                       if metadata["direction"] == -1 else
                       min(metadata["decrypt_max"], endIndex)}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))
        
        leftInclusive = decrypt_index if d == -1 else endIndex+1
        rightInclusive = endIndex-1 if d == -1 else decrypt_index
        store.seek(leftInclusive)
        pad_out = store.read(rightInclusive - leftInclusive + 1)[::-d]
        return (pad_out, endIndex)

# Returns (pad, index) 
def read_encrypt_pad(uid, rid, mlen):
    """ Read the next mlen bytes from the pad for encryption.

    Advances the pointer in metadata.
    Will return new pad data each call.

    Args:
        uid: User ID of the sender.
        rid: User ID of the recipient.
        mlen: Amount of pad to retrieve in BYTES.
    Returns:
        Returns a tuple of (pad data, index)
        pad data is a string.
        index is the start index of the portion of the pad used.
    Throws:
        AssertionError if any index goes out of bounds
    """
    metadataFile = get_metadatafile_name(uid, rid)
    metadata = read_metadata(metadataFile)
    d = metadata["direction"]

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        e = metadata["encrypt_index"]
        endIndex = e + d * mlen
        assert endIndex >= 0 and endIndex < metadata["n_bytes"]
        if d == 1:
            assert endIndex < metadata["split_index"]
        if d == -1:
            assert endIndex >= metadata["split_index"]
        
        with open(metadataFile, "w") as mfile:
            updates = {"encrypt_index": e+d*mlen}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))

            leftInclusive = e if d == 1 else endIndex+1
            rightInclusive = endIndex-1 if d == 1 else e
            store.seek(leftInclusive)
            pad_data = store.read(rightInclusive - leftInclusive + 1)[::d]
            return (pad_data, e)

# True if the decrypt index requested has been used before
#  to decrypt 
def decrypt_index_used(sid, uid, decrypt_index):
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)

    # decrypt_log is of the form "1-10,10-15,15-22,"
    # indexes_used stores ["1-10","10-15","15-22"]
    indexes_used = metadata["decrypt_log"].split(",")[:-1]
    
    # If decrypt_index is within the range of any of
    #  the elements in the log, then the index has
    #  been used before
    d = metadata["direction"]
    temp = [s.split("-") for s in indexes_used]
    inclusive_ranges = [(int(r[0]), int(r[1]) + d) for r in temp]
    if d == 1:
        ans = any(map(lambda rt: rt[0] >= decrypt_index
                      and decrypt_index >= rt[1], inclusive_ranges))
    if d == -1:
        ans = any(map(lambda rt: rt[0] <= decrypt_index
                      and decrypt_index <= rt[1], inclusive_ranges))
    
    if ans:
        msg = ("Decryption index already used in message from "
             + "{} to {}".format(sid, uid)
             + "; intended index {}".format(decrypt_index))
        if d == 1:
            msg += ", increasing"
        elif d == -1:
            msg += ", decreasing"
        msg += ". Possible sign of replay or tampering."
        logging.warning(msg)

    return ans

# True if this decrypt index requested has skipped over
#  a portion of the pad
def decrypt_index_skipped(sid, uid, decrypt_index):
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)
    
    decrypt_optimum = metadata["decrypt_max"]
    d = metadata["direction"]
    if d == 1:
        ans = decrypt_index < decrypt_optimum
    if d == -1:
        ans = decrypt_index > decrypt_optimum
    
    if ans:
        msg = ("Decryption index skipped in message from "
             + "{} to {}".format(sid, uid)
             + "; intended index {}".format(decrypt_index)
             + "; last known index {}".format(decrypt_optimum))
        if d == 1:
            msg += ", increasing"
        elif d == -1:
            msg += ", decreasing"
        msg += ". Possible sign of a maliciously dropped packet."
        logging.warning(msg)
    
    return ans

# Returns UID of this device
def whoami(override_true_id=None):
    # Override just in case
    if override_true_id:
        return override_true_id

    files = os.listdir(".")
    metadata_file = filter(lambda f: f.find(METADATA_STEM) > -1, files)[0]
    uid = metadata_file[:metadata_file.index(".")]
    return uid
