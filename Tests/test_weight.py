import time
import urllib
from http import HTTPStatus
import io

import LifeLogServer


import auth_tests
import test_db
import pytest
import csv
import collections

WEIGHT_URL='/api/v1/weight'
ENTRY_URL=f'{WEIGHT_URL}/entry'
BATCH_URL=f'{WEIGHT_URL}/batch'

BATCH_GET_HAPPY_PARAMS={'since':150, 'before':450, 'limit':1, 'offset':1}
BATCH_GET_HAPPY_RESULTS=[[None, '300', '333.0']]

BATCH_GET_ALL_SINCE=0
BATCH_GET_ALL_BEFORE=1000
BATCH_GET_ALL_COUNT=5
BATCH_GET_ALL_PARAMS={'since':BATCH_GET_ALL_SINCE, 'before':BATCH_GET_ALL_BEFORE, 'limit':2*BATCH_GET_ALL_COUNT+100, 'offset':0}

def parse_csv(input, /):
    if type(input) == str:
        string = input
    else:
        assert type(input) == bytes
        string = input.decode('utf-8')
    file = io.StringIO(string)
    reader = csv.reader(file, skipinitialspace=True)
    return list(reader)

def fuzzy_equals(arg1, arg2, /, arg1_ignores_nones=True, arg2_ignores_nones=False):
    """Approximately computes arg1 == arg2. The deviation from this approximation is
    that the comparison is done recursively (only recursive for Mappings and
    Iterables) and if one arg is None and the corresponding argument is True
    then True is returned regardless of the other argument's value.

    e.g. fuzzy_equals([[1,2,3], None,    [7,8,9]],
                      [[1,2,3], [4,5,6], [7,8,9]]) is True
    """
    if not (arg1_ignores_nones or arg2_ignores_nones):
        return arg1 == arg2

    if isinstance(arg1, collections.abc.Mapping):
        assert isinstance(arg2, collections.Mapping)
        assert len(arg1) == len(arg2)
        for key in arg1:
            item1 = arg1[key]
            item2 = arg2[key]
            if not fuzzy_equals(item1, item2):
                return False
        return True
    elif isinstance(arg1, collections.abc.Iterable) and not isinstance(arg1, str):
        assert isinstance(arg2, collections.abc.Iterable)
        assert len(arg1) == len(arg2)
        for (item1, item2) in zip(arg1, arg2):
            if not fuzzy_equals(item1, item2):
                return False
        return True
    else:
        if arg1_ignores_nones and arg1 is None:
            return True
        if arg2_ignores_nones and arg2 is None:
            return True
        return arg1 == arg2

@pytest.mark.unit
@pytest.mark.parametrize("ret_format", ["csv", "scatter", None,])
def test_get_happy(client, ret_format):
    print(f"ret_format: {ret_format}")
    params = BATCH_GET_HAPPY_PARAMS.copy()
    if ret_format is not None:
        params['format'] = ret_format
    else:
        ret_format = "csv"
    params = urllib.parse.urlencode(params)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.charset == 'utf-8'
    if ret_format == "csv":
        assert response.mimetype == 'text/csv'
        assert fuzzy_equals(BATCH_GET_HAPPY_RESULTS, parse_csv(response.data))
    elif ret_format == "scatter":
        assert response.mimetype == 'image/png'

@pytest.mark.unit
def test_batch_get_bad_format(client):
    params = BATCH_GET_HAPPY_PARAMS.copy()
    params['format'] = "iowueljhavnjkasdf"
    params = urllib.parse.urlencode(params)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

@pytest.mark.unit
def test_get_missingParam(client):
    for key in ['since', 'before', 'limit', 'offset']:
        params = BATCH_GET_HAPPY_PARAMS.copy()
        params.pop(key, None)
        params = urllib.parse.urlencode(params)
        url = BATCH_URL + '?' + params
        response = client.get(url, headers=auth_tests.AUTH_HEADERS)
        status = response.status_code
        assert status == HTTPStatus.BAD_REQUEST, f'key = "{key}"; url = "{url}"; status = {status}'

