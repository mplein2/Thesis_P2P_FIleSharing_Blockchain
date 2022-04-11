import json
import logging
import threading
from pickle import dumps, loads
from flask import Flask, render_template, request, redirect
import Compress
from Networking import receiver, sendRequest, JoinRequest,SearchBundleRequest,receiveBundle,GetBundleRequest
from Groups import GroupManager, Invite,Group
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
    return render_template("index.html", groups=groupManager.groups,client=client,progress=progress)


@app.route("/groups", methods=['GET'])
def groups():
    group = request.args.get('group')
    group = groupManager.getGroupWithName(group)
    return render_template("groups.html", groups=groupManager.groups, group=group)


@app.route('/start', methods=['POST', 'GET'])
def start():
    print("Start Worked")
    # TODO Start downloading
    return "alright"


@app.route('/generateInvite', methods=['POST'])
def generateInvite():
    if request.method == 'POST':
        data = request.form
        group = data["group"]
        print(str(group))
        # TODO IP SPECIFIC BLOCKCHAIN
        ip = data["ip"]
        print("Generate Invite for :", group)
        group = groupManager.getGroupWithName(group)
        print(group)
        invite = group.generateInvite()
        return Compress.compress(invite.toJSON())


@app.route('/joinGroup', methods=['POST'])
def joinGroup():
    if request.method == 'POST':
        data = request.form
        invite = data["invite"]
        inviteDecomp = Compress.decompress(invite)
        inviteLoad = json.loads(inviteDecomp)
        invite = Invite(inviteLoad["id"],inviteLoad["name"], inviteLoad["timestamp"], inviteLoad["peers"])
        joinReq = JoinRequest(invite.name, invite.timestamp)
        # TODO PORTS
        print(invite.peers)
        for peer in invite.peers:
            print(peer[0])
            res = sendRequest(peer[0], 6700, dumps(joinReq), groupManager)
            group = res.group
            group = Group(group.name,group.private,group.admins,group.peers,group.timestamp)
            groupManager.addGroup(group)
        return "1"


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
        bundle = bundleManager.createBundle(name,desc,path=path)
        groupManager.addBundle(bundle,groupName)
        return "0"

@app.route('/selectDownloadLocation', methods=['POST'])
def selectDownloadLocation():
    if request.method == 'POST':
        path = easygui.diropenbox(msg="Select folder to download bundles", title="Select Bundle Download Location")
        print(path)
        #Update Download Path in Config
        client.DIR_PATH_DOWNLOADS=path
        client.saveConfig()
        #Return path to browser and update it in modal
        return path

@app.route('/searchBundles', methods=['POST'])
def searchBundles():
    # print("Search Bundles Route")
    if request.method == 'POST':
        data = request.form

        #Get Keywords from search
        keywords = data["searchKeyWords"].split()
        # print("Search for :",keywords)

        #Get Group
        group = data["group"]
        group = groupManager.getGroupWithName(group)

        searchReq = SearchBundleRequest(group.id,keywords)
        responses = []
        # SEND TO ALL PEERS COLLECT RESPONSES AND PRESENT
        for peer in group.peers:
            res = sendRequest(peer[0], 6700, dumps(searchReq), groupManager)
            #if other peer is responded.
            if res is not False:
                # print(res)
                responses.append([peer[0],res])
            else:
                print("No Response from",peer[0])
        #Merge all responses to single list
        # for x in responses:
        #     print("Response:",x[0],x[1],x[1].responseBundles)
        #WITH RESPONSES DO STUFF.
        #Respond
        return render_template("search.html", groups=groupManager.groups, group=group , responses = responses)

@app.route('/createGroup', methods=['POST'])
def createGroup():
    if request.method == 'POST':
        data = request.form
        name = data["name"]
        if data["private"]:
            private = 1
        else:
            private = 0
    if groupManager.createGroup(name, private, [client.publicIP]):
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
        #TODO dynamic port on receiver for bundle
        portForBundleReceiver = 6701
        bundleReceiver = threading.Thread(target=receiveBundle, args=[portForBundleReceiver,client,groupManager,groupId,downloadManager])
        bundleReceiver.start()
        getBundleReq = GetBundleRequest(bundleId,groupId,portForBundleReceiver)
        res = sendRequest(userIp, 6700, dumps(getBundleReq), groupManager)
        # if other peer is responded.
        if res is not False:
            #Responded decide what to do
            pass
        else:
            # print("No Response from", userIp)
            pass
    return "1"


@app.route('/quitGroup', methods=['POST'])
def quitGroup():
    print('QUIT GROUP REQ')
    if request.method == 'POST':
        data = request.form
        group = data["group"]
        if groupManager.quitGroup(group):
            # True
            return "0"
        else:
            # False
            return "1"


if __name__ == "__main__":
    client = Client()
    groupManager = GroupManager()
    bundleManager = BundleManager()
    downloadManager = DownloadManager(groupManager,client)
    receiver = threading.Thread(target=receiver, args=[groupManager])
    receiver.start()
    app.run(host='', port=6969)
