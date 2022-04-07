from Bundles import Bundle
import Groups
from Groups import GroupManager, Group
import os
import copy
import json


class DownloadManager:
    def __init__(self, groupManager):
        self.DIR_PATH_DOWNLOADS = '%s\\TorrentApp\\Downloads\\' % os.environ['APPDATA']
        if not os.path.exists(self.DIR_PATH_DOWNLOADS):
            # Create a new directory because it does not exist
            print("Gonna Create Downloads Folder")
            os.makedirs(self.DIR_PATH_DOWNLOADS)
        # Takes the main groupManager for general use . Updating Peers etc.
        self.groupManager = groupManager
        self.bundlesDownloading = []
        self.loadBundles()

    def downloadBundle(self, bundle: Bundle, group: Group):
        print("Download Manager Creating Download Class for ", bundle.name)
        bundleToDownload = BundleToDownload(bundle, group)
        self.saveBundle(bundleToDownload)
        self.bundlesDownloading.append(bundleToDownload)

    def loadBundles(self):
        bundles = [bundle for bundle in os.listdir(self.DIR_PATH_DOWNLOADS)]
        for bundle in bundles:
            print("DOWNLAOD BUNDLE NAME:", bundle)
            self.loadBundle(self.DIR_PATH_DOWNLOADS + bundle)
        print(self.bundlesDownloading)

    def loadBundle(self, groupDir):
        # try:
        file = open(groupDir)
        json_load_bundle = json.load(file)
        file.close()
        bundle = BundleToDownload(name=json_load_bundle["name"], bundleId=json_load_bundle["bundleId"],
                                  groupId=json_load_bundle["groupId"],
                                  root=json_load_bundle["root"], peers=json_load_bundle["peers"],
                                  files=json_load_bundle["files"])

        self.bundlesDownloading.append(bundle)

    # except:
    #     print("Error Opening Bundle file for download:", groupDir)

    def saveBundle(self, bundleToDownload):
        # Create JSON file
        json_file_name = bundleToDownload.name + ".json"
        json_file = open(self.DIR_PATH_DOWNLOADS + json_file_name, "w")
        json_file.write(json.dumps(bundleToDownload.toJSON()))
        json_file.close()

    def findPeers(self, bundleId, groupId):
        pass

    def getBundleWithId(self, bundleId):
        pass

    def getDownloadProgress(self):
        progressOfBundles = []
        indexNum = 0
        for x in self.bundlesDownloading:
            indexNum = indexNum + 1
            x: BundleToDownload
            totalPieces = 0
            completedPieces = 0
            for file in x.files:
                for piece in file["pieces"]:
                    totalPieces = totalPieces + 1
                    if piece[2] == 1:
                        completedPieces = completedPieces + 1
            pieces = str(completedPieces)+"/"+str(totalPieces)
            progress = completedPieces//totalPieces
            #TODO Status
            progressOfBundle = {"index":indexNum,"name": x.name, "pieces":pieces,"progress":progress,"status":"TODOTHIS"}
            progressOfBundles.append(progressOfBundle)
        return progressOfBundles


class BundleToDownload:
    def __init__(self, bundle=None, group=None, name=None, bundleId=None, groupId=None, root=None, peers=None,
                 files=None):
        if bundleId is None:
            # If Creating From bundle and group.
            self.name = bundle.name
            self.bundleId = bundle.id
            self.groupId = group.id
            self.root = bundle.root
            self.peers = []
            # Get a copy i can manipulate to create BundleToDownload File List.
            bundleTemp = copy.copy(bundle)
            bundleTemp: Bundle

            # Append A 0 For if a piece has been downloaded.
            for file in bundleTemp.files:
                for piece in file["pieces"]:
                    piece.append(0)
            print(bundle.files)

            # Refactor Files to fit BundleToDownload Class
            self.files = bundleTemp.files
        else:
            # If Load
            self.name = name
            self.bundleId = bundleId
            self.groupId = groupId
            self.root = root
            self.peers = peers
            self.files = files

    def toJSON(self):
        return self.__dict__