@pytest.mark.integration
def test_get_auth(client):
    params = urllib.parse.urlencode(BATCH_GET_HAPPY_PARAMS)
    url = BATCH_URL + '?' + params

    auth_tests.run_tests(client.get, url)

@pytest.mark.unit
def test_entry_add_happy(monkeypatch, client):
    units="WKz2CVpF"
    value_units=0.89934
    value_kg=0.48191

    def mocked_conversion(tmp_value, tmp_units):
        assert(tmp_value == value_units)
        assert(tmp_units == units)
        return value_kg
    monkeypatch.setattr('LifeLogServer.weight.kg_from_unsafe', mocked_conversion)


    params = urllib.parse.urlencode(BATCH_GET_ALL_PARAMS)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 5


    params = urllib.parse.urlencode({'weight':value_units, 'datetime':450, 'units':units})
    response = client.post(ENTRY_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.CREATED


    params = urllib.parse.urlencode(BATCH_GET_ALL_PARAMS)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    data = parse_csv(response.data)
    assert len(data) == 6
    list_truths = list(map(lambda x: fuzzy_equals([None, "450", str(value_kg)], x), data))
    assert(list_truths.count(True) == 1)

@pytest.mark.unit
@pytest.mark.parametrize("expected_code, params_dict, conv_ret", [
    (HTTPStatus.UNPROCESSABLE_ENTITY, {'units':'kilograms', 'weight': 0.1,     'datetime': 2000000000,  }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {'units':'kilograms',                    'datetime': 0,           }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {'units':'kilograms', 'weight': 0.1,                              }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {'units':'kilograms', 'weight': 'hello', 'datetime': 0,           }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {'units':'kilograms', 'weight': 0.1,     'datetime': 'hello',     }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {                     'weight': 0.1,     'datetime': 0,           }, 0.1, ),
    (HTTPStatus.BAD_REQUEST,          {'units':'LKBi3nuG',  'weight': 0.1,     'datetime': 0,           }, None, ),
])
def test_entry_add_invalid(monkeypatch, client, expected_code, params_dict, conv_ret):
    def mocked_conversion(tmp_value, tmp_units):
        assert('weight' in params_dict and tmp_value == params_dict['weight'])
        assert('units' in params_dict and tmp_units == params_dict['units'])
        return conv_ret
    monkeypatch.setattr('LifeLogServer.weight.kg_from_unsafe', mocked_conversion)

    params = urllib.parse.urlencode(params_dict)
    response = client.post(ENTRY_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == expected_code

@pytest.mark.integration
def test_entry_add_auth(client, monkeypatch):
    weight=0.1
    datetime=450
    units='kilograms'

    def mocked_conversion(tmp_value, tmp_units):
        assert(tmp_value == weight)
        assert(tmp_units == units)
        return tmp_value
    monkeypatch.setattr('LifeLogServer.weight.kg_from_unsafe', mocked_conversion)

    params = urllib.parse.urlencode({'weight':weight, 'datetime':datetime, 'units': units})
    url = ENTRY_URL + '?' + params

    auth_tests.run_tests(client.post, url, expected_status=HTTPStatus.CREATED)

@pytest.mark.integration
def test_entry_add_autocommits(app, client, monkeypatch):
    weight=0.1
    datetime=450
    units='kilograms'

    def mocked_conversion(tmp_value, tmp_units):
        assert(tmp_value == weight)
        assert(tmp_units == units)
        return tmp_value
    monkeypatch.setattr('LifeLogServer.weight.kg_from_unsafe', mocked_conversion)

    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450, 'units': 'kilograms'})
    url = ENTRY_URL + '?' + params

    test_db.count_commits(app, client.post, url, monkeypatch, expected_cc=1, headers=auth_tests.AUTH_HEADERS, expected_status=HTTPStatus.CREATED)

    def fakeTime():
        raise Exception("asdf")

    monkeypatch.setattr('time.time', fakeTime)
    test_db.count_commits(app, client.post, url, monkeypatch, expected_cc=0, headers=auth_tests.AUTH_HEADERS, expected_exception=Exception)

