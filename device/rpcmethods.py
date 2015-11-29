from utils import *
import encrypt
import os
import json

"""
All methods that are RPCs should go here.
"""

# Confirm controller handle.
csc = None

def encrypt(recipient_uid, message):
    """ Encrypts a message using a one time pad  
    recipient_uid is the id of the recipient. This impacts what pad will be used to encrypt
    message is the intended message to be encrypted
    returns a dictionary with keys cipher_text, and index_used
    """
    ## I imagine the pad to be read_from_device depends on the recipient_uid, the index, and the length of the pad
    return 0
    (pad,index_used) = read_encrypt_pad(recipient_uid,len(message)) 
    cipher_list = encrypt.encrypt(message,pad)
    cipher_text = encrypt.pretty_print(cipher_list)
    return {
            "status":"ok",
            "cipher_text":cipher_text,
            "index_used":index_used,
    }

def decrypt(sender_uid, cipher_text, index):
    """ Decrypts a message using a one time pad
    sender_uid is the id of the user who sent the cipher text.
    cipher_text is the contents of what they sent to be decrypt
    returns message decrypted
    """
    pad = read_decrypt_pad(sender_uid, index, len(cipher_text))
    message_list = encrypt.decrypt(message,pad)
    message = encrypt.pretty_print(message_list)
    return {
            "status":"ok",
            "message":message,
    }

def sign(recipient_uid,message):
    """ takes in a message and returns an authentication tag for that message
    recipient_uid is the id of the reciever
    message is the message that needs to be authenticated """

    pad = read_encrypt_pad(recipient_uid, len(message))
    message_hash = encrypt.hash(message)
    return message_hash

def verify(sender_uid,message,tag):


    return False

def read_encrypt_pad(recipient_uid, mlen):\
    # Hack way to get the metadata file without the UID
    files = os.listdir(".")
    metadataFile = filter(lambda f: f.find(get_metadatafile_name("")) > -1, files)[0]
    metadata = read_metadata(metadataFile)

    storeFile = metadata["store_filename"]
    with open(storeFile, "rb") as store:
        pad = store.read()
        e = metadata["encrypt_index"]
        d = metadata["direction"]
        if d in [1,-1]:
            with open(metadataFile, "w") as mfile:
                metadata["encrypt_index"] += mlen*d
                del metadata["checksum"]
                metadata["checksum"] = hash(frozenset(metadata.items()))
                mfile.write(json.dumps(metadata))
            return pad[e:e + d*mlen:d]
        else:
            raise ValueError("Metadata is corrupt; direction should be 1 or -1")

def echo(*args, **kwargs):
    """Echo back all arguments (for testing rpc mechanism)."""
    return {
        "received_args": args,
        "received_kwargs": kwargs
    }

def alwaysfail(*args, **kwargs):
    """Always return an error (for testing rpc mechanism)."""
    raise ValueError("this is normal.")

def add(a, b):
    """Add two numbers (for testing rpc mechanism)."""
    return a + b

def test_prompt():
    print "test prompt requested", csc
    return csc.yn_prompt("[Fake] Release 2000\nbits of pad?")
