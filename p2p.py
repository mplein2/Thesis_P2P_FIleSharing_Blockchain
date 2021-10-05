import socket
from socket import *
from types import SimpleNamespace
from fragment import *


def receiver(client):
    UDP_IP = client.localIP
    UDP_PORT = client.port
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    datasize = 0
    while True:
        print("Listening on ", UDP_IP, ":", UDP_PORT)
        data, addr = sock.recvfrom(65507)  # buffer size is 1024 bytes
        x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        print(x)
        try:
            f = open("Received_" + x.fileName, "rb+")
        except:
            f = open("Received_" + x.fileName, "wb")
        f.seek(x.fileFragment * x.fragmentSize, 0)
        print(x.fileFragment, x.fragmentSize, x.fragmentContent)
        print(f.tell())
        f.write(base64.b64decode(x.fragmentContent))
        f.close()


async def SendFiles(fileName, fileFragment, fragmentSize):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    addr = ("192.168.178.26", 6969)
    fragment = Fragment(fileName, fileFragment, fragmentSize)
    print(fragment.toJSON(), "\n")
    print("Sending File")
    clientSocket.sendto(fragment.toJSON().encode(), addr)
