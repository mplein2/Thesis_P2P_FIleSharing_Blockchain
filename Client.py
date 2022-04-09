from requests import get
import os
from socket import *
import copy
import json

class Client:
    def __init__(self):
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

        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']
        self.DIR_PATH_CONFIG = self.DIR_PATH_CLIENT+"config.json"
        if not os.path.exists(self.DIR_PATH_CONFIG):
            #Create The Config File
            f = open(self.DIR_PATH_CONFIG, "x")
            f.close()
            self.DIR_PATH_DOWNLOADS = "C:\Downloads"
            self.DOWNLOAD_PEER_CONNECTIONS = 5
            self.saveConfig()
        else:
            with open(self.DIR_PATH_CONFIG, 'r') as f:
                data = f.read()
                cfgObj = json.loads(data)
                self.DIR_PATH_DOWNLOADS = cfgObj["DIR_PATH_DOWNLOADS"]
                self.DOWNLOAD_PEER_CONNECTIONS = cfgObj["DOWNLOAD_PEER_CONNECTIONS"]
        print("Client Initialized")

    def saveConfig(self):
        saveCpy = copy.copy(self)
        del saveCpy.DIR_PATH_CLIENT
        del saveCpy.DIR_PATH_CONFIG
        del saveCpy.publicIP
        saveCpyJSON = json.dumps(saveCpy.__dict__)
        with open(self.DIR_PATH_CONFIG, 'w') as f:
            f.write(saveCpyJSON)




