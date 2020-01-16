import flask as f
import time

from flask import request
from . import db as database

bp = f.Blueprint('weight', __name__)

#maximum acceptable offset between our clock and the client's
MAX_TIME_ERROR = 300

@bp.route('/record', methods=['POST'])
def record():
    dt = request.args.get('datetime', None, type=int)
    weight = request.args.get('weight', None, type=float)

    if dt is None and weight is None:
        return ("Query is missing both the datetime (int) and weight (float) parameters", 400)
    elif dt is None:
        return ("Query is missing the datetime (int) parameter", 400)
    elif weight is None:
        return ("Query is missing the weight (float) parameter", 400)

    if dt > time.time() + MAX_TIME_ERROR:
        return (f"Given time is {time.time() - dt} seconds in the future.", 400)

    db = database.get_db()

    db.execute('INSERT INTO weight (datetime, weight) VALUES (?, ?)',
               (dt, weight))
    db.commit()


    return "success", 200

@bp.route('/get')
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
