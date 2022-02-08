import base64
import zlib


def compress(text):
    return base64.b64encode(zlib.compress(text.encode()))


def decompress(text):
    return zlib.decompress(base64.b64decode(text)).decode()
