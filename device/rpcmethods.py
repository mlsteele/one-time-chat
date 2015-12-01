import crypto
import read
import os
import json
import base64
import traceback

"""
All methods that are RPCs should go here.
"""

ALLOW_LIST = [
    "package",
    "unpackage",
    "whoami",
    "test_prompt",
    "teapot",
]

# Confirm controller handle.
csc = None

def package(src_uid, dst_uid, message):
    """ Encrypt a message from from_uid to to_uid.
    Message is plaintext.
    Package it up with the index and MAC so the recipient can decode it.
    """
    # TODO verify bit release with user
    message = message.encode("utf-8")
    (p_text, index) = read.read_encrypt_pad(src_uid, dst_uid, len(message))
    (p_body, _)     = read.read_encrypt_pad(src_uid, dst_uid, len(message) + crypto.TAG_LENGTH)

    print "package    index:{}    message:{}    p_body:{}".format(
        index, base64.b64encode(message[:4]), base64.b64encode(p_body[:4]))

    try:
        package = crypto.package(index, message, p_text, p_body)
        # Base64 encode the package for transport.
        package_b64 = base64.b64encode(package)
        return {
            "success": True,
            "package": package_b64,
        }
    except crypto.CryptoError:
        traceback.print_exc()
        return {
            "success": False,
            "error": "Encryption failed.",
        }

def unpackage(src_uid, dst_uid, package_b64):
    # TODO verify bit release with user

    # b64 decode the package for decryption.
    package = base64.b64decode(package_b64)

    try:
        pre = crypto.pre_unpackage(package)
    except crypto.CryptoError:
        traceback.print_exc()
        return {
            "success" : False,
            "error": "Decryption failed.",
        }

    message_length = pre["message_length"]
    body_length = pre["body_length"]
    p_text_index = pre["p_text_index"]
    p_body_index = pre["p_body_index"]

    p_text = read.read_decrypt_pad(src_uid, dst_uid,
                                   p_text_index, message_length)
    p_body = read.read_decrypt_pad(src_uid, dst_uid,
                                   p_body_index, body_length)

    print "unpackage    index:{}    package:{}    p_body:{}".format(
        p_text_index, base64.b64encode(package[:4]), base64.b64encode(p_body[:4]))

    try:
        message = crypto.unpackage(package, p_text, p_body)  
        return {
            "success" : True,
            "message" : message,
        }
    except crypto.CryptoError:
        traceback.print_exc()
        return {
            "success" : False,
            "error": "Decryption failed.",
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

def test_prompt():
    print "test prompt requested", csc
    return csc.yn_prompt("[Fake] Release 2000\nbits of pad?")

def teapot():
    return "Error 418: I'm a teapot"
