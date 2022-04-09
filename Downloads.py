from Bundles import Bundle
import Groups
from Groups import GroupManager, Group
import os
import copy
import json
import threading
from Networking import CheckBundleAvailabilityRequest,CheckBundleAvailabilityResponse,sendRequest
from pickle import dumps,loads
from time import sleep

class DownloadManager:
    def __init__(self, groupManager,client):
        self.client = client
        self.STATUS = True
        self.DIR_PATH_DOWNLOADS = '%s\\TorrentApp\\Downloads\\' % os.environ['APPDATA']
        if not os.path.exists(self.DIR_PATH_DOWNLOADS):
            # Create a new directory because it does not exist
            print("Creating Downloads Folder")
            os.makedirs(self.DIR_PATH_DOWNLOADS)
        # Takes the main groupManager for general use . Updating Peers etc.
        self.groupManager = groupManager
        self.bundlesDownloading = []
        self.loadBundles()

        #used from downloader()
        #List of list with thread and bundle id its downlaoding [[bundleid,threadObj],[bundleid,threadObj],[bundleid,threadObj]]
        self.activeThreads=[]
        self.downloader()
        print("DownloadManager Initialized")






    def downloader(self):

        for bundle in self.bundlesDownloading:
            bundle : BundleToDownload
            if bundle.getStatus()==0:
                #Start 1 thread for each bundle not downloaded
                thread = threading.Thread(target=self.downloadThread, args=[bundle])
                self.activeThreads.append([bundle.bundleId, thread])
                thread.start()


    def downloadThread(self,bundle):
        bundle : BundleToDownload
        #Peers im going to start connections with
        activePeers = []

        #All Peers that i have found at past that have it . Focus them first .
        allPeers = bundle.peers


        #Get Group
        group = self.groupManager.getGroupWithId(bundle.groupId)
        group: Group


        # print("Thread for ",bundle," started.")



        while self.STATUS:
            #From Previously Found Peers (allPeers) Check If active and start transfer .
            #Put them in activePeers if active . (Start downloading immediately)
            # print(allPeers)
            # if len(allPeers):
            #     for peer in allPeers:
            #         checkAvailabilityReq = CheckBundleAvailabilityRequest(bundleId, groupId)
            #         res = sendRequest(peer, 6700, dumps(checkAvailabilityReq), groupManager)
            #         # if other peer is responded.
            #         if res is not False:
            #             res : CheckBundleAvailabilityResponse
            #             if res.response == 0:
            #                 #Peer Dosent Have it
            #                 #FUCK
            #                 pass
            #             elif res.response == 1:
            #                 #Peer has it
            #                 pass
            #         else:
            #             #Dead peer
            #             print("No Response from", userIp)


            #Find New Peers that have bundle by asking group Peers
            # Ones that have it append to all Peers And Active Peers
            for peer in group.peers:
                #IF PEER IS ME DONT SEND TO MYSELF
                # print("PEER IP ",peer[0])
                # print("MYSELF ",self.client.publicIP)
                if peer[0]!=self.client.publicIP:
                    # print(peer[0])
                    # print(self.client.publicIP)
                    checkAvailabilityReq = CheckBundleAvailabilityRequest(bundle.bundleId, bundle.groupId)
                    res = sendRequest(peer[0], 6700, dumps(checkAvailabilityReq), self.groupManager)
                    # if other peer is responded.
                    if res is not False:
                        res : CheckBundleAvailabilityResponse
                        if res.answer == 0:
                            #Peer Dosent Have it
                            #fuck this below
                            #TODO PUT PEER IN IGNORE LIST don't send to him again.
                            pass
                        elif res.answer == 1:
                            allPeers.append(peer)
                            activePeers.append((peer,0))
                    else:
                        #Dead peer
                        # print("No Response from", userIp)
                        pass

            # print(allPeers)
            # print(activePeers)

            #From peers that i found and are not already used
            #Downlaod From the Also .


            #Time delay until next iteration .
            #If status changed it will be paused.
            #Sleep()
            # print("CONTINUING TO DOWNLOAD")
            sleep(30)

    def downloadFromPeer(self):
        pass





    def downloadBundle(self, bundle: Bundle, group: Group):
        print("Download Manager Creating Download Class for ", bundle.name)
        bundleToDownload = BundleToDownload(bundle, group)
        self.saveBundle(bundleToDownload)
        self.bundlesDownloading.append(bundleToDownload)


    def findPeers(self):
        pass


    def loadBundles(self):
        bundles = [bundle for bundle in os.listdir(self.DIR_PATH_DOWNLOADS)]
        for bundle in bundles:
            # print("DOWNLAOD BUNDLE NAME:", bundle)
            self.loadBundle(self.DIR_PATH_DOWNLOADS + bundle)
        # print(self.bundlesDownloading)

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

    def getStatus(self):
        #Status = 0 if not completed 1 if completed
        totalPieces = 0
        completedPieces = 0
        for file in self.files:
            for piece in file["pieces"]:
                totalPieces = totalPieces + 1
                if piece[2]==1:
                    completedPieces = completedPieces + 1
        if totalPieces==completedPieces:
            return 1
        else:
            return 0


    def toJSON(self):
        return self.__dict__
