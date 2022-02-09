import socket


class ConnectionManager:
    def __init__(self):
        pass


def receiver():
    while True:
        # Get UDP From here.
        UDP_IP = "127.0.0.1"
        UDP_PORT = 6700
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("Received:", data, " from", addr)


# peers should be a list
def keepAlive(peers):
    peers = ["82.1.1.1", ]
    UDP_IP = "127.0.0.1"
    UDP_PORT = 6700
    while True:
        for peer in peers:
            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
            sock.bind((UDP_IP, UDP_PORT))
            sock.sendto(b'KeepAlive', peer)
    sock.sendto(b'Data', peer)


if __name__ == "__main__":
    keepAlive()
