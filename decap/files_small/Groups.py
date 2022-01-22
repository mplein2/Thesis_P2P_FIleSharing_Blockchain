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
            group_files = os.listdir(self.DIR_PATH_GROUPS)
            for x in group_files:
                # Load All Json Group Files
                file = open(self.DIR_PATH_GROUPS + x)
                json_load_group = json.load(file)
                file.close()
                # Append them on Groups List
                try:
                    loaded_group = Group(json_load_group["group_name"], json_load_group["group_desc"],
                                         json_load_group["group_priv"],
                                         json_load_group["peer_list"])
                    self.Groups.append(loaded_group)
                except:
                    pass

    def CreateGroup(self, group_name, group_desc, group_priv, peer_list):
        group_name = "@" + group_name.replace(" ", "_").lower()
        new_group = Group(group_name, group_desc, group_priv, peer_list)
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

    def GroupRefresh(self):
        # Clear
        self.Groups = []
        # Reload
        group_files = os.listdir(self.DIR_PATH_GROUPS)
        for x in group_files:
            # Load All Json Group Files
            file = open(self.DIR_PATH_GROUPS + x)
            json_load_group = json.load(file)
            file.close()
            # Append them on Groups List
            try:
                loaded_group = Group(json_load_group["group_name"], json_load_group["group_desc"],
                                     json_load_group["group_priv"],
                                     json_load_group["peer_list"])
                self.Groups.append(loaded_group)
            except:
                pass


# This will be a class representing a group that the user is part of .
class Group:
    def __init__(self, group_name, group_desc, group_priv, peer_list):
        self.group_name = group_name
        self.group_desc = group_desc
        self.group_priv = group_priv
        self.peer_list = peer_list

    def AddPeer(self, ip, port):
        self.peer_list.append((ip, port))

    def GroupSave(self, DIR_PATH_GROUPS):
        # Create JSON file
        json_file_name = self.group_name + ".json"
        json_file = open(DIR_PATH_GROUPS + "\\" + json_file_name, "w")
        json_file.write(self.toJSON())
        json_file.close()

    def toJSON(self):
        return json.dumps(self.__dict__)
