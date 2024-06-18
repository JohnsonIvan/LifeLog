import flask
import os
import importlib

from . import database
from . import weight

API_VERSION = importlib.metadata.version("LifeLogServer")

DEFAULT_SECRET_KEY = "dev"


class BadConfigException(Exception):
    pass


class DefaultKeyException(BadConfigException):
    pass


def create_app(
    config_file,
    database_file,
):
    app = flask.Flask(__name__)

    app.config.from_pyfile(config_file)

    if app.config["SECRET_KEY"] is None:  # pragma: no cover
        raise DefaultKeyException("Using the default secret key is not supported")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/api_version")
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
        return flask.Response(f"{API_VERSION}", mimetype="text/plain")

    BASE_URL = "/api/v1"

    @app.route(BASE_URL + "/ping")
    def ping():
        return flask.Response("pong\n", mimetype="text/plain")

    database.init_app(app=app, database_file=database_file)

    app.register_blueprint(weight.bp, url_prefix=BASE_URL + "/weight")

    return app
