import copy
import json
import pickle
import socket
import threading
from socket import *
from Groups import GroupManager, Group


class Request:
    def __init__(self, type):
        self.type = type

    def toJSON(self):
        return json.dumps(self.__dict__)


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


def requestHandler(data, addr, groupManager: GroupManager):
    req = pickle.loads(data)
    # Response to JoinRequest
    if req.type == 1:
        req = JoinRequest(req.name, req.timestamp)
        # TODO If this is allowed add peer and respond
        # TODO Peer Port
        groupManager.addPeerGroup(req.name, [addr[0]])
        group = groupManager.getGroup(req.name)
        groupCpy = copy.copy(group)
        del groupCpy.bundles
        joinResponse = JoinResponse(groupCpy)
        return pickle.dumps(joinResponse)

    # Response to search req
    elif req.type == 2:
        # Create The Request again for local use
        req = SearchBundleRequest(req.groupID, req.keywords)
        # Get All Bundles User has
        bundlesOfGroup = groupManager.getGroupWithID(req.groupID).bundles
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
        group = groupManager.getGroupWithID(req.groupId)
        bundle = group.getBundleWithId(req.bundleId)
        bundleReceiver = threading.Thread(target=sendBundle,
                                          args=[addr, req.portForBundleReceiver, groupManager, group, bundle])
        bundleReceiver.start()
        # TODO refactor use it to determine if user ok to send bundle
        return pickle.dumps(GetBundleResponse(1))


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
        print("Received from :", addr, " data:", data)
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
        print("Exception on SendRequest:", exception)
        return False


def receiveBundle(port):
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
                print(data)
                bundleBytes = bundleBytes + data
                #TODO save Bytes to group and downloads also start downloading.
                if not data:
                    # print("Break")
                    break
#                print("Break2")
#             print("Break3")
#       print("Break4")




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
            print(bundleStr)
        s.sendall(bundleStr.encode())