@pytest.mark.unit
def test_entry_delete_happy(app, client):
    entry_id='148064f1-48bc-415d-9ff8-8a57d7ad8687'

    with app.app_context():
        db = LifeLogServer.database.get_db()

        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 1)

        response = client.delete(ENTRY_URL + f'/{entry_id}', headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == HTTPStatus.NO_CONTENT

        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 0)


@pytest.mark.unit
def test_entry_delete_badid(app, client):
    entry_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

    with app.app_context():
        db = LifeLogServer.database.get_db()

        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 0)

        response = client.delete(ENTRY_URL + f'/{entry_id}', headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

@pytest.mark.unit
@pytest.mark.parametrize(
     "entry_id,                              id_exists, add_units, add_datetime, add_weight, expected_error", [
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", True,      True,      False,        True,       None                            ),
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", True,      True,      True,         False,      None                            ),
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", True,      True,      True,         True,       None                            ),
    ('148064f1-48bc-415d-9ff8-8a57d7ad8687', True,      False,     False,        False,      HTTPStatus.BAD_REQUEST          ),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', False,     True,      True,         True,       HTTPStatus.UNPROCESSABLE_ENTITY ),
])
def test_entry_update(monkeypatch, app, client, entry_id, id_exists, add_units, add_datetime, add_weight, expected_error):
    units='VRA7sGtk'
    datetime=61833
    weight_units=0.98068
    weight_kg=0.17910

    def mocked_conversion(tmp_value, tmp_units):
        if add_weight:
            assert(tmp_value == weight_units)
            assert(tmp_units == units)
            return weight_kg
        else:
            assert(tmp_value is None)
            assert(tmp_units == units)
            return None
    monkeypatch.setattr('LifeLogServer.weight.kg_from_unsafe', mocked_conversion)

    params={}
    if add_units:
        params['units'] = units
    if add_datetime:
        params['datetime'] = datetime
    if add_weight:
        params['weight'] = weight_units
    with app.app_context():
        db = LifeLogServer.database.get_db()
        initial_value = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        if not id_exists:
            assert(len(initial_value) == 0)
        else:
            assert(len(initial_value) == 1)
            initial_value = initial_value[0]

        db = LifeLogServer.database.get_db()
        sParams = urllib.parse.urlencode(params)
        response = client.put(ENTRY_URL + f'/{entry_id}?{sParams}', headers=auth_tests.AUTH_HEADERS)


        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()

        if expected_error is not None:
            assert(response.status_code == expected_error)
            if not id_exists:
                return

            assert(len(results) == 1)
            row=results[0]

            assert(row['weight_kg'] == initial_value['weight_kg'])
            assert(row['datetime'] == initial_value['datetime'])
            return


        assert response.status_code == HTTPStatus.NO_CONTENT

        assert(len(results) == 1)
        row = results[0]

        if 'weight' in params.keys():
            assert(row['weight_kg'] == weight_kg)
        else:
            assert(row['weight_kg'] == initial_value['weight_kg'])
        if 'datetime' in params.keys():
            assert(row['datetime'] == datetime)
        else:
            assert(row['datetime'] == initial_value['datetime'])

@pytest.mark.unit
@pytest.mark.parametrize("input_value, input_unit, expected, max_error", [
    (100.0,   "kilograms", 100.0,    None),
    (100.0,   "pounds",    45.35924, 0.01),
    (100.0,   "pM8FqiQn",  None,     None),
    (100,     "kilograms", None,     None),
    ("foo",   "kilograms", None,     None),
    ("100.0", "kilograms", None,     None),
    ("100",   "kilograms", None,     None),
])
def test_kg_from_unsafe(input_value, input_unit, expected, max_error):
    actual=LifeLogServer.weight.kg_from_unsafe(input_value, input_unit)
    if max_error is None:
        if(expected != actual):
            import pdb; pdb.set_trace()
            pass
    else:
        assert(abs(expected-actual) <= max_error)
