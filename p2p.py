import socket
import threading
import time

def receiver():
    while True:
        # Get UDP From here.
        UDP_PORT = 6700
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind(("", UDP_PORT))
        y = threading.Thread(target=keepAlive,args=[sock])
        y.start()
        while True:
            print("Trying to receive")
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("Received:", data, " from", addr)


# peers should be a list
def keepAlive(sock):
    peers = ["82.102.57.157", ]
    while True:
        time.sleep(5)
        for peer in peers:
            print("Sending KeepAlive to ",peer,":",6700)
            sock.sendto(b'KeepAlive', (peer,6700))
        sock.sendto(b'Data', (peer,6700))


if __name__ == "__main__":
    x = threading.Thread(target=receiver)
    x.start()


