from requests import get
import os


class Client:
    def __init__(self):
        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']

        # Try to get public Ip from "ipify" API
        try:
            self.publicIP = get('https://api.ipify.org').text
        except:
            print("Couldn't Get Public IP")
