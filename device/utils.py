import json

def get_storefile_name(uid):
    return "{}.random.store".format(uid)

def get_metadatafile_name(uid):
    return "{}.random.metadata".format(uid)

def read_metadata(filename):
    with open(filename, "r") as metadata:
        data = json.loads(metadata.read())
        assert len(data.items()) == data["n_eles"]
        data_check = dict(data)
        del data_check["checksum"]
        assert data["checksum"] == hash(frozenset(data_check.items()))
        assert data["uid"] != data["rid"]
        assert data["split_index"] >= 0 and data["split_index"] < data["n_bytes"]
        return data