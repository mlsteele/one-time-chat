class Storage(object):
    """Interface to a single file as an addressable byte store."""

    def __init__(self, filepath):
        self._filepath = filepath

    def get(self, start_index, n_bytes):
        """Get bytes from the store.

        Args:
            start_index: Index of the first byte to get.
            stop_index: Number of bytes to get.
        Returns:
            String of length n_bytes.
        """
        if not (start_index >= 0):
            raise ValueError("Invalid start_index {}".format(start_index))
        if not (n_bytes > 0):
            raise ValueError("n_bytes must be >0 ({})".format(n_bytes))

        with open(self._filepath, "rb") as f:
            f.seek(start_index)
            res = f.read(n_bytes)

        if not (len(res) == n_bytes):
            raise ValueError("Cannot read past end of storage.")

        return res
