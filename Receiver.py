import socket
from socket import *
from types import SimpleNamespace


def receiver():
    # UDP_IP = client.localIP
    UDP_IP = '0.0.0.0'
    # UDP_PORT = client.port
    UDP_PORT = 6700
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        print("Listening on ", UDP_IP, ":", UDP_PORT)
        data, addr = sock.recvfrom(65507)  #max
        print(data)


def sendRequest(address, port, request):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    print("Sending")
    clientSocket.sendto(request, (address, port))