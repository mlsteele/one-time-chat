import crypto
from crypto import CryptoError
import unittest

class TestCrypto(unittest.TestCase):
    def test_xor(self):
        self.assertEqual("\x00", crypto.xor("\x00", "\x00"))
        self.assertEqual("\x01", crypto.xor("\x00", "\x01"))
        self.assertEqual("\x00", crypto.xor("\x01", "\x01"))
        self.assertEqual("\x04\n\x05", crypto.xor("\x0f\x00\x00", "\x0b\n\x05"))

    def test_package_identity(self):
        index = 0
        message = "Test that pad being 0 is identity"
        p_text = chr(0)*len(message)
        p_body = chr(0)*(len(message)+ crypto.TAG_LENGTH)
        p_tag_key = chr(0) * crypto.TAG_KEY_LENGTH
        package = crypto.package(index, message, p_text, p_body, p_tag_key)
        # Should be index | message | HMAC(key, index | message)
        correctPackage = 6*chr(0)+message+(crypto.hmac_sha256(p_tag_key, 6*chr(0)+message))
        self.assertEqual(package, correctPackage)
    
    def test_package_reflexive(self):
        message = "Test that packaged and unpackaging returns the same message"
        index = 0
        p_text =  "otuhixnuheotuheouaoecgudoaeuteoahduao',.peaecd'983d uaoeuhu" #pseudo random typing
        p_body = ",'cd.ucr,'.gud.,9'ud249 l3uf19842gfpd4gdu r9'7i3pkur84gciudr.g,fi r138uf927 i'e7pduxanw;jk8"
        p_tag_key = "N\xbb\xcf\xb0jT\x81\x12X2.\xe5zMi\xee"

        self.assertEquals(len(p_body), len(p_text)+crypto.TAG_LENGTH)
        package = crypto.package(index, message, p_text, p_body, p_tag_key)
        unpackage = crypto.unpackage(package, p_text, p_body, p_tag_key)
        self.assertEquals(unpackage, message)

    def test_codec_index_identity(self):
        """Test that encoding and decoding an index works."""
        for i in range(200):
            index = i * 100000
            encoded = crypto.encode_index(index)
            self.assertEqual(6, len(encoded))
            self.assertEqual(crypto.INDEX_ENCODE_LENGTH, len(encoded))
            decoded = crypto.decode_index(encoded)
            self.assertEqual(index, decoded)

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
        with self.assertRaises(CryptoError):
            crypto.decode_index(crypto.encode_index(crypto.INDEX_MAX+1))


if __name__ == '__main__':
    unittest.main()
