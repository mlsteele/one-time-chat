import hashlib

def xor_string(a, b):
    if len(a) != len(b):
        raise ValueError("Messages must be the same length!")
    return a ^ b

def xor(charA, charB):
    return chr(ord(charA) ^ ord(charB))
def xorHelper((charA, charB)):
    return xor(charA, charB)
def encrypt(message, pad):
    return map(xorHelper,zip(message,pad))
def decrypt(cipher, pad):
    return map(xorHelper,zip(cipher,pad))

def pretty_print(liste):
    string = ''
    for i in liste:
        string +=i
    print string
    return string

# For now let's just do
# i || p2 xor ((p1 xor m) || MAC(p1 xor m))
# j || pj xor (i || pi xor m || MAC(i || pi xor m))
def MAC(m, key=-1):
    h = hashlib.sha256()
    h.update(m)
    return h.digest()

