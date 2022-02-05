from time import time
import os
from os import listdir
from os.path import isfile, join
import json


class Group:
    def __init__(self, name, private, admin, peers, time):
        self.name = name
        self.private = private
        self.admins = admin
        self.peers = peers
        self.timestamp = time

    def toJSON(self):
        return json.dumps(self.__dict__)


class GroupManager:

    def __init__(self):
        self.groups = []
        self.DIR_PATH_GROUPS = '%s\\TorrentApp\\Groups\\' % os.environ['APPDATA']
        # Load Groups
        self.loadGroups()
        print("GroupManager Initialized")

    def createGroup(self, name, private, admin):
        timeNow = time()
        newGroup = Group(name, private, [admin, ], [admin, ], timeNow)
        self.saveGroup(newGroup)
        self.groups.append(newGroup)
        return True

    def saveGroup(self, group: Group):
        # Create JSON file
        json_file_name = group.name + ".json"
        json_file = open(self.DIR_PATH_GROUPS + "\\" + json_file_name, "w")
        json_file.write(group.toJSON())
        json_file.close()

    def loadGroup(self, file):
        file = open(self.DIR_PATH_GROUPS + file)
        json_load_group = json.load(file)
        file.close()
        group = Group(json_load_group["name"], json_load_group["private"], json_load_group["admins"],
                      json_load_group["peers"], json_load_group["timestamp"])
        self.groups.append(group)


    def loadGroups(self):
        files = [f for f in listdir(self.DIR_PATH_GROUPS) if isfile(join(self.DIR_PATH_GROUPS, f))]
        for file in files:
            self.loadGroup(file)
