import socket
from socket import *
from types import SimpleNamespace


def receiver():
    # UDP_IP = client.localIP
    UDP_IP = '127.0.0.1'
    # UDP_PORT = client.port
    UDP_PORT = 6900
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        print("Listening on ", UDP_IP, ":", UDP_PORT)
        data, addr = sock.recvfrom(65507)  # Buffer suze in bytes


def sendRequest(address, port, request):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(request.toJSON().encode(), (address, port))
