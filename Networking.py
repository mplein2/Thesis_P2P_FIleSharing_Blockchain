import copy
import hashlib
import json
import os
import pickle
import socket
import threading
from socket import *

import Blockchain
import Client
from Bundles import Bundle
from Groups import GroupManager, Group


class Request:
    def __init__(self, type):
        self.type = type

    def toJSON(self):
        return json.dumps(self.__dict__)


# All Classes extended Request even Response Classes just for type and toJSON method.

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
    def __init__(self, bundleId, groupId):
        super().__init__(4)
        self.bundleId = bundleId
        self.groupId = groupId


class CheckBundleAvailabilityResponse(Request):
    def __init__(self, answer):
        super().__init__(4)
        self.answer = answer


class DownloadBundleRequest(Request):
    def __init__(self, bundleId, groupId, file, port):
        super().__init__(5)
        self.bundleId = bundleId
        self.groupId = groupId
        self.file = file
        self.port = port


class DownloadBundleResponse(Request):
    def __init__(self, answer):
        super().__init__(5)
        self.answer = answer


class UpdateBlockchainRequest(Request):
    def __init__(self, groupId):
        super().__init__(6)
        self.groupId = groupId


class UpdateBlockchainResponse(Request):
    def __init__(self, answer):
        super().__init__(6)
        self.answer = answer


class GetBlockRequest(Request):
    def __init__(self, groupId, blockIndex):
        super().__init__(7)
        self.groupId = groupId
        self.blockIndex = blockIndex


class GetBlockResponse(Request):
    def __init__(self, answer):
        super().__init__(7)
        self.answer = answer


class GetSignatureRequest(Request):
    def __init__(self, groupId, lastIndex, transaction):
        super().__init__(8)
        self.groupId = groupId
        self.lastIndex = lastIndex
        self.transaction = transaction


class GetSignatureResponse(Request):
    def __init__(self, answer):
        super().__init__(8)
        self.answer = answer


def requestHandler(data, addr, groupManager: GroupManager):
    req = pickle.loads(data)
    print(f"Received From {addr[0]}:{addr[1]} {req.__class__.__name__}")

    # Response to JoinRequest
    # TODO refactor this.
    if req.type == 1:
        req = JoinRequest(req.name, req.timestamp)
        group = groupManager.getGroupWithName(req.name)
        if group.blockchain.isUserAllowed(addr[0]):
            groupManager.addPeerGroup(req.name, [addr[0]])
            groupCpy = copy.copy(group)
            del groupCpy.bundles
            joinResponse = JoinResponse(groupCpy)
            return pickle.dumps(joinResponse)
        else:
            return False

    # Response to search req
    elif req.type == 2:
        # Create The Request again for local use
        req = SearchBundleRequest(req.groupID, req.keywords)
        # Get All Bundles User has
        bundlesOfGroup = groupManager.getGroupWithId(req.groupID).bundles
        # Bundles to reply
        responseBundles = []
        # print(responseBundles)
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
        return pickle.dumps(GetBundleResponse(1))

    elif req.type == 4:
        req = CheckBundleAvailabilityRequest(req.bundleId, req.groupId)
        group = groupManager.getGroupWithId(req.groupId)
        bundle = group.getBundleWithId(req.bundleId)
        if bundle is False:
            # Not Found
            return pickle.dumps(CheckBundleAvailabilityResponse(0))
        else:
            # Found
            return pickle.dumps(CheckBundleAvailabilityResponse(1))

    elif req.type == 5:
        # print("Received Request To Send File")
        req = DownloadBundleRequest(req.bundleId, req.groupId, req.file, req.port)
        uploadThread = threading.Thread(target=uploadBundle,
                                        args=[addr, req.port, req.bundleId, req.groupId, req.file, groupManager])
        uploadThread.start()
        return pickle.dumps(DownloadBundleResponse(1))

    elif req.type == 6:
        req = UpdateBlockchainRequest(req.groupId)
        group = groupManager.getGroupWithId(req.groupId)
        # If i am in group for group that im not in.
        if group is not False:
            if group.blockchain.isUserAllowed(addr[0]):
                # User is ok
                lastBlock = group.blockchain.getLastBlock()
                lastBlock: Blockchain.Block
                lastBlockIndex = lastBlock.index
                return pickle.dumps(UpdateBlockchainResponse(lastBlockIndex))
            else:
                # User not invited not joined, therefore don't answer.
                return False

    elif req.type == 7:
        req = GetBlockRequest(req.groupId, req.blockIndex)
        group = groupManager.getGroupWithId(req.groupId)
        block = group.blockchain.getBlockWithIndex(req.blockIndex)
        if block is not False:
            return pickle.dumps(GetBlockResponse(block))
        else:
            return False

    elif req.type == 8:
        req = GetSignatureRequest(req.groupId, req.lastIndex, req.transaction)
        group = groupManager.getGroupWithId(req.groupId)
        lastIndex = group.blockchain.getLastBlockIndex()
        # If up to date or more
        if lastIndex == req.lastIndex:
            # Up To date
            if group.blockchain.verifyTransaction(req.transaction):
                # Transaction Ok
                signature = rsa.sign(transactionStr.encode(), group.client.privateKey, 'SHA-1')
                return pickle.dumps(GetSignatureResponse(str(signature.hex())))
            else:
                # Transaction not ok.
                return pickle.dumps(GetSignatureResponse(1))

        else:
            # Not up to date.
            return pickle.dumps(GetSignatureResponse(0))


def responseHandler(data, addr):
    res = pickle.loads(data)

    if res.type == 1:
        res = JoinResponse(res.group)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 2:
        res = SearchBundleResponse(res.responseBundles)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 3:
        res = SearchBundleResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 4:
        res = CheckBundleAvailabilityResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 5:
        res = DownloadBundleResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 6:
        res = UpdateBlockchainResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 7:
        res = GetBlockResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res

    elif res.type == 8:
        res = GetSignatureResponse(res.answer)
        print(f"Received from {addr[0]}:{addr[1]} {res.__class__.__name__}")
        return res


