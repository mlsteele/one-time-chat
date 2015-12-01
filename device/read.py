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
        return (pad[e:e + d*mlen:d], e)
