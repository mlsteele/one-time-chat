import hashlib
import struct
import hmac
import base64

# Length of encoded index in bytes.
INDEX_ENCODE_LENGTH = 6
# Maximum supported pad index.
INDEX_MAX = (2**(INDEX_ENCODE_LENGTH * 8)) - 1
# Length of tag in bytes.
TAG_LENGTH = 32
# Length of the HMAC key in bytes.
TAG_KEY_LENGTH = 16

class CryptoError(Exception):
    pass


def package(index, message, p_text, p_body, p_tag_key, verbose=False):
    """
    Secure a message with encryption and integrity protection.

    package := i || (p_body XOR body)
    body := ciphertext || tag
    tag := HMAC(p_tag_key, i || ciphertext)
    ciphertext := p_text XOR message

    - '||' means concatenation.
    - i is a fixed-length encoding of the pad index.
    - HMAC is a sha256-based HMAC.

    Args:
        index: Index into the pad used. (int)
        message: Plaintext message to encrypt. (string)
        p_text: Pad bytes to use for hiding the message. (string)
        p_body: Pad bytes to use for hiding the message and tag. (string)
        p_tag_key: Pad bytes to use as HMAC key. (string)
        verbose: Whether to print parts to the console. (boolean)

    Returns:
        The secured message, ready for sending. (string)
    """
    # Assert parameter types.
    ##TODO: better assert check error messages
    cassert(isinstance(index, int), "Index not int")
    cassert(isinstance(message, str))
    cassert(isinstance(p_text, str))
    cassert(isinstance(p_body, str))
    cassert(isinstance(p_tag_key, str))

    # Assert various parameter properties.
    cassert(0 <= index <= INDEX_MAX)
    cassert(len(p_text) == len(message))
    cassert(len(p_body) == len(message) + TAG_LENGTH)
    cassert(len(p_tag_key) == TAG_KEY_LENGTH)

    # Encrypt the plaintext.
    ciphertext = encrypt(message, p_text)

    # Encode the index.
    i_enc = encode_index(index)
    cassert(len(i_enc) == INDEX_ENCODE_LENGTH)

    # Create the integrity tag.
    tag = hmac_sha256(key=p_tag_key, message=i_enc + ciphertext)
    cassert(len(tag) == TAG_LENGTH)

    body = ciphertext + tag

    full_package = i_enc + encrypt(body, p_body)

    # Size of result.
    cassert(len(full_package) == len(message) + INDEX_ENCODE_LENGTH + TAG_LENGTH)
    # Amount of total pad used.
    cassert(len(p_text) + len(p_body) + len(p_tag_key) == 2*len(message) + TAG_LENGTH + TAG_KEY_LENGTH)

    if verbose:
        print "package verbose:"
        print "  index", index
        print "  index_encoded", b64(i_enc)
        print "  p_text", b64(p_text)
        print "  p_body", b64(p_body)
        print "  p_tag_key", b64(p_tag_key)
        print "  message", message
        print "  ciphertext", b64(ciphertext)
        print "  tag", b64(tag)

    return full_package


def unpackage(package, p_text, p_body, p_tag_key, verbose=True):
    """Extract the message and verify its integrity.

    Args:
        package: Packaged message to decrypt. (string)
        p_text: Pad bytes used to hide the message. (string)
        p_body: Pad bytes used to hide the message and tag. (string)
        p_tag_key: Pad bytes to use as HMAC key. (string)
        verbose: Whether to print parts to the console. (boolean)

    Returns:
        The plaintext message (string).
    Raises:
        CryptoError: If there is an error or the integrity check fails.
    """
    # Assert parameter types.
    cassert(isinstance(package, str))
    cassert(isinstance(p_text, str))
    cassert(isinstance(p_body, str))
    cassert(isinstance(p_tag_key, str))

    # Assert parameter properties
    cassert(len(p_text) == len(package) - INDEX_ENCODE_LENGTH - TAG_LENGTH)
    cassert(len(p_body) == len(package) - INDEX_ENCODE_LENGTH)
    cassert(len(p_tag_key) == TAG_KEY_LENGTH)

    # Extract package contents
    i_enc = package[:INDEX_ENCODE_LENGTH]
    index = decode_index(i_enc)
    encrypted_body = package[INDEX_ENCODE_LENGTH:]

    # Decrypt body.
    plain_body = decrypt(encrypted_body, p_body)

    # The starting index of the body pad: index + length of cipher text
    # Length of cipher text = length of body - length of tag
    tag = plain_body[-TAG_LENGTH:]
    ciphertext = plain_body[:-TAG_LENGTH]

    # Compute the expected tag.
    expected_tag = hmac_sha256(key=p_tag_key, message=i_enc + ciphertext)

    if verbose:
        print "unpackage verbose:"
        print "  index", index
        print "  index_encoded", b64(i_enc)
        print "  p_text", b64(p_text)
        print "  p_body", b64(p_body)
        print "  p_tag_key", b64(p_tag_key)
        print "  ciphertext", b64(ciphertext)
        print "  tag", b64(tag)

    # Check the tag.
    if hmac.compare_digest(tag, expected_tag):
        message = decrypt(ciphertext, p_text)
        return message
    else:
        raise CryptoError("Integrity Error") 

def pre_unpackage(package, verbose=False):
    """Extract what information is necessary to fetch before unpackaging.

    Returns:
    {
        message_length: Expected length of the underlying message.
        p_text_index: Index of the text pad bytes.
    }
    Raises:
        CryptoError on failure.
    """
    message_length = len(package) - INDEX_ENCODE_LENGTH - TAG_LENGTH 
    cassert(message_length >= 0)
    p_text_index = decode_index(package[:INDEX_ENCODE_LENGTH])
    res = {
        "message_length": message_length,
        "p_text_index": p_text_index,
    }
    if verbose:
        print res
    return res

def encode_index(index_num):
    """
    Encode an index as a fixed length string.
    """
    cassert(0 <= index_num <= INDEX_MAX)
    cassert(INDEX_ENCODE_LENGTH < 8)
    try:
        eight_pack = struct.pack("<Q", index_num)
    except struct.error as ex:
        raise CryptoError(ex)
    cassert(len(eight_pack) == 8)
    return eight_pack[:INDEX_ENCODE_LENGTH]


def decode_index(index_str):
    """
    Decode an index encoded as a fixed length string.
    """
    cassert(isinstance(index_str, str), "Index not instance of String")
    cassert(len(index_str) == INDEX_ENCODE_LENGTH, "Not None")
    eight_pack = index_str + "\x00" + "\x00"
    try:
        return struct.unpack("<Q", eight_pack)[0]
    except struct.error as ex:
        raise CryptoError(ex)


def xor(charA, charB):
    return chr(ord(charA) ^ ord(charB))


def xorHelper((charA,charB)):
    return xor(charA, charB)


def encrypt(message, pad):
    return "".join(map(xorHelper, zip(message, pad)))


def decrypt(cipher, pad):
    return "".join(map(xorHelper, zip(cipher, pad)))


def hmac_sha256(key, message):
    cassert(isinstance(key, str))
    cassert(isinstance(message, str))
    return hmac.new(key, message, digestmod=hashlib.sha256).digest()


def cassert(condition, error=None):
    """Assert and throw a CryptoError if it fails."""
    if not condition:
        raise CryptoError(error)


def b64(string):
    return base64.b64encode(string)
