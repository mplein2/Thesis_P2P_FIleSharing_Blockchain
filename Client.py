from requests import get
import os
from socket import *
import copy
import json
import rsa


class Client:
    def __init__(self):
        # TODO PEER TO PEER
        # # Try to get public Ip from "ipify" API
        # try:
        #     self.publicIP = get('https://api.ipify.org').text
        # except:
        #     print("Couldn't Get Public IP")

        # Because local use this as ip
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        self.publicIP = sock.getsockname()[0]
        sock.close()

        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']
        self.DIR_PATH_CONFIG = self.DIR_PATH_CLIENT + "config.json"
        self.DIR_PATH_PRIVATE_KEY = self.DIR_PATH_CLIENT + "PRIVATEKEY.json"
        self.DIR_PATH_PUBLIC_KEY = self.DIR_PATH_CLIENT + "PUBLICKEY.json"
        if not os.path.exists(self.DIR_PATH_CONFIG):
            # Create The Config File
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

        # RSA Keys
        if not os.path.exists(self.DIR_PATH_PUBLIC_KEY):
            if not os.path.exists(self.DIR_PATH_PRIVATE_KEY):
                #Create new Keys
                self.publicKey, self.privateKey = rsa.newkeys(512)
                #Create Key Files
                f = open(self.DIR_PATH_PRIVATE_KEY, "wb+")
                f.write(self.privateKey.save_pkcs1(format='PEM'))
                f.close()

                f = open(self.DIR_PATH_PUBLIC_KEY, "wb+")
                f.write(self.publicKey.save_pkcs1(format='PEM'))
                f.close()
                print("RSA Keys Created")
        else:
            f = open(self.DIR_PATH_PRIVATE_KEY, "rb")
            data = f.read()
            self.privateKey = rsa.PrivateKey.load_pkcs1(data)
            # print(self.privateKey)
            f.close()

            f = open(self.DIR_PATH_PUBLIC_KEY, "rb")
            data = f.read()
            self.publicKey = rsa.PublicKey.load_pkcs1(data)
            # print(self.publicKey)
            f.close()

            # print("RSA Keys Loaded")

        print("Client Initialized")

    def saveConfig(self):
        saveCpy = copy.copy(self)
        del saveCpy.DIR_PATH_CLIENT
        del saveCpy.DIR_PATH_CONFIG
        del saveCpy.DIR_PATH_PUBLIC_KEY
        del saveCpy.DIR_PATH_PRIVATE_KEY
        del saveCpy.publicIP
        if hasattr(self, 'publicKey'):
            del saveCpy.publicKey
        if hasattr(self, 'privateKey'):
            del saveCpy.privateKey
        saveCpyJSON = json.dumps(saveCpy.__dict__)
        with open(self.DIR_PATH_CONFIG, 'w') as f:
            f.write(saveCpyJSON)
            f.close()
