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
    """Encrypt a message from from_uid to to_uid.
    Message is plaintext.
    Package it up with the index and MAC so the recipient can decode it.
    """
    # TODO verify bit release with user
    message = message.encode("utf-8")
    (p_text, index) = read.read_encrypt_pad(src_uid, dst_uid, len(message))
    (p_body, _)     = read.read_encrypt_pad(src_uid, dst_uid, len(message) + crypto.TAG_LENGTH)
    (p_tag_key, _)  = read.read_encrypt_pad(src_uid, dst_uid, crypto.TAG_KEY_LENGTH)

    try:
        package = crypto.package(index, message, p_text, p_body, p_tag_key, verbose=True)
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
        pre = crypto.pre_unpackage(package, verbose=True)
    except crypto.CryptoError:
        traceback.print_exc()
        return {
            "success" : False,
            "error": "Decryption failed.",
        }

    message_length = pre["message_length"]
    p_text_index = pre["p_text_index"]

    index     = p_text_index
    p_text    = read.read_decrypt_pad(   src_uid, dst_uid, index, message_length)
    index     = read.decrypt_index_shift(src_uid, dst_uid, index, message_length)
    p_body    = read.read_decrypt_pad(   src_uid, dst_uid, index, message_length + crypto.TAG_LENGTH)
    index     = read.decrypt_index_shift(src_uid, dst_uid, index, message_length + crypto.TAG_LENGTH)
    p_tag_key = read.read_decrypt_pad(   src_uid, dst_uid, index, crypto.TAG_KEY_LENGTH)

    try:
        message = crypto.unpackage(package, p_text, p_body, p_tag_key, verbose=True)
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

# Returns UID of this device
def whoami(true_id=None):
    return read.whoami(true_id)

def test_prompt():
    print "test prompt requested", csc
    return csc.yn_prompt("[Fake] Release 2000\nbits of pad?")

def teapot():
    return "Error 418: I'm a teapot"
