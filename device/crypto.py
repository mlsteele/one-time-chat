import hashlib

# INDEX_MAX = ?
# INDEX_ENCODE_LENGTH = ?

def package(index, message, p_text, p_body):
    """
    Secure a message with encryption and integrity protection.

    package := i || body
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
    assert isinstance(index, int)
    assert isinstance(message, str)
    assert isinstance(p_text, str)
    assert isinstance(p_body, str)

    # Assert various properties we know should be true.
    raise NotImplementedError("this is not done.")

    response = self.rpc_client.encrypt(target, message)
    cipher_text = response["cipher_text"]
    index_used = response["index_used"]

    tag = self.rpc_client.sign(index_used + ciphertext)

    integrity = self.rpc_client.encrypt(target, ciphertext + tag)

    message_body = integrity["cipher_text"]

    return self.send(target, index_used + message_body)

def unpackage(package, p_text, p_body):
    """ Extract the message and verify it's integrity """ 
    raise NotImplementedError("this is not done.")
    packet_sender = packet[u'sender_uid']
    packet_message = packet[u'contents']
    index = packet_message[:MAX_INDEX_LENGTH]
    packet_body = packet_message[MAX_INDEX_LENGTH:]
    
    plain_body = self.rpc_client.decrypt(packet_sender,
            packet_body,
            int(index)+len(packet_body)-TAG_LENGTH)
    ## the starting index of the body pad: index + length of cipher text
    ## length of cipher text = length of body - length of tag
    tag = plain_body[-64:]
    ciphertext = plain_body[:-64]
    isSafe = self.rpc_client.verfy(packet_sender,index+ciphertext,tag)
    if isSafe:
       message = self.rpc_client.encrypt(packet_sender,ciphertext,index)
def xor_string(a, b):
    if len(a) != len(b):
        raise ValueError("Messages must be the same length!")
    return a ^ b


def xor(charA, charB):
    return chr(ord(charA) ^ ord(charB))


def xorHelper((charA,charB)):
    return xor(charA, charB)


def encrypt(message, pad):
    return map(xorHelper, zip(message, pad))


def decrypt(cipher, pad):
    return map(xorHelper, zip(cipher, pad))


def pretty_print(liste):
    string = ''
    for i in liste:
        string += i
    print string
    return string

# For now let's just do
# i || p2 xor ((p1 xor m) || MAC(p1 xor m))
# j || pj xor (i || pi xor m || MAC(i || pi xor m))


def MAC(m, key=-1):
    h = hashlib.sha256()
    h.update(m)
    return h.digest()


def hash(message):
    return hashlib.sha512(message).hexdigest()
