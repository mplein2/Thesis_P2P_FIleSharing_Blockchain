import json
import os


class GroupManager:

    # Constructor To Initialize Group Manager
    # This will Retrieve all stored groups and handle groups.
    def __init__(self):
        self.Groups = []
        self.DIR_PATH_GROUPS = '%s\\TorrentApp\\Groups\\' % os.environ['APPDATA']
        if not os.path.exists(self.DIR_PATH_GROUPS):
            os.makedirs(self.DIR_PATH_GROUPS)
        else:
            groupfiles = os.listdir(self.DIR_PATH_GROUPS)
            for x in groupfiles:
                # Load All Json Group Files
                file = open(self.DIR_PATH_GROUPS + x)
                json_load_group = json.load(file)
                file.close()
                # Append them on Groups List
                loaded_Group = Group(json_load_group["group_name"], json_load_group["peer_list"])
                self.Groups.append(loaded_Group)

    def CreateGroup(self, group_name, peer_list):
        new_group = Group(group_name, peer_list)
        new_group.GroupSave(self.DIR_PATH_GROUPS)

    def JoinGroup(self):
        pass

    def GroupAnnounce(self):
        pass

    def GroupSearchFile(self):
        pass

    def GroupShareFile(self):
        pass

    def GroupSave(self):
        pass


# This will be a class representing a group that the user is part of .
class Group:
    def __init__(self, group_name, peer_list):
        self.group_name = group_name
        self.peer_list = peer_list

    def AddPeer(self, ip, port):
        self.peer_list.append((ip, port))

    def GroupSave(self, DIR_PATH_GROUPS):
        # Create JSON file
        JSONFileName = self.group_name + ".json"
        jsonFile = open(DIR_PATH_GROUPS + "\\" + JSONFileName, "w")
        jsonFile.write(self.toJSON())
        jsonFile.close()

    def toJSON(self):
        return json.dumps(self.__dict__)
