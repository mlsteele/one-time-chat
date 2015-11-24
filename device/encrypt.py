import hashlib

def xor_string(a, b):
    if len(a) != len(b):
        raise ValueError("Messages must be the same length!")
    return a ^ b

# For now let's just do
# i || p2 xor ((p1 xor m) || MAC(p1 xor m))
# j || pj xor (i || pi xor m || MAC(i || pi xor m))
def MAC(m, key=-1):
    h = hashlib.sha256()
    h.update(m)
    return h.digest()

def encrypt(m, i, j, k=0):
    # use ord
    msg = str(i) + 
    
