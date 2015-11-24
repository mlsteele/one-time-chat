"""
All methods that are RPCs should go here.
"""

def encrypt(recipient_uid, message):
    return {
        "status": "failed",
        "reason": "I don't know how to encrypt",
    }

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
