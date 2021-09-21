import json
import os
import socket


class Client:

    def __init__(self):
        self.DIR_PATH_CLIENT = '%s\\TorrentApp\\' % os.environ['APPDATA']
        self.hostname = socket.gethostname()
        self.publicIP = "1.1.1.1"
        # self.publicIP = get('https://api.ipify.org').text
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
        json_file_name = "config.json"
        json_file = open(self.DIR_PATH_CLIENT + "\\" + json_file_name, "w")
        json_file.write(self.toJSON())
        json_file.close()

    def toJSON(self):
        config_file = {"GUIPort": self.gui_port, "ClientPort": self.port}
        return json.dumps(config_file)
