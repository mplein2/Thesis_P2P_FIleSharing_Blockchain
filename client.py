import json
import os
import socket

from requests import get


class Client:

    def __init__(self):
        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']
        self.hostname = socket.gethostname()
        self.publicIP = "1.1.1.1"
        #self.publicIP = get('https://api.ipify.org').text
        self.localIP = socket.gethostbyname(self.hostname)
        try:
            file = open(self.DIR_PATH_CLIENT + "config.json")
            json_load_group = json.load(file)
            file.close()
            print(json_load_group)
            self.port = json_load_group["ClientPort"]
            self.gui_port = json_load_group["GUIPort"]
        except:
            print("passed")

    def print(self):
        print("Your Computer Name is:" + self.hostname)
        print("Your Local IP Address is:" + self.localIP)
        print("Your Public IP Address is:" + self.publicIP)

    def save(self):
        # Create JSON file
        JSONFileName = "config.json"
        jsonFile = open(self.DIR_PATH_CLIENT + "\\" + JSONFileName, "w")
        jsonFile.write(self.toJSON())
        jsonFile.close()
    def toJSON(self):
        ConfigFile = {"GUIPort": self.gui_port, "ClientPort": self.port}
        return json.dumps(ConfigFile)
