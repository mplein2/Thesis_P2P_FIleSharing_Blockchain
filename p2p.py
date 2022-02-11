from socket import socket, AF_INET, SOCK_DGRAM


def server():
    UDP_PORT = 56700
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    print(sock.getsockname())

    while True:
        print("Ready to receive")
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("Received", data, "from", addr)


def send():



if __name__ == "__main__":
    server()

if __name__ == "__main__":
    listen()

if __name__ == "__main__":
    listen()
