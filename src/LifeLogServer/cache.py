import flask as f
import functools
import uuid
import pickle
import time

from http import HTTPStatus

from flask import request

from . import database
from . import auth

CACHE_HEADER = "cacheid"

def cache(func=None, /, **factoryKwargs):
    if not func:
        return functools.partial(cache)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cacheid = request.headers.get(CACHE_HEADER, None, type=str)
        givenToken = request.headers.get(auth.AUTH_HEADER, None, type=str)
        if cacheid is None or givenToken is None:
            # TODO: should we return an error this case?
            return func(*args, **kwargs)
        try:
            uuid.UUID(cacheid)
        except ValueError:
            return (f'{CACHE_HEADER} header could not be parsed as a UUID (RFC-4122)\n', HTTPStatus.BAD_REQUEST)

        db = database.get_db()
        rows = db.execute('SELECT * FROM cache WHERE uuid = ? AND token = ?', (cacheid, givenToken)).fetchall()
        assert(len(rows) <= 1)
        if len(rows) == 1:
            row = rows[0]
            cResponse = pickle.loads(row['response'])
            return cResponse


        request_time = int(time.time())

        response = func(*args, **kwargs)
        response = f.make_response(response)
        response.freeze()
        bResponse = pickle.dumps(response)

        db.execute('INSERT INTO cache (uuid, token, request_time, response) VALUES (?, ?, ?, ?)',
                                      (cacheid, givenToken, request_time, bResponse))

        return response

    return wrapper
