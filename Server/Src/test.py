import flask

application = flask.Flask(__name__)

#todo: maybe it would be better to use a flask.Blueprint instead of a variable?
BASE_URL = '/api/v1'

@application.route(BASE_URL + '/')
def hello_world():
    return 'Hello, World!\n'

@application.route(BASE_URL + '/ping')
def ping():
    return 'pong\n'

@application.route(BASE_URL + '/html')
def html():
    return "<h1 style='color:blue'>Hello There!</h1>"

@application.route(BASE_URL + '/fail')
def fail():
    result = {'a': 'b'}
    return flask.make_response(flask.jsonify(result), 201)

if __name__ == '__main__':
    application.run(host='0.0.0.0')
