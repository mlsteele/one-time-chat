import crypto
import read
import os
import json
import base64

"""
All methods that are RPCs should go here.
"""

# TODO add explicit rpc allow list.

# Confirm controller handle.
csc = None

def package(src_uid, dst_uid, message):
    """ Encrypt a message from from_uid to to_uid.
    Message is plaintext.
    Package it up with the index and MAC so the recipient can decode it.
    """
    message = message.encode("utf-8")
    (p_text, index) = read.read_encrypt_pad(src_uid, dst_uid, len(message))
    (p_body, _)     = read.read_encrypt_pad(src_uid, dst_uid, len(message) + crypto.TAG_LENGTH)
    try:
        package = crypto.package(index, message, p_text, p_body)
        # Base64 encode the package for transport.
        package_b64 = base64.b64encode(package)
        return {
            "success": True,
            "package": package_b64,
        }
    except CryptoError:
        return {
                "success": False,
        }

def unpackage(src_uid, dst_uid, package_b64):
    # b64 decode the package for decryption.
    package = base64.b64decode(package_b64)
    message_length = len(package) - crypto.INDEX_ENCODE_LENGTH - crpto.TAG_LENGTH 
    body_length = len(package) - crypto.INDEX_ENCODE_LENGTH
    p_text = read.read_decrypt_pad(dst_uid, message_length)
    p_body = read.read_decrypt_pad(dst_uid, body_length)

    try:
        message = crypto.unpackage(package, p_text, p_body)  
        return {
                "success" : True,
                "message" : message
        }
    except CryptoError:
        return {
                "success" : False,
        }
def encrypt(recipient_uid, message):
    """ Encrypts a message using a one time pad  
    recipient_uid is the id of the recipient. This impacts what pad will be used to encrypt
    message is the intended message to be encrypted
    returns a dictionary with keys cipher_text, and index_used
    """
    ## I imagine the pad to be read_from_device depends on the recipient_uid, the index, and the length of the pad
    #TODO: index_used might buggy
    (pad,index_used) = read_encrypt_pad(recipient_uid, len(message)) 
    cipher_list = encrypt.encrypt(message, pad)
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
def whoami(true_id=None):
    return read.whoami(true_id)

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

def teapot():
    return "Error 418: I'm a teapot"
