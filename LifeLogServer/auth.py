import flask as f
import functools

from . import database

from http import HTTPStatus

AUTH_HEADER="token"

__PERM_ROOT='ultimate'

def requireAuth(func=None, /, permissions=["ultimate"], userid_keyword="userid"):
    """In order to authenticated a particular user, you must provide one of that user's tokens in the 'token' header.

    **Example**:

    .. sourcecode:: bash

       curl --header 'token: 488bf926-f046-4e59-ae62-04431f211fc2' --request GET --url 'https://lifelog.ivanjohnson.net/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0'

    At present there is no automatic way of obtaining an API token.
    """
    if not func:
        return functools.partial(requireAuth, permissions=permissions, userid_keyword=userid_keyword)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            givenToken = f.request.headers[AUTH_HEADER]
        except KeyError:
            return (f'You must use the \"{AUTH_HEADER}\" header to authenticate', HTTPStatus.UNAUTHORIZED)

        db = database.get_db()

        rows = db.execute('SELECT userid FROM tokens WHERE token = ?', (givenToken,)).fetchone()
        if rows is None or len(rows) == 0:
            return ("The provided auth token is invalid", HTTPStatus.UNAUTHORIZED)
        userid = rows['userid']

        rows = db.execute('SELECT permission FROM token_perms WHERE token = ?', (givenToken,)).fetchall()
        token_perms = list(map(lambda row: row['permission'], rows))
        missing_permissions = []
        if __PERM_ROOT not in token_perms:
            for req in permissions:
                if req not in token_perms:
                    missing_permissions.append(req)
        if len(missing_permissions) > 0:
            return (f"The provided auth token is missing the following permissions: {missing_permissions}", HTTPStatus.FORBIDDEN)

        kwargs[userid_keyword] = userid
        return func(*args, **kwargs)
    return wrapper