def receiver(groupManager):
    UDP_IP = '0.0.0.0'
    UDP_PORT = 6700
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Listening on ", UDP_IP, ":", UDP_PORT)
    while True:
        try:
            # RECEIVE AND RESPOND.
            data, addr = sock.recvfrom(65537)
            # data, addr = sock.recvfrom(65507)
            # print("Received from :", addr)
            response = requestHandler(data, addr, groupManager)
            # Request Handler if not want to answer returns False.
            if response is not False:
                sock.sendto(response, addr)
        except Exception as e:
            pass


def sendRequest(address, port, request):
    # Create a socket for sending files
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)
    try:
        clientSocket.sendto(request, (address, port))
        data, addr = clientSocket.recvfrom(65537)
        res = responseHandler(data, addr)
        return res
    # TODO except socket.timeout
    except Exception as exception:
        # print("Exception on SendRequest:", exception)
        return False


def receiveBundle(port, client, groupManager, groupId, downloadManager):
    # print("RECEIVING BUNDLE THREAD")
    bundleBytes = b""
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        # print("Bundle Receiver Ready")
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connection From {addr[0]}:{addr[1]} Accepted.")
            while True:
                data = conn.recv(1024)
                # print(data)
                bundleBytes = bundleBytes + data
                if not data:
                    # print("Break")
                    break
            # print("Break3")
    # print("Bundle Str",bundleBytes.decode())
    bundleObj = json.loads(bundleBytes.decode())
    # Fix Bundle Root to be downloaded and location
    client: Client.Client
    bundleObj["root"] = client.DIR_PATH_DOWNLOADS
    bundle = Bundle(bundleObj["name"], bundleObj["description"], bundleObj["id"], bundleObj["timestamp"],
                    bundleObj["root"], bundleObj["pieceSize"], bundleObj["files"])
    group = groupManager.getGroupWithId(groupId)
    groupManager.addBundle(bundle, group.name)
    downloadManager.downloadBundle(bundle, group)


def sendBundle(addr, port, groupManager, group, bundle):
    # print("SENDING BUNDLE THREAD")
    group: Group
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr[0], port))
        print(f"Connected To {addr[0]}:{addr[1]}.")
        # print("SENDING DATA")
        groupManager: GroupManager
        json_file_name = bundle.name + ".json"
        bundleDir = groupManager.DIR_PATH_GROUPS + group.name + "\\" + "Bundles" + "\\" + json_file_name
        # print(bundleDir)
        # print(json_file_name)
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


def downloadBundle(downloadManager, port, peer, file, bundle, usedPeers, freeFiles):
    pieceList = []
    # Find pieces missing
    for x in bundle.files:
        if x["path"] == file[0]:
            pieceList = x["pieces"]
            break
    # pieceList = [[0, '5920572cf97d3711a77a9b7a3469a5fd03bb2a8a', 0]]
    # print("DOWNLOADING BUNDLE THREAD")
    filePath = bundle.root + f"\\{bundle.name}" + file[0]
    dir = filePath.rsplit('\\', 1)[0]
    # print(dir)
    # Create Directory's that don't exist.
    isExist = os.path.exists(dir)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(dir)

    if os.path.exists(filePath) is False:
        # print("Creating File")
        file = open(filePath, 'x')
        file.close()

    with open(filePath, 'rb+') as openfileobject:
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            # print("Bundle Receiver Ready")
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connection From {addr[0]}:{addr[1]} Accepted.")
                data = conn.recv(1024)
                if data.decode() == "OK":
                    # print("Received Ok")
                    for piece in pieceList:
                        if piece[2] == 0:
                            # print(f"Sending Piece num {piece[0]} ")
                            conn.sendall(str(piece[0]).encode())
                            openfileobject.seek(piece[0] * bundle.pieceSize)
                            data = conn.recv(100000)
                            # print(f"Received {data}")
                            if hashlib.sha1(data).hexdigest() == piece[1]:
                                # print("HASH OK")
                                openfileobject.write(data)
                                piece[2] = 1
                                # print(piece)
                            else:
                                pass
                                # print("hashes dont match")
                    # delimmiter for data
                    conn.sendall("🥭🍓🍇🍉🍐🥧🍊🍍🍏🥑🍑🍌🍎🍐🍉🍇🍓🥭🥝🍒🍅".encode())
                    usedPeers.remove(peer)
                    downloadManager.saveBundle(bundle)
    # print(f"Thread Exit {file}")


def uploadBundle(addr, port, bundleId, groupId, file, groupManager):
    # print("SENDING BUNDLE THREAD")
    group = groupManager.getGroupWithId(groupId)
    bundle = group.getBundleWithId(bundleId)
    with open(bundle.root + file, 'rb') as openfileobject:
        try:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect((addr[0], port))
                # print("SENDING DATA")
                s.sendall("OK".encode())
                while True:
                    piece = s.recv(1024)
                    # delimmiter for data
                    if piece == "🥭🍓🍇🍉🍐🥧🍊🍍🍏🥑🍑🍌🍎🍐🍉🍇🍓🥭🥝🍒🍅".encode():
                        break
                    else:
                        if piece == b'':
                            # print("Empty")
                            pass
                        else:
                            piece = int(piece.decode())
                            # print(f"Trying to send {piece}")
                            openfileobject.seek(piece * bundle.pieceSize)
                            readData = openfileobject.read(bundle.pieceSize)
                            s.sendall(readData)
        except ConnectionResetError as exception:
            print("Downloader DC")
