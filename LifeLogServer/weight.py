import flask as f
import time

from flask import request
from . import db as database
from . import auth

bp = f.Blueprint('weight', __name__)

#maximum acceptable offset between our clock and the client's
sMAX_TIME_ERROR = 300

@bp.route('/record', methods=['POST'])
@database.get_autocommit_db
@auth.requireAuth
def record(*, db):
    dt = request.args.get('datetime', None, type=int)
    weight = request.args.get('weight', None, type=float)

    if dt is None or weight is None:
        msg = ""
        if dt is None and weight is None: # pragma: no cover
            msg = "Query is missing both the datetime (int) and weight (float) parameters"
        elif dt is None: # pragma: no cover
            msg = "Query is missing the datetime (int) parameter"
        elif weight is None: # pragma: no cover
            msg = "Query is missing the weight (float) parameter"
        return (msg, 400)

    now = time.time()
    if dt > now + sMAX_TIME_ERROR:
        sErr=dt - now
        msg = f"Given time is in the future."
        if sErr > 995*now: # pragma: no cover
            msg += "\nMaybe the time parameter was provided in units of milliseconds instead of seconds?"

        return (msg, 400)

    db.execute('INSERT INTO weight (datetime, weight) VALUES (?, ?)',
               (dt, weight))

    return "success", 200

@bp.route('/get')
@auth.requireAuth()
def get():
    since = request.args.get('since', None, type=int)
    before = request.args.get('before', None, type=int)
    limit = request.args.get('limit', None, type=int)
    offset = request.args.get('offset', None, type=int)

    if before is None or since is None or limit is None or offset is None:
        return ("Query is missing missing at least one of the required int parameters: before, since, limit, offset", 400)

    db = database.get_db()

    rows = db.execute('SELECT * FROM weight WHERE ? <= datetime AND datetime < ? ORDER BY datetime LIMIT ? OFFSET ?',
               (since, before, limit, offset)).fetchall()
    db.commit()

    data = ""
    for row in rows:
        data += f"{row['datetime']}, {row['weight']}\n"

    return f.Response(data, mimetype='text/csv')
