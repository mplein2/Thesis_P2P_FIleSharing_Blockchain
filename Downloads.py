import copy
import json
import os
import threading
from math import floor
from pickle import dumps
from time import sleep

from Bundles import Bundle
from Groups import Group
from Networking import CheckBundleAvailabilityRequest, CheckBundleAvailabilityResponse, sendRequest, is_port_in_use, \
    downloadBundle, DownloadBundleRequest


class DownloadManager:
    def __init__(self, groupManager, client):
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

        # used from downloader()
        # List of list with thread and bundle id its downlaoding [[bundleid,threadObj],[bundleid,threadObj],[bundleid,threadObj]]
        self.activeThreads = []
        self.downloader()
        print("DownloadManager Initialized")

    def downloader(self):
        for bundle in self.bundlesDownloading:
            bundle: BundleToDownload
            # if not completed
            if bundle.getStatus() == 0:
                # Start 1 thread for each bundle not downloaded
                thread = threading.Thread(target=self.downloadThread, args=[bundle])
                self.activeThreads.append([bundle.bundleId, thread])
                thread.start()

    def downloadThread(self, bundle):
        bundle: BundleToDownload
        usedPeers = []
        # Files that are not complete and can be downloaded
        freeFiles = []
        for file in bundle.files:
            complete = True
            for piece in file["pieces"]:
                # 0 = not downloaded yet file is not complete
                if piece[2] == 0:
                    complete = False
                    break
            if complete is False:
                freeFiles.append([file["path"], 0])

        # Peers im going to start connections with
        activePeers = []
        # All Peers that i have found at past that have it . Focus them first .
        seeders = bundle.peers
        # Get Group
        group = self.groupManager.getGroupWithId(bundle.groupId)
        group: Group
        # print("Thread for ",bundle," started.")

        while self.STATUS:
            # print(usedPeers)
            # Find New Peers that have bundle by asking group Peers
            for peer in group.peers:
                # if he already is a peer of this group dont do the rest go to other peer thats not confirmed.
                potentiallyNewPeer = True
                for x in seeders:
                    if x[0] == peer[0]:
                        potentiallyNewPeer = False
                if not potentiallyNewPeer:
                    continue

                # IF PEER IS ME DONT SEND TO MYSELF
                # print("PEER IP ",peer[0])
                # print("MYSELF ",self.client.publicIP)
                if peer[0] != self.client.publicIP:
                    # print(peer[0])
                    # print(self.client.publicIP)
                    checkAvailabilityReq = CheckBundleAvailabilityRequest(bundle.bundleId, bundle.groupId)
                    res = sendRequest(peer[0], 6700, dumps(checkAvailabilityReq))
                    # if other peer is responded.
                    if res is not False:
                        res: CheckBundleAvailabilityResponse
                        if res.answer == 0:
                            # Peer Dosent Have it
                            # TODO PUT PEER IN IGNORE LIST don't send to him again.
                            pass
                        elif res.answer == 1:
                            # Check if he already is in
                            if peer not in seeders:
                                seeders.append(peer)
                            # new peer found update bundle download file.
                            # print("new peep found")
                            if peer not in bundle.peers:
                                bundle.peers.append(peer)
                                self.saveBundle(bundle)

                    else:
                        # Dead peer
                        # print("No Response from", userIp)
                        pass

            # Even though request is same as above no need to chance something
            # reuse code for saem task lead to download from peer with tcp in pieces .

            # From peers that i found and are not already used
            # Downlaod From the Also .
            for peer in bundle.peers:
                if peer not in usedPeers:
                    checkAvailabilityReq = CheckBundleAvailabilityRequest(bundle.bundleId, bundle.groupId)
                    res = sendRequest(peer[0], 6700, dumps(checkAvailabilityReq))
                    # if other peer is responded.
                    if res is not False:
                        res: CheckBundleAvailabilityResponse
                        if res.answer == 0:
                            # Peer Dosent Have it
                            # fuck this below
                            # TODO PUT PEER IN IGNORE LIST don't send to him again.
                            pass
                        elif res.answer == 1:
                            # print("Have peer with bundle to use . ")
                            # Find free port.
                            freePort = False
                            # TODO dynamic
                            port = 6702
                            while freePort is False:
                                if is_port_in_use(port) is True:
                                    port = port + 1
                                else:
                                    freePort = True

                            # Assign File
                            file = []
                            for fileToDownload in freeFiles:
                                if fileToDownload[1] == 0:
                                    file = fileToDownload
                                    # Block others use the same file
                                    fileToDownload[1] = 1
                                    break
                            # if no file to download (all completed -> break)
                            if len(file) == 0:
                                break

                            # ADD PEER TO USED PEERS.
                            usedPeers.append(peer)
                            # Download Bundle is a networking function not self.function .
                            downloadReceiver = threading.Thread(target=downloadBundle,
                                                                args=[self, port, peer, file, bundle, usedPeers,
                                                                      freeFiles])
                            downloadReceiver.start()
                            # print(f"File :{file}")
                            downloadBundleReq = DownloadBundleRequest(bundle.bundleId, bundle.groupId, file[0], port)
                            res = sendRequest(peer[0], 6700, dumps(downloadBundleReq))

                            if res is False:
                                # User didnt Respond Close Thream And Remove Him from usedPeers.
                                usedPeers.remove(peer)
                                # print("No Response from", peer)

            # Time delay until next iteration .
            if len(freeFiles) == 0:
                # No More Files To Be Downloaded
                self.saveBundle(bundle)
                print(f"All Files Completed for {bundle.name}")
                break
            sleep(1)

    def downloadBundle(self, bundle: Bundle, group: Group):
        # print("Download Manager Creating Download Class for ", bundle.name)
        bundleToDownload = BundleToDownload(bundle, group)
        self.saveBundle(bundleToDownload)
        self.bundlesDownloading.append(bundleToDownload)
        # Re Initialize Downloader
        self.downloader()

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
                                  root=json_load_bundle["root"], pieceSize=json_load_bundle["pieceSize"],
                                  peers=json_load_bundle["peers"],
                                  files=json_load_bundle["files"])

        self.bundlesDownloading.append(bundle)

    # except:
    #     print("Error Opening Bundle file for download:", groupDir)

    def saveBundle(self, bundle):
        # Create JSON file
        json_file_name = bundle.name + ".json"
        json_file = open(self.DIR_PATH_DOWNLOADS + json_file_name, "w")
        json_file.write(json.dumps(bundle.toJSON()))
        json_file.close()

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
            pieces = str(completedPieces) + "/" + str(totalPieces)
            # Get progress as a % eg. 70%
            progress = floor((completedPieces / totalPieces) * 100)
            if progress > 99:
                status = 1
            else:
                status = 0
            progressOfBundle = {"index": indexNum, "name": x.name, "pieces": pieces, "progress": progress,
                                "status": status}
            progressOfBundles.append(progressOfBundle)
        return progressOfBundles


