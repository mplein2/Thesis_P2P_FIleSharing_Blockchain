from time import time
import os
from os import listdir
from os.path import isfile, join
import json
from typing import Type
import shutil


class Invite:
    def __init__(self, name, timestamp, peers):
        self.name = name
        self.timestamp = timestamp
        self.peers = peers

    def toJSON(self):
        return json.dumps(self.__dict__)


class Group:
    def __init__(self, name, private, admin, peers, timestamp):
        self.name = name
        self.private = private
        self.admins = admin
        self.peers = peers
        self.timestamp = timestamp

    def generateInvite(self):
        invite = Invite(self.name, self.timestamp, self.peers)
        return invite

    def toJSON(self):
        return json.dumps(self.__dict__)


class GroupManager:

    def __init__(self):
        self.groups = []
        self.DIR_PATH_GROUPS = '%s\\TorrentApp\\Groups\\' % os.environ['APPDATA']
        # Load Groups
        self.loadGroups()
        print("GroupManager Initialized")

    def addGroup(self, group):
        self.saveGroup(group)
        self.groups.append(group)

    def removeGroup(self, group):
        for x in self.groups:
            if x.name == group:
                print(self.groups.remove(x))
        print(self.groups)

    def getGroup(self, name):
        group: Group
        for group in self.groups:
            if group.name == name:
                return group

    def addPeerGroup(self, name, peer):
        group: Group
        for group in self.groups:
            if group.name == name:
                group.peers.append(peer)
                self.saveGroup(group)
                return

    def createGroup(self, name, private, admin):
        timeNow = time()
        newGroup = Group(name, private, [admin, ], [admin, ], timeNow)
        self.saveGroup(newGroup)
        self.groups.append(newGroup)
        return True

    def quitGroup(self, name):
        shutil.rmtree(self.DIR_PATH_GROUPS + name)
        self.removeGroup(name)
        return True

    def saveGroup(self, group: Group):
        # Create JSON file
        json_file_name = group.name + ".json"
        if not os.path.exists(self.DIR_PATH_GROUPS + group.name):
            # Create a new directory because it does not exist
            print("Gonna Create Group Folder")
            os.makedirs(self.DIR_PATH_GROUPS + group.name)
        json_file = open(self.DIR_PATH_GROUPS + group.name + '\\' + json_file_name, "w")
        json_file.write(group.toJSON())
        json_file.close()

    def loadGroup(self, file):
        fileName = file
        try:
            file = open(self.DIR_PATH_GROUPS + fileName + "\\" + fileName + ".json")
            json_load_group = json.load(file)
            file.close()
            group = Group(json_load_group["name"], json_load_group["private"], json_load_group["admins"],
                          json_load_group["peers"], json_load_group["timestamp"])
            self.groups.append(group)
        except:
            print("Error Opening Group file :", fileName)

    def loadGroups(self):
        try:
            groups = [group for group in listdir(self.DIR_PATH_GROUPS)]
            for group in groups:
                self.loadGroup(group)
        except:
            print("Group Folder Not Found")