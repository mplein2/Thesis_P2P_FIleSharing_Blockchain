import copy
import json
import pickle
import socket
import threading
from socket import *
from Bundles import Bundle
import Client
from Groups import GroupManager, Group
import os


class Request:
    def __init__(self, type):
        self.type = type

    def toJSON(self):
        return json.dumps(self.__dict__)

#All Classes extended Request even Response Classes just for type and toJSON method.

class JoinRequest(Request):
    def __init__(self, name, timestamp):
        super().__init__(1)
        self.name = name
        self.timestamp = timestamp


class JoinResponse(Request):
    def __init__(self, group):
        super().__init__(1)
        self.group = group


class SearchBundleRequest(Request):
    def __init__(self, groupId, keyword):
        super().__init__(2)
        self.groupID = groupId
        self.keywords = keyword


class SearchBundleResponse(Request):
    def __init__(self, responseBundles):
        super().__init__(2)
        self.responseBundles = responseBundles


class GetBundleRequest(Request):
    def __init__(self, bundleId, groupId, portForBundleReceiver):
        super().__init__(3)
        self.bundleId = bundleId
        self.groupId = groupId
        self.portForBundleReceiver = portForBundleReceiver


class GetBundleResponse(Request):
    def __init__(self, answer):
        super().__init__(3)
        self.answer = answer


class CheckBundleAvailabilityRequest(Request):
    def __init__(self,bundleId, groupId):
        super().__init__(4)
        self.bundleId = bundleId
        self.groupId = groupId

class CheckBundleAvailabilityResponse(Request):
    def __init__(self,answer):
        super().__init__(4)
        self.answer = answer


class DownloadBundleRequest(Request):
    def __init__(self, bundleId, groupId,file, port):
        super().__init__(5)
        self.bundleId = bundleId
        self.groupId = groupId
        self.file = file
        self.port = port


class DownloadBundleResponse(Request):
    def __init__(self, answer):
        super().__init__(5)
        self.answer = answer



def requestHandler(data, addr, groupManager: GroupManager):
    req = pickle.loads(data)
    print(req)

    # Response to JoinRequest
    if req.type == 1:
        req = JoinRequest(req.name, req.timestamp)
        # TODO If this is allowed add peer and respond
        # TODO Peer Port
        groupManager.addPeerGroup(req.name, [addr[0]])
        group = groupManager.getGroupWithName(req.name)
        groupCpy = copy.copy(group)
        del groupCpy.bundles
        joinResponse = JoinResponse(groupCpy)
        return pickle.dumps(joinResponse)

    # Response to search req
    elif req.type == 2:
        # Create The Request again for local use
        req = SearchBundleRequest(req.groupID, req.keywords)
        # Get All Bundles User has
        bundlesOfGroup = groupManager.getGroupWithId(req.groupID).bundles
        # Bundles to reply
        responseBundles = []
        print(responseBundles)
        for bundle in bundlesOfGroup:
            # For each bundle make a single list (bundleKeywords) and search if any of the keywords other user send are in there then send back
            name = bundle.name.split()
            desc = bundle.description.split()
            bundleKeywords = name + desc
            # print("Bundle Keywords : ",bundleKeywords)
            # print("Request Keywords : ",req.keywords)
            if any(keyword in req.keywords for keyword in bundleKeywords):
                # print("HIT")
                responseBundles.append({"id": bundle.id, "name": bundle.name, "description": bundle.description})
        # Create Response and return it to be used as answer
        # print(responseBundles)
        searchResponse = SearchBundleResponse(responseBundles)
        # print("Search Response :",searchResponse)
        return pickle.dumps(searchResponse)

    elif req.type == 3:
        req = GetBundleRequest(req.bundleId, req.groupId, req.portForBundleReceiver)
        group = groupManager.getGroupWithId(req.groupId)
        bundle = group.getBundleWithId(req.bundleId)
        bundleReceiver = threading.Thread(target=sendBundle,
                                          args=[addr, req.portForBundleReceiver, groupManager, group, bundle])
        bundleReceiver.start()
        # TODO refactor use it to determine if user ok to send bundle
        #TODO 9/4 ????
        return pickle.dumps(GetBundleResponse(1))

    elif req.type == 4:
        req = CheckBundleAvailabilityRequest(req.bundleId, req.groupId)
        group = groupManager.getGroupWithId(req.groupId)
        bundle = group.getBundleWithId(req.bundleId)
        if bundle is False:
            #Not Found
            return pickle.dumps(CheckBundleAvailabilityResponse(0))
        else :
            #Found
            return pickle.dumps(CheckBundleAvailabilityResponse(1))

    elif req.type == 5:
        print("Received Request To Send File")
        req = DownloadBundleRequest(req.bundleId, req.groupId, req.file,req.port)
        uploadThread = threading.Thread(target=uploadBundle,
                                          args=[addr, req.port,req.bundleId,req.groupId,req.file,groupManager])
        uploadThread.start()
        # TODO refactor use it to determine if user ok to send bundle
        #TODO 9/4 ????
        return pickle.dumps(DownloadBundleResponse(1))

