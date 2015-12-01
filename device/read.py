from metadata import *

# Returns the relevant portion of the pad
def read_decrypt_pad(sid, uid, decrypt_index, clen):
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)
    assert decrypt_index >= 0 and decrypt_index < metadata["n_bytes"]

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        pad = store.read()
        d = metadata["direction"]
        endIndex = decrypt_index - d * clen
        assert endIndex >= 0 and endIndex < metadata["n_bytes"]

        print("Decrypt index skipped: {}\nDecrypt index used: {}\n".
              format(decrypt_index_skipped(sid, uid, decrypt_index),
                     decrypt_index_used(sid, uid, decrypt_index)))
        with open(metadataFile, "w") as mfile:
            updates = {"decrypt_log":
                       "{}{}-{},".format(metadata["decrypt_log"],
                                         decrypt_index,
                                         endIndex),
                       "decrypt_max":
                       max(metadata["decrypt_max"], endIndex-1)
                       if metadata["direction"] == -1 else
                       min(metadata["decrypt_max"], endIndex+1)}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))

        return pad[decrypt_index:endIndex:-d]

# Returns (pad, index) 
def read_encrypt_pad(uid, rid, mlen):
    metadataFile = get_metadatafile_name(uid, rid)
    metadata = read_metadata(metadataFile)

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        pad = store.read()
        e = metadata["encrypt_index"]
        d = metadata["direction"]
        endIndex = e + d * mlen
        assert endIndex >= 0 and endIndex < metadata["n_bytes"]

        with open(metadataFile, "w") as mfile:
            updates = {"encrypt_index": e+d*mlen}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))
        return (pad[e:endIndex:d], e)

# True if the decrypt index requested has been used before
#  to decrypt 
def decrypt_index_used(sid, uid, decrypt_index):
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)

    # Of the form "1-10,10-15,15-22,"
    indexes_used = metadata["decrypt_log"].split(",")[:-1]
    print "indexes_used in decrypt_index_used is:"
    print indexes_used
    return str(decrypt_index) in [s.split("-")[0] for s in indexes_used]

# True if this decrypt index requested has skipped over
#  a portion of the pad
def decrypt_index_skipped(sid, uid, decrypt_index, history=-1):
    metadataFile = get_metadatafile_name(uid, sid)
    metadata = read_metadata(metadataFile)
    
    history = history if history > 0 else 0
    indexes_used = metadata["decrypt_log"].split(",")[-history:-1]
    print "indexes_used[-history:] in skipped is:"
    print indexes_used
    if len(indexes_used) == 0:
        return False
    return not any(map(lambda s: s.split("-")[1] == str(decrypt_index),
                       indexes_used))

# Returns UID of this device
def whoami(override_true_id=None):
    # Override just in case
    if override_true_id:
        return override_true_id

    files = os.listdir(".")
    metadata_file = filter(lambda f: f.find(METADATA_STEM) > -1, files)[0]
    uid = metadata_file[:metadata_file.index(".")]
    return uid
