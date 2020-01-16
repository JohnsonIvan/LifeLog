import os

import flask


def create_app(test_config=None):
    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)

    # Set config defaults
    #TODO: tutorial says I can have a proper secret key located in ${instance}/config.py? Once that's done, delete the SECRET_KEY line.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'lifelog.sqlite'),
    )

    # load actual config values
    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    BASE_URL = '/api/v1'

    @app.route(BASE_URL + '/')
    def hello_world():
        return flask.Response('Hello, World!\n', mimetype='text/plain')

    @app.route(BASE_URL + '/ping')
    def ping():
        return flask.Response('pong\n', mimetype='text/plain')

    @app.route(BASE_URL + '/html')
    def html():
        return "<h1 style='color:blue'>Hello There!</h1>"

    @app.route(BASE_URL + '/fail')
    def fail():
        result = {'a': 'b'}
        return (result, 500)


    return app
