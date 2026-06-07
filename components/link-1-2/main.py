from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/caesar-mail-to-2", methods=["POST"])
def caesarMailTo2():
    encoded = request.args.get("encoded")
    print(encoded)

if __name__ == "__main__":
    app.run(debug=True)