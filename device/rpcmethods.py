from utils import *
import crypto
import read
import os
import json


"""
All methods that are RPCs should go here.
"""

# Confirm controller handle.
csc = None
TAG_LENGTH = 64 ### Constant length of SHA1 hash

def package(src_uid, dst_uid, message):
    """ Encrypt a message from from_uid to to_uid.
    Message is plaintext
    Package it up with the index and MAC so the recipient can decode it.
    """
    # TODO: actually encrypt.
    (p_cipher,index) = read.read_encrypt_pad(src_uid, dst_uid,len(message))
    (p_body,not_used) = read.read_encrypt_(src_uid,dst_uid,len(message)+TAG_LENGTH)
    package = crpyto.package(index,message,p_cipher,p_body)
    return {
        "success": True,
        "package": package # TODO encrypt instead please.
    }

def encrypt(recipient_uid, message):
    """ Encrypts a message using a one time pad  
    recipient_uid is the id of the recipient. This impacts what pad will be used to encrypt
    message is the intended message to be encrypted
    returns a dictionary with keys cipher_text, and index_used
    """
    ## I imagine the pad to be read_from_device depends on the recipient_uid, the index, and the length of the pad
    #TODO: index_used might buggy
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
    """ verifies that the message hashes to the tag value """
    return encrypt.hash(message)==tag

# Returns UID of this device
def me(true_id=None):
    if true_id: # Override for when multiple clients on one computer
        return true_id
    files = os.listdir(".")
    metadata_file = filter(lambda f: f.find(METADATA_STEM) > -1, files)[0]
    uid = metadata_file[:metadata_file.index(".")]
    return uid

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
