import logging

from flask import Flask, render_template, request, redirect

from Groups import GroupManager
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
        print(data)
        group_name = data["GroupName"]
        group_desc = data["GroupDesc"]
        try:
            group_priv = data["private"]
        except:
            group_priv = 0
        GroupManager.CreateGroup(group_name, group_desc, group_priv, [(c1.localIP, c1.port)])
        # Refresh Group Manager
        GroupManager.GroupRefresh()
        return redirect("/groups", code=302)


@app.route("/")
def main():
    return render_template("index.html", myIP=c1.publicIP)


@app.route("/groups")
def groups():
    return render_template("groups.html", myIP=c1.publicIP, groups=GroupManager.Groups)

@app.route("/settings")
def settings():
    return render_template("settings.html", myIP=c1.publicIP)

if __name__ == "__main__":
    c1 = Client()
    GroupManager = GroupManager()
    app.run(host='127.0.0.1', port=6700)
