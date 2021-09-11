import logging

from flask import Flask, render_template

from client import Client

app = Flask(__name__)

# This Dissabless Logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/")
def main():
    return render_template("dashboard.html", ip=c1.publicIP)


if __name__ == "__main__":
    c1 = Client()
    app.run(host='127.0.0.1', port=6700)
