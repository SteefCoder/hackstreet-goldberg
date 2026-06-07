import flask

app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return flask.render_template("hello_world.html", text=flask.request.args.get('text'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
