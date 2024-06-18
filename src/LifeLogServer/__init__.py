import flask
import os
import pkg_resources

from . import database
from . import weight

API_VERSION = "0.0.1"

DEFAULT_SECRET_KEY='dev'

def create_app(test_config=None):
    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)

    # Set config defaults
    #TODO: tutorial says I can have a proper secret key located in ${instance}/config.py? Once that's done, delete the SECRET_KEY line.
    app.config.from_mapping(
        SECRET_KEY=DEFAULT_SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'lifelog.sqlite'),
    )

    # load actual config values
    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)
    if app.config['SECRET_KEY'] == DEFAULT_SECRET_KEY: # pragma: no cover
        print("WARNING: USING DEFAULT KEY")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/api_version')
    def getAPIVersion():
        """Returns the api version of the Life Log Server.

        .. :quickref: ; Get the api version

        **Example Request**

        .. sourcecode:: bash

            curl --request GET --url https://lifelog.ivanjohnson.net/api_version

        **Example Response**

        .. sourcecode:: http

          HTTP/1.0 200 OK
          Content-Type: text/plain; charset=utf-8

          0.4.0a0
        """
        return flask.Response(f'{API_VERSION}', mimetype='text/plain')

    BASE_URL = '/api/v1'

    @app.route(BASE_URL + '/ping')
    def ping():
        return flask.Response('pong\n', mimetype='text/plain')

    database.init_app(app)

    app.register_blueprint(weight.bp, url_prefix=BASE_URL + '/weight')

    return app
