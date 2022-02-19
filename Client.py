from requests import get
import os
from socket import *

class Client:
    def __init__(self):
        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']




        # TODO PEER TO PEER
        # # Try to get public Ip from "ipify" API
        # try:
        #     self.publicIP = get('https://api.ipify.org').text
        # except:
        #     print("Couldn't Get Public IP")

        #Because local use this as ip
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        self.publicIP = sock.getsockname()[0]
        sock.close()