import json
import os
import socket
from requests import get


class Client:
    def __init__(self):
        # TODO REFACTOR AND DOCUMENT THIS
        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']
        self.hostname = socket.gethostname()
        self.localIP = socket.gethostbyname(self.hostname)
        # Try to get public Ip from "ipify" API
        try:
            self.publicIP = get('https://api.ipify.org').text
        except:
            print("Couldn't Get Public IP")
        try:
            file = open(self.DIR_PATH_CLIENT + "config.json")
            json_load_group = json.load(file)
            file.close()
            print(json_load_group)
            self.port = json_load_group["ClientPort"]
            self.gui_port = json_load_group["GUIPort"]
            print("Config Loaded")
        except:
            print('Config Not Found')
            self.port = 6969
            self.gui_port = 6700
            self.save()
            print('New Config Generated')

    #
    def print(self):
        print("Your Computer Name is:" + self.hostname)
        print("Your Local IP Address is:" + self.localIP)
        print("Your Public IP Address is:" + self.publicIP)

    # Save Client Preferences and Settings to %appdata%
    def save(self):
        json_file_name = "config.json"
        json_file = open(self.DIR_PATH_CLIENT + "\\" + json_file_name, "w")
        json_file.write(self.toJSON())
        json_file.close()

    # Converts self to json strings
    def toJSON(self):
        config_file = {"GUIPort": self.gui_port, "ClientPort": self.port}
        return json.dumps(config_file)
