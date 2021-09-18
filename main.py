import logging
from Groups import GroupManager

from flask import Flask, render_template, request

from client import Client

app = Flask(__name__)

# This Disables Logging
app.logger.disabled = False
log = logging.getLogger('werkzeug')
log.disabled = False


@app.route("/create_group", methods=['POST'])
def create_group():
    if request.method == 'POST':
        data = request.form
        group_name = data["GroupName"]
        GroupManager.CreateGroup(group_name, [(c1.localIP, c1.port)])
        return "ok"


@app.route("/")
def main():
    return render_template("index.html", myIP=c1.publicIP)


@app.route("/groups")
def groups():
    return render_template("groups.html", myIP=c1.publicIP, groups=GroupManager.Groups)


if __name__ == "__main__":
    c1 = Client()
    GroupManager = GroupManager()
    app.run(host='127.0.0.1', port=6700)
