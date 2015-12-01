import crypto
from crypto import CryptoError
import unittest

class TestCrypto(unittest.TestCase):
    def test_xor(sel):
        # TODO write
        pass

    def test_codec_index_identity(self):
        """Test that encoding and decoding an index works."""
        # TODO write this test

    def test_encode_index_bad(self):
        """Test that encode index detects bad input."""
        with self.assertRaises(CryptoError):
            crypto.encode_index(-1)
        with self.assertRaises(CryptoError):
            crypto.encode_index("foo")

    def test_decode_index_bad(self):
        """Test that encode index detects bad input."""
        with self.assertRaises(CryptoError):
            crypto.decode_index("asdf")
        with self.assertRaises(CryptoError):
            crypto.decode_index("1234567")


if __name__ == '__main__':
    unittest.main()
