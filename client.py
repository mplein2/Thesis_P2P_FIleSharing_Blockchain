import socket

from requests import get


class Client:

    def __init__(self):
        self.hostname = socket.gethostname()
        self.publicIP = "1.1.1.1"
        #self.publicIP = get('https://api.ipify.org').text
        self.localIP = socket.gethostbyname(self.hostname)
        self.port = 6969
        self.gui_port = 6700
        self.print()

    def print(self):
        print("Your Computer Name is:" + self.hostname)
        print("Your Local IP Address is:" + self.localIP)
        print("Your Public IP Address is:" + self.publicIP)
