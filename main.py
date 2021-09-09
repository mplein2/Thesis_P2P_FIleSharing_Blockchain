from flask import Flask, render_template

from client import Client

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("index.html", ip=c1.publicIP)


@app.route("/blank")
def blank():
    return render_template("blank.html")


if __name__ == "__main__":
    c1 = Client()
    app.run(host='127.0.0.1', port=6700)
