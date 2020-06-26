import datetime
import flask as f
import io
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as mpl_pyplot
import time
import uuid

from matplotlib.backends.backend_agg import FigureCanvasAgg as mpl_FigureCanvas

from flask import request
from http import HTTPStatus

from . import database
from . import auth
from . import cache

__UNIT_DATA=[{"unit": "kilograms", "kg_per_unit": 1}, {"unit": "pounds", "kg_per_unit": 0.45359237}]
__UNITS = list(map(lambda d: d['unit'], __UNIT_DATA))

bp = f.Blueprint('weight', __name__)

#maximum acceptable offset between our clock and the client's
sMAX_TIME_ERROR = 300

#@bp.route('/entry/<uuid:id>', methods=['GET'])
#@auth.requireAuth()
#def entry_get(userid):
#    #TODO

def kg_from_unsafe(value, units):
    try:
        value = float(value)
    except:
        return None
    for dictionary in __UNIT_DATA:
        if dictionary["unit"] == units:
            return value * dictionary["kg_per_unit"]
    return None

def usafeunit_from_kg(kg, units):
    for dictionary in __UNIT_DATA:
        if dictionary["unit"] == units:
            return kg / dictionary["kg_per_unit"]
    return None

@bp.route('/entry', methods=['POST'])
@database.autocommit_db
@cache.cache
@auth.requireAuth
def entry_add(userid):
    """Add one new weight entry

    .. :quickref: Weight; Log new weight entry

    Omitting any query string parameters results in undefined behavior.

    Requires authentication (See :ref:`authentication`).

    :query datetime: Integer number of seconds since the Unix epoch, representing the time the measurement was made at
    :query weight: The recorded weight in kilograms
    :query units: Specifies the units of measure for the `weight` parameter
    :status 201: measurement created
    :status 400: possibly returned when missing parameters
    :status 422: possibly returned when provided date is in the future
    """

    dt = request.args.get('datetime', None, type=int)
    weight = request.args.get('weight', None, type=float)
    units = request.args.get('units', None, type=str)

    num_missing_params=(dt is None) or (weight is None) or (units is None)
    if num_missing_params > 0:
        if num_missing_params == 1: # pragma: no cover
            msg = "The following query string parameter is missing:\n"
        else: # pragma: no cover
            msg = "The following {num_missing_params} query string parameters are missing:\n"
        if dt is None: # pragma: no cover
            msg += "\tdatetime (int)\n"
        if weight is None: # pragma: no cover
            msg += "\tweight (float)\n"
        if units is None: # pragma: no cover
            msg += "\tunits (float)\n"

        return (msg, HTTPStatus.BAD_REQUEST)

    weight_kg = kg_from_unsafe(weight, units)
    if weight_kg is None:
        msg = f'The provided measurement, "{weight} {units}", is not valid. The "weight" parameter must be a number and the "units" parameter must be one of {__UNITS}'
        return (msg, HTTPStatus.BAD_REQUEST)


    now = time.time()
    if dt > now + sMAX_TIME_ERROR:
        sErr=dt - now
        msg = f"The given time ({dt}) is in the future; the current time is {now}."
        if sErr > (now - 60*60*24*365)*1e3: # pragma: no cover
            msg += "\n\tMaybe the time parameter was provided in units of milliseconds instead of seconds?"
        return (msg, HTTPStatus.UNPROCESSABLE_ENTITY)


    uid = uuid.uuid4()

    db = database.get_db()
    db.execute('INSERT INTO weight (id, userid, datetime, weight_kg) VALUES (?, ?, ?, ?)',
               (str(uid), userid, dt, weight_kg))

    return f"{uid}", HTTPStatus.CREATED

@bp.route('/entry/<uuid:entryid>', methods=['PUT'])
@database.autocommit_db
@cache.cache
@auth.requireAuth()
def entry_update(userid, entryid):
    """Update the given weight entry.

    .. :quickref: Weight; Update the given weight entry.

    Requires authentication (See :ref:`authentication`).

    :query datetime: new datetime (optional)
    :query weight: new weight (optional)
    :query units: units for new weight (optional)
    :status 204: Success
    """
    dt = request.args.get('datetime', None, type=int)
    weight = request.args.get('weight', None, type=float)
    units = request.args.get('units', None, type=str)

    if dt is None and weight is None:
        return f'You must provide at least one of the two parameters "datetime" (an int) and "weight" (a float)', HTTPStatus.BAD_REQUEST

    if (weight is not None) and (units is None):
        return f'You must specify the units of the provided weight measurement using the "units" parameter', HTTPStatus.BAD_REQUEST

    weight_kg = kg_from_unsafe(weight, units)

    if (weight is not None) and (weight_kg is None):
        assert(units not in __UNITS)
        return f'The value of "units" must be one of {__UNITS}; the value you gave is {units}.', HTTPStatus.BAD_REQUEST

    db = database.get_db()

    if dt is None:
        ret = db.execute('UPDATE weight SET             weight_kg=? WHERE userid=? AND id=?',
                                            (           weight_kg,     str(userid), str(entryid)))
    elif weight_kg is None:
        ret = db.execute('UPDATE weight SET datetime=?           WHERE userid=? AND id=?',
                                            (dt,                    str(userid), str(entryid)))
    else:
        ret = db.execute('UPDATE weight SET datetime=?, weight_kg=? WHERE userid=? AND id=?',
                                            (dt,        weight_kg,     str(userid), str(entryid)))

    if ret.rowcount == 0:
        return f"", HTTPStatus.UNPROCESSABLE_ENTITY
    elif ret.rowcount == 1:
        return f"", HTTPStatus.NO_CONTENT
    else: # pragma: no cover
        assert(False)

