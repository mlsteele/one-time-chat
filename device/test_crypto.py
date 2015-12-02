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
        correctPackage = 6*chr(0)+message+(crypto.sha(6*chr(0)+message))
        self.assertEqual(package, correctPackage)
    
    def test_package_reflexive(self):
        message = "Test that packaged and unpackaging returns the same message"
        index = 0
        p_text =  "otuhixnuheotuheouaoecgudoaeuteoahduao',.peaecd'983d uaoeuhu" #pseudo random typing
        p_body = ",'cd.ucr,'.gud.,9'ud249 l3uf19842gfpd4gdu r9'7i3pkur84gciudr.g,fi r138uf927 i'elaui '/u.,'u,.uu 872 pp9237pi9247pduxanw;jk8"
        self.assertEquals(len(p_body), len(p_text)+crypto.TAG_LENGTH)
        package = crypto.package(index, message, p_text, p_body)
        unpackage = crypto.unpackage(package, p_text, p_body)
        self.assertEquals(unpackage, message)

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
