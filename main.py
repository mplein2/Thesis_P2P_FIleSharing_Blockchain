import logging
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# This Disables Logging
app.logger.disabled = False
log = logging.getLogger('werkzeug')
log.disabled = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/start', methods=['POST', 'GET'])
def start():
    print("Start Worked")
    return "fuck";


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=6969)
