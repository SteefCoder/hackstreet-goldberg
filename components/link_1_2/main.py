import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from components.mail.mail import Browser, Sender, Receiver
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

def send_mail(msg):
    with Browser() as gmail:
        sender = Sender(gmail, typing_delay=0.2)
        sender.send(recv="lianbitterbal@gmail.com", msg=msg)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/caesar-mail-to-2", methods=["POST"])
def caesarMailTo2():
    encoded = request.args.get("q")
    print(encoded)
    send_mail(encoded)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)