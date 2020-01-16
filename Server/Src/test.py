import flask

application = flask.Flask(__name__)

#todo: maybe it would be better to use a flask.Blueprint instead of a variable?
BASE_URL = '/api/v1'

@application.route(BASE_URL + '/')
def hello_world():
    return flask.Response('Hello, World!\n', mimetype='text/plain')

@application.route(BASE_URL + '/ping')
def ping():
    return flask.Response('pong\n', mimetype='text/plain')

@application.route(BASE_URL + '/html')
def html():
    return "<h1 style='color:blue'>Hello There!</h1>"

@application.route(BASE_URL + '/fail')
def fail():
    result = {'a': 'b'}
    return (result, 500)

if __name__ == '__main__':
    application.run(host='0.0.0.0')
