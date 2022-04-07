import base64
import zlib


def compress(text):
    return base64.b64encode(zlib.compress(text.encode()))


def decompress(text):
    return zlib.decompress(base64.b64decode(text)).decode()

if __name__ == "__main__":
    print(decompress("eJyrVspLzE1VslJQCkktLjFU0lFQKsnMBTITcwuAooZmJiYGZkZGFoZ6lmbmJkYmZkAFBampRcVAyWglCyM9QwMjPVNzPUNTc6XYWgBS0RRG"))
    print(len('{"name": "Test1", "timestamp": 1644062281.9674246, "peers": ["82.102.57.157"]["82.102.57.157"]mp": 1644062281.9674246, "peers":mp": 1644062281.9674246, "peers":'))
    print(len('eJyrVspLzE1VslJQCkktLjFU0lFQKsnMBTITcwuAooZmJiYGZkZGFoZ6lmbmJkYmZkAFBampRcVAyWglCyM9QwMjPVNzPUNTc6XYWgBS0RRG'))
    pass