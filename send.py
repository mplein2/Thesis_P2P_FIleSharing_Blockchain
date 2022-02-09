import socket
import sys

HOST = '127.0.0.1'
PORT = 6700
if __name__ == "__main__":
    # Create socket for server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    # Let's send data through UDP protocol
    send_data = "Test1"
    s.sendto(send_data.encode('utf-8'), (HOST, PORT))
    print("\n\n 1. Client Sent : ", send_data, "\n\n")
    s.close()
