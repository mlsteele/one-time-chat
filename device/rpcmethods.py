import crypto
import read
import os
import json
import base64
import traceback
import logging
import metadata
from jsonstore import JsonStore

"""
All methods that are RPCs should go here.
"""

ALLOW_LIST = [
    "package",
    "unpackage",
    "get_next_ref",
    "save_next_ref",
]

# Confirm controller handle.
csc = None

def package(src_uid, dst_uid, message):
    """Encrypt a message from from_uid to to_uid.
    Message is plaintext.
    Package it up with the index and MAC so the recipient can decode it.
    """
    if src_uid == dst_uid:
        return {
            "success": False,
            "error": "Rejecting message to yourself."
        }

    message = message.encode("utf-8")
    if not csc.yn_prompt("Are you sure you want send a\n{} byte message?".format(len(message))):
        return {
            "success": False,
            "error": "User rejected pad read request.",
        }

    try:
        (p_text, index) = read.read_encrypt_pad(src_uid, dst_uid, len(message))
        (p_body, _)     = read.read_encrypt_pad(src_uid, dst_uid, len(message) + crypto.TAG_LENGTH)
        (p_tag_key, _)  = read.read_encrypt_pad(src_uid, dst_uid, crypto.TAG_KEY_LENGTH)
    except metadata.NoMetadataException:
        return {
            "success": False,
            "error": "Shared pad not found.",
        }
    except read.PadContainException:
        return {
            "success": False,
            "error": "Pad depleted.",
        }

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
    # b64 decode the package for decryption.
    package = base64.b64decode(package_b64)

    if not csc.yn_prompt("Are you sure you want\nto decrypt a message?"):
        return {
            "success": False,
            "error": "User rejected pad read request.",
        }
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

    try:
        skip_detected = read.decrypt_index_skipped(src_uid, dst_uid, p_text_index)
        reuse_detected = read.decrypt_index_used(src_uid, dst_uid, p_text_index)

        start_index = next_index = p_text_index
        (p_text, next_index) = read.read_decrypt_pad(src_uid, dst_uid,
                                                     next_index, message_length)
        (p_body, next_index) = read.read_decrypt_pad(src_uid, dst_uid,
                                                     next_index, message_length + crypto.TAG_LENGTH)
        (p_tag_key, _)       = read.read_decrypt_pad(src_uid, dst_uid,
                                                     next_index, crypto.TAG_KEY_LENGTH)
    except metadata.NoMetadataException:
        return {
            "success": False,
            "error": "Shared pad not found.",
        }

    try:
        message = crypto.unpackage(package, p_text, p_body, p_tag_key, verbose=True)
        return {
            "success": True,
            "message": message,
            "skip_detected": skip_detected,
            "reuse_detected": reuse_detected,
        }
    except crypto.IntegrityError:
        traceback.print_exc()
        logging.error("Integrity error in message from {} to {} with index {}".format(
            src_uid, dst_uid, start_index))
        return {
            "success": False,
            "error":"Decryption failed.", # Don't tell client specifics.
        }
    except crypto.CryptoError:
        traceback.print_exc()
        return {
            "success": False,
            "error":"Decryption failed.",
        }

def get_next_ref(uid, server_address):
    """Get the nextref setting for a (user, server) pair.
    Look up in the local table. Default to 0.
    """
    store = JsonStore("nextref.json")
    store.read()
    return store.data.get(uid, {}).get(server_address, None)

def save_next_ref(uid, server_address, nextref):
    """Save the nextref setting for a (user, server) pair."""
    store = JsonStore("nextref.json")
    store.read()
    uid_entry = store.data.get(uid, {})
    uid_entry[server_address] = nextref
    store.data[uid] = uid_entry
    store.write()

# Returns UID of this device
def whoami(true_id=None):
    return read.whoami(true_id)

def test_prompt():
    print "test prompt requested", csc
    return csc.yn_prompt("[Fake] Release 2000\nbits of pad?")

def teapot():
    return "Error 418: I'm a teapot"
