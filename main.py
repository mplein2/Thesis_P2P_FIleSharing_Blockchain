import logging
from flask import Flask, render_template, request, redirect

from Groups import GroupManager
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
        print("Generate Invite for :", group)
        # TODO generate group invite
        compressedInvite = "standard's"
        return compressedInvite


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
    app.run(host='127.0.0.1', port=6969)
