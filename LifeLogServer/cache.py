import flask as f
import functools
import uuid
import pickle
import time

from http import HTTPStatus

from flask import request

from . import database

def cache(func=None, /, **factoryKwargs):
    if not func:
        return functools.partial(requireAuth)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cacheid = request.args.get('cacheid', None, type=str)
        db = database.get_db()
        if cacheid is not None:
            try:
                uuid.UUID(cacheid)
            except ValueError:
                return ('cacheid header could not be parsed as a UUID (RFC-4122)', HTTPStatus.BAD_REQUEST)
            rows = db.execute('SELECT * FROM cache WHERE ? = uuid', (cacheid, )).fetchall()
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

        db.execute('INSERT INTO cache (uuid, request_time, response) VALUES (?, ?, ?)',
            (cacheid, request_time, bResponse))

        return response

    return wrapper
