import socket
import sys

addr = '82.102.57.157'
port = 6700
data = "yolo".encode()

if __name__ == "__main__":
    # Create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Make the socket multicast-aware, and set TTL.
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)  # Change TTL (=20) to suit
    # Send the data
    s.sendto(data, (addr, port))

