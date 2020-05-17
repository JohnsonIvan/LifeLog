import flask as f
import functools

from . import db as database

from http import HTTPStatus

def requireAuth(func=None, /):
    AUTH_HEADER="token"
    if not func:
        return functools.partial(requireAuth)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = database.get_db()
        try:
            givenToken = f.request.headers[AUTH_HEADER]
        except KeyError:
            return (f'You must use the \"{AUTH_HEADER}\" header to authenticate', HTTPStatus.UNAUTHORIZED)
        rows = db.execute('SELECT * FROM auth_token WHERE token = ?', (givenToken,)).fetchone()
        db.commit()

        if len(rows) == 0:
            return ("The provided auth token does not have access to this resource", HTTPStatus.FORBIDDEN)
        return func(*args, *kwargs)
    return wrapper
