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
    return render_template("index.html")


@app.route("/groups")
def groups():
    return render_template("groups.html")


@app.route('/start', methods=['POST', 'GET'])
def start():
    print("Start Worked")
    return "fuck"


@app.route('/createGroup', methods=['POST'])
def createGroup():
    if request.method == 'POST':
        data = request.form
        name = data["name"]
        if data["private"]:
            private = 1
        else:
            private = 0
    if groupManager.createGroup(name, private, [client.publicIP ]):
        # True
        return "0"
    else:
        # False
        return "1"


if __name__ == "__main__":
    client = Client()
    groupManager = GroupManager()
    app.run(host='127.0.0.1', port=6969)
