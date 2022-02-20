import json
from json import *
import logging
import threading
from pickle import dumps,loads
from flask import Flask, render_template, request, redirect
import compress
from Networking import receiver,sendRequest,JoinRequest
from Groups import GroupManager,Invite
from Client import Client

app = Flask(__name__)

# This Disables Logging
app.logger.disabled = False
log = logging.getLogger('werkzeug')
log.disabled = False


# Routes
@app.route("/")
def index():
    return render_template("index.html", groups=groupManager.groups)


@app.route("/groups", methods=['GET'])
def groups():
    group = request.args.get('group')
    print("Group page request :", group)
    return render_template("groups.html", groups=groupManager.groups, group=group)


@app.route('/start', methods=['POST', 'GET'])
def start():
    print("Start Worked")
    return "fuck"


@app.route('/generateInvite', methods=['POST'])
def generateInvite():
    if request.method == 'POST':
        data = request.form
        group = data["group"]
        #TODO IP SPECIFIC BLOCKCHAIN
        ip = data["ip"]
        print("Generate Invite for :", group)
        group = groupManager.getGroup(group)
        invite = group.generateInvite()
        return compress.compress(invite.toJSON())


@app.route('/joinGroup', methods=['POST'])
def joinGroup():
    if request.method == 'POST':
        data = request.form
        invite = data["invite"]
        inviteDecomp = compress.decompress(invite)
        inviteLoad = json.loads(inviteDecomp)
        invite = Invite(inviteLoad["name"], inviteLoad["timestamp"], inviteLoad["peers"])
        joinReq = JoinRequest(invite.name,invite.timestamp)
        #TODO PORTS
        print(invite.peers)
        for peer in invite.peers:
            print(peer[0])
            sendRequest(peer[0],6700,dumps(joinReq),groupManager)
        return "1"




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


if __name__ == "__main__":
    client = Client()
    groupManager = GroupManager()
    receiver = threading.Thread(target=receiver, args=[groupManager])
    receiver.start()
    app.run(host='', port=6969)
