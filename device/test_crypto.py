import crypto
from crypto import CryptoError
import unittest

class TestCrypto(unittest.TestCase):
    def test_xor(self):
        # TODO write
        pass
    def test_package_identity(self):
        index = 0
        message = "Test that pad being 0 is identity"
        p_text = chr(0)*len(message)
        p_body = chr(0)*(len(message)+ crypto.TAG_LENGTH)
        package = crypto.package(index, message, p_text, p_body)
        # Should be index | message | Sha(index | message)
        correctPackage = chr(0)+message+(crypto.sha(chr(0)+message))
        self.assertEqual(package, correctPackage)
        
    def test_codec_index_identity(self):
        """Test that encoding and decoding an index works."""
        # TODO write this test
        for index in range(20):
            assert crypto.decode_index(crypto.encode_index(index)) == index

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
