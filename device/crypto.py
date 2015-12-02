import hashlib
import struct

# Length of encoded index in bytes.
INDEX_ENCODE_LENGTH = 6
# Maximum supported pad index.
INDEX_MAX = (2**(INDEX_ENCODE_LENGTH * 8)) - 1
# Length of tag in bytes.
TAG_LENGTH = 64

class CryptoError(Exception):
    pass


def package(index, message, p_text, p_body):
    """
    Secure a message with encryption and integrity protection.

    package := i || (p_body XOR body)
    body := ciphertext || tag
    tag := SHA(i || ciphertext)
    ciphertext := p_text XOR message

    - '||' means concatenation.
    - i is a fixed-length encoding of the pad index.
    - SHA refers to a SHA256 hash.

    Args:
        index: Index into the pad used. (int)
        message: Plaintext message to encrypt. (string)
        p_cipher: Bytes to use for XORing with message. (string)
        p_body: Bytes to use for XORing with message || tag. (string)

    Returns:
        The secured message, ready for sending. (string)
    """
    # Assert parameter types.
    ##TODO: better assert check error messages
    cassert(isinstance(index, int), "Index not int")
    cassert(isinstance(message, str))
    cassert(isinstance(p_text, str))
    cassert(isinstance(p_body, str))

    # Assert various properties we know should be true.
    cassert(0 <= index <= INDEX_MAX)
    cassert(len(p_text) == len(message))
    cassert(len(p_body) == len(message) + TAG_LENGTH)

    # Encrypt the plaintext.
    ciphertext = encrypt(message, p_text)

    # Encode the index.
    i_enc = encode_index(index)
    cassert(len(i_enc) == INDEX_ENCODE_LENGTH)

    # Create the integrity tag.
    tag = sha(i_enc + ciphertext)
    cassert(len(tag) == TAG_LENGTH)

    body = ciphertext + tag

    return i_enc + encrypt(body, p_body)


def unpackage(package, p_text, p_body):
    """ Extract the message and verify it's integrity """ 
    
    # extract package contents
    index = package[:INDEX_ENCODE_LENGTH]
    encrypted_body = package[INDEX_ENCODE_LENGTH:]
    plain_body = decrypt(encrypted_body,p_body)
    ## the starting index of the body pad: index + length of cipher text
    ## length of cipher text = length of body - length of tag
    tag = plain_body[-1*TAG_LENGTH:]
    ciphertext = plain_body[:-1*TAG_LENGTH]

    # integrity check
    if sha(index + ciphertext) == tag:
        message = decrypt(ciphertext,p_text)
        return message
    else:
        raise CryptoError("Integrity Error") 

def pre_unpackage(package):
    """Extract what information is necessary to fetch before unpackaging.

    Returns:
    {
        p_text_index
        p_body_index
    }
    Raises:
        CryptoError on failure.
    """
    message_length = len(package) - INDEX_ENCODE_LENGTH - TAG_LENGTH 
    cassert(message_length > 0)
    body_length = message_length + TAG_LENGTH
    p_text_index = decode_index(package[:INDEX_ENCODE_LENGTH])
    p_body_index = p_text_index + message_length
    return {
        "message_length": message_length,
        "body_length": body_length,
        "p_text_index": p_text_index,
        "p_body_index": p_body_index,
    }

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


def sha(stuff):
    return hashlib.sha512(stuff).digest()

def cassert(condition, error=None):
    """Assert and throw a CryptoError if it fails."""
    if not condition:
        raise CryptoError(error)