def responseHandler(data, groupManager):
    res = pickle.loads(data)

    if res.type == 1:
        res = JoinResponse(res.group)
        return res

    elif res.type == 2:
        res = SearchBundleResponse(res.responseBundles)
        return res

    elif res.type == 3:
        res = SearchBundleResponse(res.answer)
        return res

    elif res.type == 4:
        res = CheckBundleAvailabilityResponse(res.answer)
        return res

    elif res.type == 5:
        res = DownloadBundleResponse(res.answer)
        return res


def receiver(groupManager):
    UDP_IP = '0.0.0.0'
    UDP_PORT = 6700
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening on ", UDP_IP, ":", UDP_PORT)
    while True:
        # RECEIVE AND RESPOND.
        data, addr = sock.recvfrom(65537)
        # data, addr = sock.recvfrom(65507)
        print("Received from :", addr)
        response = requestHandler(data, addr, groupManager)
        sock.sendto(response, addr)


def sendRequest(address, port, request, groupManager):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)
    try:
        clientSocket.sendto(request, (address, port))
        data, addr = clientSocket.recvfrom(65537)
        # data, addr = clientSocket.recvfrom(65507)
        res = responseHandler(data, groupManager)
        return res
    # TODO except socket.timeout
    # TODO for better exception handling fix later.
    except Exception as exception:
        # print("Exception on SendRequest:", exception)
        return False


def receiveBundle(port,client,groupManager,groupId,downloadManager):
    print("RECEIVING BUNDLE THREAD")
    bundleBytes = b""
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        print("Bundle Receiver Ready")
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                # print(data)
                bundleBytes = bundleBytes + data
                #TODO save Bytes to group and downloads also start downloading.
                if not data:
                    # print("Break")
                    break
            # print("Break3")
    # print("Bundle Str",bundleBytes.decode())
    bundleObj = json.loads(bundleBytes.decode())
    #Fix Bundle Root to be downloaded and location
    client : Client.Client
    bundleObj["root"] =client.DIR_PATH_DOWNLOADS
    bundle = Bundle(bundleObj["name"],bundleObj["description"],bundleObj["id"],bundleObj["timestamp"],bundleObj["root"],bundleObj["pieceSize"],bundleObj["files"])
    group = groupManager.getGroupWithId(groupId)
    groupManager.addBundle(bundle,group.name)
    downloadManager.downloadBundle(bundle,group)


def sendBundle(addr, port, groupManager, group, bundle):
    print("SENDING BUNDLE THREAD")
    group: Group
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr[0], port))
        print("SENDING DATA")
        groupManager: GroupManager
        json_file_name = bundle.name + ".json"
        bundleDir = groupManager.DIR_PATH_GROUPS + group.name + "\\" + "Bundles" + "\\" + json_file_name
        print(bundleDir)
        print(json_file_name)
        with open(bundleDir) as f:
            bundleContent = f.read()
            bundleObj = json.loads(bundleContent)
            bundleObj["root"] = ""
            bundleStr = json.dumps(bundleObj)

        s.sendall(bundleStr.encode())

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def downloadBundle(port, peer,file,bundle,usedPeers,freeFiles):
    bundle : BundleToDownload
    print("DOWNLOADING BUNDLE THREAD")
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        print("Bundle Receiver Ready")
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr} to download file.")
            data = conn.recv(1024)
            if data.decode() == "OK":
                for piece in file["pieces"]:
                    print(piece)




def uploadBundle(addr, port,bundleId,groupId,file,groupManager):
    print("SENDING BUNDLE THREAD")
    group = groupManager.getGroupWithId(groupId)
    bundle = group.getBundleWithId(bundleId)
    print( file)
    print(bundle.root)
    with open(os.path.join(bundle.root, file), 'rb') as openfileobject:
        with socket(AF_INET, SOCK_STREAM) as s:
            s.connect((addr[0], port))
            print("SENDING DATA")
            s.sendall("OK".encode())
            while True:
                piece = s.recv(1024)
                print(piece)
