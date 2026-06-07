import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from components.mail.mail import Browser, Sender, Receiver
import flask
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from threading import Thread
from colorama import init, Fore
import webbrowser


init(autoreset=True)
app = Flask(__name__, static_folder="static")
CORS(app)


def show_hello_world(msg):
    webbrowser.open(f"http://localhost:8080/final?text={msg}")


def wait_for_qr_to_arrive():
    print(Fore.BLUE + "Waiting for the qr code...")
    with Browser() as recv_browser:
        receiver = Receiver(recv_browser)
        receiver.receive(show_hello_world, image=True, immediate=False)


@app.route("/final")
def hello_world():
    return flask.render_template("hello_world.html", text=flask.request.args.get('text'))


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/caesar-mail-to-2", methods=["POST"])
def caesarMailTo2():
    encoded = request.args.get("q")
    print(encoded)

    with Browser() as gmail:
        sender = Sender(gmail, typing_delay=0.2)
        sender.send(recv="lianbitterbal@gmail.com", msg=encoded)

    Thread(target=wait_for_qr_to_arrive).start()
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = 8080
    print(Fore.GREEN + f"Flask server started running at port {port}")
    app.run(debug=True, host="localhost", port=port)