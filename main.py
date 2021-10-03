import logging
import threading
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
        GroupManager.CreateGroup(group_name, group_desc, group_priv, [(client.localIP, client.port)])
        # Refresh Group Manager
        GroupManager.GroupRefresh()
        return redirect("/groups", code=302)


@app.route("/change_settings", methods=['POST'])
def change_settings():
    if request.method == 'POST':
        data = request.form
        client.port = data["ClientPort"]
        client.gui_port = data["GUIPort"]
        # TODO fix this make post in js and after response run app and take care of redirect through JS on client_side .
        # try:
        #     return redirect("http://127.0.0.1:" + client.gui_port + "/settings", code=302)
        # finally:
        #     app.run(host='127.0.0.1', port=client.gui_port)
        client.save()


@app.route("/")
def index():
    return render_template("index.html", myIP=client.publicIP)


@app.route("/groups")
def groups():
    return render_template("groups.html", myIP=client.publicIP, groups=GroupManager.Groups)


@app.route("/settings")
def settings():
    return render_template("settings.html", myIP=client.publicIP, GUIPort=client.gui_port, ClientPort=client.port)


if __name__ == "__main__":
    client = Client()
    GroupManager = GroupManager()
    app.run(host='127.0.0.1', port=client.gui_port)
