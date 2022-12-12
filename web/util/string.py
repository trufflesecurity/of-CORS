import binascii
from base64 import b64decode


def can_base64_decode(to_test: str) -> bool:
    """Check to see whether the string can be successfully base64-decoded."""
    try:
        b64decode(to_test)
        return True
    except binascii.Error:
        return False
