# Returns the relevant portion of the pad
def read_decrypt_pad(sender_uid, decrypt_index, clen):
    uid = me()
    metadataFile = get_metadatafile_name(uid, sender_uid)
    metadata = read_metadata(metadataFile)
    assert decrypt_index >= 0 and decrypt_index < metadata["n_bytes"]

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        pad = store.read()
        d = metadata["direction"]
        endIndex = decrypt_index + d * clen
        assert endIndex >= 0 and endIndex < metadata["n_bytes"]

        with open(metadataFile, "w") as mfile:
            updates = {"decrypt_indexes":
                       "{}{}-{},".format(metadata["decrypt_indexes"],
                                         decrypt_index,
                                         endIndex)}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))

        return pad[decrypt_index:endIndex:d]

# Returns (pad, index) 
def read_encrypt_pad(recipient_uid, mlen):
    uid = me()
    metadataFile = get_metadatafile_name(uid, recipient_uid)
    metadata = read_metadata(metadataFile)

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        pad = store.read()
        e = metadata["encrypt_index"]
        d = metadata["direction"]

        with open(metadataFile, "w") as mfile:
            updates = {"encrypt_index": e+d*mlen}
            metadata = update_metadata(metadata, updates)
            mfile.write(json.dumps(metadata))
        assert e+d*mlen >= 0 and e+d*mlen < metadata["n_bytes"]
        return (pad[e:e + d*mlen:d], e)

# True if the decrypt index requested has been used before
#  to decrypt 
def decrypt_index_used(sender_uid, decrypt_index):
    uid = me()
    metadataFile = get_metadatafile_name(uid, sender_uid)
    metadata = read_metadata(metadataFile)

    # Of the form "1-10,10-15,15-22,"
    indexes_used = metadata["decrypt_indexes"].split(",")
    return str(decrypt_index) in [s.split("-")[0] for s in indexes_used]

# True if this decrypt index requested has skipped over
#  a portion of the pad
def decrypt_index_skipped(sender_uid, decrypt_index, history=10):
    uid = me()
    metadataFile = get_metadatafile_name(uid, sender_uid)
    metadata = read_metadata(metadataFile)
    
    indexes_used = metadata["decrypt_indexes"].split(",")[-history:]
    return not any(map(lambda s: s.split("-")[1] == str(decrypt_index),
                       indexes_used))
