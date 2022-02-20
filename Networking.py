import socket
from socket import *
import pickle

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
        super().__init__(2)
        self.group = group

def requestHandler(data,groupManager):
    req = pickle.loads(data)
    # Response to JoinRequest
    if req.type == 1:
        req = JoinRequest(req.name,req.timestamp)
        group = groupManager.getGroup(req.name)
        return pickle.dumps(JoinResponse(group))


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
        response = requestHandler(data,groupManager)
        sock.sendto(response,addr)

def sendRequest(address, port, request,groupManager):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(request, (address, port))
    data, addr = clientSocket.recvfrom(65507)
    responseHandler(data, groupManager)
