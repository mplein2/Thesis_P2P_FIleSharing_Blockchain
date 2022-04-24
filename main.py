import json
import logging
import threading
from pickle import dumps, loads
from flask import Flask, render_template, request, redirect

import Blockchain
import Compress
from Networking import receiver, sendRequest, JoinRequest, SearchBundleRequest, receiveBundle, GetBundleRequest
from Groups import GroupManager, Invite, Group
from Client import Client
import easygui
from Bundles import BundleManager
from Downloads import DownloadManager

app = Flask(__name__)

# This Disables Logging
app.logger.disabled = False
log = logging.getLogger('werkzeug')
log.disabled = False


# Routes
@app.route("/")
def index():
    progress = downloadManager.getDownloadProgress()
    return render_template("index.html", groups=groupManager.groups, client=client, progress=progress)


@app.route("/groups", methods=['GET'])
def groups():
    group = request.args.get('group')
    group = groupManager.getGroupWithName(group)
    # Check if user should see admin panels.
    peers, bans, admins, owner = group.blockchain.parseBlockchain()
    # Check privs what to show on group page.
    adminPriv = False
    for admin in group.admins:
        if admin[0] == client.publicIP:
            adminPriv = True
            admins.remove([client.publicIP])
            peers.remove([client.publicIP])

    ownerPriv = False
    if group.blockchain.getOwner() == client.publicIP:
        ownerPriv = True

    return render_template("groups.html", groups=groupManager.groups, group=group, client=client, adminPriv=adminPriv,
                           ownerPriv=ownerPriv, peers=peers, bans=bans, admins=admins)


@app.route('/start', methods=['POST', 'GET'])
def start():
    print("Start Worked")
    if downloadManager.STATUS:
        downloadManager.STATUS = False
        # downloadManager Off
        print("Download Manager Not Active")
        return "0"
    else:
        downloadManager.STATUS = True
        # downloadManager On
        print("Download Manager Active")
        return "1"


@app.route('/generateInvite', methods=['POST'])
def generateInvite():
    if request.method == 'POST':
        data = request.form
        group = data["group"]
        group = groupManager.getGroupWithName(group)
        # TODO KEY SPECIFIC BLOCKCHAIN
        ip = data["ip"]  # This is string
        transaction = Blockchain.InviteTransaction(ip)
        transactionStr = json.dumps(transaction.__dict__)
        group.blockchain.addNewTransaction(transactionStr)
        # print("Generate Invite for :", group)
        # print(group)
        invite = group.generateInvite()
        return Compress.compress(invite.toJSON())


@app.route('/deleteBundle', methods=['POST'])
def deleteBundle():
    if request.method == 'POST':
        data = request.form
        groupId = data["groupId"]
        bundleId = data["bundleId"]
        if groupManager.deleteBundle(groupId, bundleId):
            return "1"
        else:
            return "0"


@app.route('/joinGroup', methods=['POST'])
def joinGroup():
    if request.method == 'POST':
        data = request.form
        invite = data["invite"]
        inviteDecomp = Compress.decompress(invite)
        inviteLoad = json.loads(inviteDecomp)
        invite = Invite(inviteLoad["id"], inviteLoad["name"], inviteLoad["timestamp"], inviteLoad["peers"])
        joinReq = JoinRequest(invite.name, invite.timestamp)
        print(invite.peers)
        for peer in invite.peers:
            print(peer[0])
            res = sendRequest(peer[0], 6700, dumps(joinReq))
            if res is not False:
                # Response from user with group data.
                group = res.group
                group = Group(group.name, group.admins, group.peers, group.timestamp,
                              blockchainPath=groupManager.DIR_PATH_GROUPS + group.name + "\\Blockchain", client=client)
                groupManager.addGroup(group)
                # Make Join Transaction.
                transaction = Blockchain.JoinTransaction(client.publicIP,
                                                         client.publicKey.save_pkcs1(format='PEM').decode("utf-8"))
                transactionStr = json.dumps(transaction.__dict__)
                group.blockchain.addNewTransaction(transactionStr)
                # transactionStr = json.dumps(transaction.__dict__)
                # this is string json format
                # print(transactionStr)
                # print(transactionStr.__class__)
                # Genereate signature for Transaction
                # signature = rsa.sign(transactionStr.encode(), client.privateKey, 'SHA-1')
                # genesis_block = Block(0, transactionStr, str(time.time()), "0", [str(signature)])
                # genesis_block.hash = genesis_block.computeHash()
                # self.saveBlock(genesis_block)
                # self.chain.append(genesis_block)
                return "1"
        # No responses.
        return "0"


@app.route('/shareBundle', methods=['POST'])
def shareBundle():
    if request.method == 'POST':
        data = request.form
        name = data["bundleName"]
        desc = data["bundleDescription"]
        groupName = data["groupName"]
        print(name)
        print(desc)
        print(groupName)
        path = easygui.diropenbox(msg="Select folder to share as bundle", title="Share Bundle")
        bundle = bundleManager.createBundle(name, desc, path=path)
        groupManager.addBundle(bundle, groupName)
        return "0"


