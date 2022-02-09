from asyncio import sleep
import time
import socket
import sys

HOST = '127.0.0.1'
PORT = 6700


def receiver():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (HOST, PORT)
    s.bind(server_address)
    while True:
        print("####### Receiver Online #######")
        data, address = s.recvfrom(4096)
        print("\n\n 2. Server received: ", data.decode('utf-8'),"from :",address, "\n\n")
