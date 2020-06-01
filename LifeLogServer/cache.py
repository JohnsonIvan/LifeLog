import flask as f
import functools
import uuid
import pickle
import time

from http import HTTPStatus

from flask import request

from . import database
from . import auth

#TODO: USE HEADERS INSTEAD OF QUERY STRING; LESS LIKELY TO BE SAVED BY BROWSER

def cache(func=None, /, **factoryKwargs):
    if not func:
        return functools.partial(requireAuth)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cacheid = request.args.get('cacheid', None, type=str)
        if cacheid is None:
            return func(*args, **kwargs)
        try:
            uuid.UUID(cacheid)
        except ValueError:
            return ('cacheid header could not be parsed as a UUID (RFC-4122)', HTTPStatus.BAD_REQUEST)


        if auth.AUTH_HEADER in f.request.headers:
            givenToken = f.request.headers[auth.AUTH_HEADER]
        else:
            givenToken = None

        db = database.get_db()
        rows = db.execute('SELECT * FROM cache WHERE uuid = ? AND (token = ? OR (token IS NULL AND ? IS NULL))', (cacheid, givenToken, givenToken)).fetchall()
        assert(len(rows) <= 1)
        if len(rows) == 1:
            row = rows[0]
            cResponse = pickle.loads(row['response'])
            return cResponse


        request_time = int(time.time())

        response = func(*args, **kwargs)
        response = f.make_response(response)
        bResponse = pickle.dumps(response)

        bRequest = pickle.dumps(request)

        db.execute('INSERT INTO cache (uuid, token, request_time, response) VALUES (?, ?, ?, ?)',
                                      (cacheid, givenToken, request_time, bResponse))

        return response

    return wrapper
