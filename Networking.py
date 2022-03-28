import socket
from socket import *
import pickle
import copy
import Groups
from Groups import Group


class Request:
    def __init__(self,type):
        self.type = type

    def toJSON(self):
        return json.dumps(self.__dict__)

class JoinRequest(Request):
    def __init__(self,name,timestamp):
        super().__init__(1)
        self.name = name
        self.timestamp = timestamp

class JoinResponse(Request):
    def __init__(self,group):
        super().__init__(1)
        self.group = group

class SearchBundleRequest(Request):
    def __init__(self, groupId, keyword):
        super().__init__(2)
        self.groupID = groupId
        self.keywords = keyword

class SearchBundleResponse(Request):
    def __init__(self,groups):
        super().__init__(2)
        self.responseBundles = responseBundles

def requestHandler(data, addr, groupManager: Groups.GroupManager):
    req = pickle.loads(data)
    # Response to JoinRequest
    if req.type == 1:
        req = JoinRequest(req.name,req.timestamp)
        #TODO If this is allowed add peer and respond
        #TODO Peer Port
        groupManager.addPeerGroup(req.name,[addr[0]])
        group = groupManager.getGroup(req.name)
        groupCpy = copy.copy(group)
        del groupCpy.bundles
        joinResponse = JoinResponse(groupCpy)
        return pickle.dumps(joinResponse)

    elif req.type == 2:
        #Create The Request again for local use
        req = SearchBundleRequest(req.groupID,req.keywords)
        #Get All Bundles User has
        bundlesOfGroup = groupManager.getGroupWithID(req.groupID).bundles
        #Bundles to reply
        responseBundles = []
        for bundle in bundlesOfGroup:
            #For each bundle make a single list (bundleKeywords) and search if any of the keywords other user send are in there then send back
            name = bundle.name.split()
            desc = bundle.description.split()
            bundleKeywords = name + desc
            if any(keyword in req.keywords for keyword in bundleKeywords):
                responseBundles.append({"id":bundle.id,"name":bundle.name,"description":bundle.description})
        #Create Response and return it to be used as answer
        searchResponse = SearchBundleResponse(responseBundles)
        return pickle.dumps(joinResponse)

def responseHandler(data, groupManager):
    res = pickle.loads(data)

    if res.type == 1:
        res = JoinResponse(res.group)
        group = res.group
        group = Groups.Group(group.name,group.private,group.admins,group.peers,group.timestamp)
        groupManager.addGroup(group)

    elif res.type == 2:
        res = SearchBundleResponse(res.responseBundles)
        return res.responseBundles

def receiver(groupManager):
    UDP_IP = '0.0.0.0'
    UDP_PORT = 6700
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening on ", UDP_IP, ":", UDP_PORT)
    while True:
        #RECEIVE AND RESPOND.
        data, addr = sock.recvfrom(65507)
        print(addr,data)
        response = requestHandler(data,addr,groupManager)
        sock.sendto(response,addr)

def sendRequest(address, port, request,groupManager):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(request, (address, port))
    data, addr = clientSocket.recvfrom(65507)
    responseHandler(data, groupManager)



