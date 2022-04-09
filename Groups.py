from time import time
import os
from os import listdir
from os.path import isfile, join
import json
from typing import Type
import shutil
import hashlib
from Bundles import Bundle
import copy


class Invite:
    def __init__(self,id, name, timestamp, peers):
        self.id = id
        self.name = name
        self.timestamp = timestamp
        self.peers = peers

    def toJSON(self):
        return json.dumps(self.__dict__)


class Group:
    def __init__(self, name, private, admin, peers, timestamp,id=None):
        self.name = name
        self.timestamp = timestamp
        self.private = private
        self.admins = admin
        self.peers = peers
        self.bundles = []
        if id is None:
            self.id = hashlib.sha256((name+str(timestamp)).encode('utf-8')).hexdigest()
        else:
            self.id=id

    def generateInvite(self):
        invite = Invite(self.id,self.name, self.timestamp, self.peers)
        return invite

    def toJSON(self):
        return json.dumps(self.__dict__)

    def getBundleWithId(self,bundleid):
            group: Bundle
            for bundle in self.bundles:
                print("trying to match",bundle.id)
                if bundle.id == bundleid:
                    return bundle
            #If Nothing Proked return in for loop return false for not having the bundle .
            return False




class GroupManager:

    def __init__(self):
        self.groups = []
        self.DIR_PATH_GROUPS = '%s\\TorrentApp\\Groups\\' % os.environ['APPDATA']
        if not os.path.exists(self.DIR_PATH_GROUPS):
            # Create a new directory because it does not exist
            print("Gonna Create Group Folder")
            os.makedirs(self.DIR_PATH_GROUPS)
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

    def getGroupWithName(self, name):
        group: Group
        for group in self.groups:
            if group.name == name:
                return group

    def getGroupWithId(self, id):
        group: Group
        for group in self.groups:
            if group.id == id:
                return group

    def addPeerGroup(self, name, peer):
        group: Group
        for group in self.groups:
            if group.name == name:
                if peer not in group.peers:
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
        saveCopy = copy.copy(group)
        del saveCopy.bundles
        json_file.write(saveCopy.toJSON())
        json_file.close()

    def loadGroup(self, groupName):
        try:
            file = open(self.DIR_PATH_GROUPS + groupName + "\\" + groupName + ".json")
            json_load_group = json.load(file)
            file.close()
            group = Group(json_load_group["name"], json_load_group["private"], json_load_group["admins"],
                          json_load_group["peers"], json_load_group["timestamp"],json_load_group["id"],)
        except:
            print("Error Opening Group file :", groupName)


        #Load Bundles of Each group.
        groupBundlePath = self.DIR_PATH_GROUPS + groupName + "\\" + "Bundles\\"
        #Make the folder if it dosent exist .
        if not os.path.exists(groupBundlePath):
            os.makedirs(groupBundlePath)
        else:
        #if exists search all the files
            bundles = [f for f in listdir(groupBundlePath) if isfile(join(groupBundlePath, f))]
            for bundle in bundles:
                pathForBundleFile = join(groupBundlePath, bundle)
                with open(pathForBundleFile) as json_file:
                    data = json.load(json_file)
                    #    def __init__(self,name,desc,root,pieceSize=49152,files=[],path=None):
                    bundleObj = Bundle(data["name"],data["description"],data["id"],data["timestamp"],data["root"],data["pieceSize"],data["files"])
                    group.bundles.append(bundleObj)
        self.groups.append(group)

    def loadGroups(self):
        groups = [group for group in listdir(self.DIR_PATH_GROUPS)]
        for group in groups:
            self.loadGroup(group)

    def addBundle(self, bundle, group):
        if not os.path.exists(self.DIR_PATH_GROUPS + group + "\\" + "Bundles"):
            # Create a new directory because it does not exist
            print("Gonna Create Group Folder")
            os.makedirs(self.DIR_PATH_GROUPS + group + "\\" + "Bundles")
        json_file_name = bundle.name + ".json"
        json_file = open(self.DIR_PATH_GROUPS + group + "\\" + "Bundles" + "\\" + json_file_name, "w")
        json_file.write(json.dumps(bundle.toJSON()))
        json_file.close()
        self.getGroupWithName(group).bundles.append(bundle)
        print("Added Bundle")
        print(self.DIR_PATH_GROUPS + group + "\\" + "Bundles")
        print(self.DIR_PATH_GROUPS + group + "\\" + "Bundles" + "\\" + json_file_name)

