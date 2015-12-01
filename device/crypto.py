import hashlib

# TODO  FIX -- put all of this on device, cal it packet/package or something
#  because it just makes more sense to do this all on device instead of
#  sending shit back and forth 38 times. Also asking the person multiple
#  times for confirmation is annoying


def package(self, target, message):
    """ Wrapper around send that encrypts the message before sending
        mesage that needs to be sent is along the form :
        ciphertext = encrypt(message, pad)
        index_used || encrypt ( ciphertext || MAC (index_used || ciphertext) )
            """
    response = self.rpc_client.encrypt(target, message)
    cipher_text = response["cipher_text"]
    index_used = response["index_used"]

    tag = self.rpc_client.sign(index_used + ciphertext)

    integrity = self.rpc_client.encrypt(target, ciphertext + tag)

    message_body = integrity["cipher_text"]

    return self.send(target, index_used + message_body)


def xor_string(a, b):
    if len(a) != len(b):
        raise ValueError("Messages must be the same length!")
    return a ^ b


def xor(charA, charB):
    return chr(ord(charA) ^ ord(charB))


def xorHelper(xxx_todo_changeme):
    (charA, charB) = xxx_todo_changeme
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
