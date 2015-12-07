import json

class JsonStore(object):
    """
    Store json in a file.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}

    def read(self):
        try:
            with open(self.filepath, "r") as f:
                self.data = json.load(f)
        except (IOError, ValueError):
            self.data = {}

    def write(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f,
                      sort_keys=True,
                      indent=4,
                      separators=(",", ": "))