class BundleToDownload:

    def __init__(self, bundle=None, group=None, name=None, bundleId=None, groupId=None, root=None, pieceSize=None,
                 peers=None,
                 files=None):
        if bundleId is None:
            # If Creating From bundle and group.
            self.name = bundle.name
            self.bundleId = bundle.id
            self.groupId = group.id
            self.pieceSize = bundle.pieceSize
            self.root = bundle.root
            self.peers = []
            # Get a copy i can manipulate to create BundleToDownload File List.
            bundleTemp = copy.copy(bundle)
            bundleTemp: Bundle

            # Append A 0 For if a piece has been downloaded.
            for file in bundleTemp.files:
                for piece in file["pieces"]:
                    piece.append(0)
            # print(bundle.files)

            # Refactor Files to fit BundleToDownload Class
            self.files = bundleTemp.files
        else:
            # If Load
            self.name = name
            self.bundleId = bundleId
            self.groupId = groupId
            self.root = root
            self.pieceSize = pieceSize
            self.peers = peers
            self.files = files

    def getStatus(self):
        # Status = 0 if not completed 1 if completed
        totalPieces = 0
        completedPieces = 0
        for file in self.files:
            for piece in file["pieces"]:
                totalPieces = totalPieces + 1
                if piece[2] == 1:
                    completedPieces = completedPieces + 1
        if totalPieces == completedPieces:
            return 1
        else:
            return 0

    def toJSON(self):
        return self.__dict__
