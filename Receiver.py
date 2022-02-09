from asyncio import sleep
import time
import socket
import sys
import socket
import binascii
import socket
import struct


def receiver():
    port = 6700
    # Create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set some options to make it multicast-friendly
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 32)
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 2)
    s.bind(('', port))

    # Set some more multicast options
    intf = socket.gethostbyname(socket.gethostname())
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
    while True:
        print("Working")
        print(s.recvfrom(10000))
