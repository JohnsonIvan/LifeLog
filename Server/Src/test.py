import flask

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!\n'

@app.route('/ping')
def ping():
    return 'pong\n'

@app.route('/html')
def html():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/fail')
def fail():
    result = {'a': 'b'}
    return flask.make_response(flask.jsonify(result), 201)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