@bp.route('/entry/<uuid:entryid>', methods=['DELETE'])
@database.autocommit_db()
@cache.cache()
@auth.requireAuth()
def entry_delete(userid, entryid):
    """Delete one weight entry.

    .. :quickref: Weight; Delete one weight entry.

    Requires authentication (See :ref:`authentication`).

    :status 204: Success
    :status 422: provided entryid does not exist
    """
    db = database.get_db()

    ret = db.execute('DELETE FROM weight WHERE userid=?      AND id=?',
                                               (str(userid),     str(entryid)))

    if ret.rowcount == 0:
        return f"", HTTPStatus.UNPROCESSABLE_ENTITY
    elif ret.rowcount == 1:
        return f"", HTTPStatus.NO_CONTENT
    else: # pragma: no cover
        assert(False)

@bp.route('/batch', methods=['GET'])
@auth.requireAuth()
def batch_get(userid):
    """Get weight measurements for a given time range.

    .. :quickref: Weight; Get collection of weight measurements.

    Omitting any query parameter results in undefined behavior.

    Requires authentication (See :ref:`authentication`).

    The "format" parameter controls how the data is returned. The possibilities are:

    * "csv" (default): The data is returned as a csv text file with one row for
      each measurement. In order, the columns are:

      #. the id of the entry
      #. the time of the measurement
      #. the recorded weight in kilograms

    * "scatter": The data is returned as an image of a scatter plot.

      This defines additional query string parameters:

      * time_format: the format string for dates (as defined by https://docs.python.org/3/library/datetime.html#datetime.datetime.strftime)
      * marker_size: proportional to the area of the marker (see the "s" parameter of https://matplotlib.org/3.2.1/api/_as_gen/matplotlib.pyplot.scatter.html)

    :query since: Integer number of seconds since the Unix epoch; return only measurements occuring on or after this time
    :query before: Integer number of seconds since the Unix epoch; return only measurements occuring before this time
    :query limit: Maximum number of results to return. Behavior is undefined when strictly greater than 100.
    :query offset: Instead of returning the start of the sorted list of results, start from this offset.
    :query format: specifies how to represent the data
    :status 400: A required parameter is missing or a parameter is invalid
    :status 422: A required parameter is invalid
    """
    since = request.args.get('since', None, type=int)
    before = request.args.get('before', None, type=int)
    limit = request.args.get('limit', None, type=int)
    offset = request.args.get('offset', None, type=int)
    ret_format = request.args.get('format', 'csv', type=str)
    time_format = request.args.get('time_format', '%Y-%m-%d', type=str) # '%Y-%m-%dT%H:%M:%S' maybe with '%z' at the end for timezone (seems to work?)
    marker_size = request.args.get('marker_size', None, type=int)

    if before is None or since is None or limit is None or offset is None:
        return ("Query is missing missing at least one of the required int parameters: before, since, limit, offset", HTTPStatus.BAD_REQUEST)

    db = database.get_db()

    rows = db.execute('SELECT * FROM weight WHERE userid = ? AND ? <= datetime AND datetime < ? LIMIT ? OFFSET ?',
               (userid, since, before, limit, offset)).fetchall()

    if ret_format == 'csv':
        data = ""
        for row in rows:
            data += f"{row['id']}, {row['datetime']}, {row['weight_kg']}\n"
        return f.Response(data, mimetype='text/csv')
    elif ret_format == 'scatter':
        times = []
        weights = []
        for row in rows:
            time = datetime.datetime.fromtimestamp(row['datetime'])
            times.append(time)
            weights.append(row['weight_kg'])
        assert(len(times) == len(weights))

        fig, ax = mpl_pyplot.subplots(nrows=1, ncols=1)
        ax.scatter(times, weights, s=marker_size)

        ax.xaxis.set_major_formatter(mpl_dates.DateFormatter(time_format))
        ax.set_ylabel('Weight (kg)')
        ax.set_xlabel('Datetime (local time)')
        ax.set_ylim(bottom=0)

        fig.autofmt_xdate()
        fig.tight_layout()

        output = io.BytesIO()
        mpl_FigureCanvas(fig).print_png(output)
        return f.Response(output.getvalue(), mimetype='image/png')
    else:
        return (f"The provided ret_format ({ret_format}) is invalid", HTTPStatus.UNPROCESSABLE_ENTITY)

#@bp.route('/batch', methods=['POST'])
#@auth.requireAuth()
#def batch_add(userid):
#    #TODO