@app.route('/selectDownloadLocation', methods=['POST'])
def selectDownloadLocation():
    if request.method == 'POST':
        path = easygui.diropenbox(msg="Select folder to download bundles", title="Select Bundle Download Location")
        print(path)
        # Update Download Path in Config
        client.DIR_PATH_DOWNLOADS = path
        client.saveConfig()
        # Return path to browser and update it in modal
        return path


@app.route('/searchBundles', methods=['POST'])
def searchBundles():
    # print("Search Bundles Route")
    if request.method == 'POST':
        data = request.form

        # Get Keywords from search
        keywords = data["searchKeyWords"].split()
        # print("Search for :",keywords)

        # Get Group
        group = data["group"]
        group = groupManager.getGroupWithName(group)

        searchReq = SearchBundleRequest(group.id, keywords)
        responses = []
        # SEND TO ALL PEERS COLLECT RESPONSES AND PRESENT
        for peer in group.peers:
            res = sendRequest(peer[0], 6700, dumps(searchReq))
            # if other peer is responded.
            if res is not False:
                # print(res)
                responses.append([peer[0], res])
            else:
                print("No Response from", peer[0])
        # Merge all responses to single list
        # for x in responses:
        #     print("Response:",x[0],x[1],x[1].responseBundles)
        # WITH RESPONSES DO STUFF.
        # Respond
        return render_template("search.html", groups=groupManager.groups, group=group, responses=responses)


@app.route('/createGroup', methods=['POST'])
def createGroup():
    if request.method == 'POST':
        data = request.form
        name = data["name"]
    if groupManager.createGroup(name, [client.publicIP]):
        # Make First Block In Blockchain Append Admin
        # Type 0 First Created
        group = groupManager.getGroupWithName(name)
        group.blockchain.createGenesisBlock(client)
        # True
        return "0"
    else:
        # False
        return "1"


@app.route('/getBundle', methods=['POST'])
def getBundle():
    if request.method == 'POST':
        data = request.form
        bundleId = data["bundleId"]
        groupId = data["groupId"]
        userIp = data["userIp"]
        # TODO dynamic port on receiver for bundle
        portForBundleReceiver = 6701
        bundleReceiver = threading.Thread(target=receiveBundle,
                                          args=[portForBundleReceiver, client, groupManager, groupId, downloadManager])
        bundleReceiver.start()
        getBundleReq = GetBundleRequest(bundleId, groupId, portForBundleReceiver)
        res = sendRequest(userIp, 6700, dumps(getBundleReq))
        # if other peer is responded.
        if res is not False:
            # Responded decide what to do
            pass
        else:
            # print("No Response from", userIp)
            pass
    return "1"


@app.route('/quitGroup', methods=['POST'])
def quitGroup():
    # print('QUIT GROUP REQ')
    if request.method == 'POST':
        data = request.form
        groupid = data["group"]
        group = groupManager.getGroupWithId(groupid)
        if groupManager.quitGroup(group):
            # True
            return "0"
        else:
            # False
            return "1"


@app.route('/banUser', methods=['POST'])
def banUser():
    if request.method == 'POST':
        data = request.form
        groupid = data["group"]
        userip = data["userip"]
        group = groupManager.getGroupWithId(groupid)
        transaction = Blockchain.BanTransaction(userip)
        transactionStr = json.dumps(transaction.__dict__)
        group.blockchain.addNewTransaction(transactionStr)
        return "0"


@app.route('/unbanUser', methods=['POST'])
def unbanUser():
    if request.method == 'POST':
        data = request.form
        groupid = data["group"]
        userip = data["userip"]
        group = groupManager.getGroupWithId(groupid)
        transaction = Blockchain.UnbanTransaction(userip)
        transactionStr = json.dumps(transaction.__dict__)
        group.blockchain.addNewTransaction(transactionStr)
        return "0"


@app.route('/addAdmin', methods=['POST'])
def addAdmin():
    if request.method == 'POST':
        data = request.form
        groupid = data["group"]
        userip = data["userip"]
        group = groupManager.getGroupWithId(groupid)
        transaction = Blockchain.AddAdminTransaction(userip)
        transactionStr = json.dumps(transaction.__dict__)
        group.blockchain.addNewTransaction(transactionStr)
        return "0"


@app.route('/removeAdmin', methods=['POST'])
def removeAdmin():
    if request.method == 'POST':
        data = request.form
        groupid = data["group"]
        userip = data["userip"]
        group = groupManager.getGroupWithId(groupid)
        transaction = Blockchain.RemoveAdminTransaction(userip)
        transactionStr = json.dumps(transaction.__dict__)
        group.blockchain.addNewTransaction(transactionStr)
        return "0"


if __name__ == "__main__":
    client = Client()
    groupManager = GroupManager(client)
    bundleManager = BundleManager()
    downloadManager = DownloadManager(groupManager, client)
    # TODO Networking Thread To Receive From Internet
    receiver = threading.Thread(target=receiver, args=[groupManager])
    receiver.start()
    app.run(host='', port=6969)
