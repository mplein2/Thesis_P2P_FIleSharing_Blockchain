import logging

from flask import Flask, render_template, request

from client import Client

app = Flask(__name__)

# This Dissabless Logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/create_group", methods=['POST'])
def test():
    if request.method == 'POST':
        data = request.form
        print(data)
        print(data["GroupName"])
        return "ok"


@app.route("/")
def main():
    return render_template("index.html", myIP=c1.publicIP)


@app.route("/groups")
def groups():
    return render_template("groups.html", myIP=c1.publicIP)


if __name__ == "__main__":
    c1 = Client()
    app.run(host='127.0.0.1', port=6700)
