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
@pytest.mark.parametrize("ret_format", [
    ("csv",),
    (None,),
])
def test_get_happy(client, ret_format):
    params = BATCH_GET_HAPPY_PARAMS.copy()
    if ret_format is not None:
        params['format'] = "csv"
    params = urllib.parse.urlencode(params)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.charset == 'utf-8'
    assert response.mimetype == 'text/csv'
    assert fuzzy_equals(BATCH_GET_HAPPY_RESULTS, parse_csv(response.data))

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
def test_record_happy(client):
    params = urllib.parse.urlencode(BATCH_GET_ALL_PARAMS)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 5


    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    response = client.post(ENTRY_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.CREATED


    params = urllib.parse.urlencode(BATCH_GET_ALL_PARAMS)
    response = client.get(BATCH_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    data = parse_csv(response.data)
    assert len(data) == 6
    list_truths = list(map(lambda x: fuzzy_equals([None, "450", '0.1'], x), data))
    assert(list_truths.count(True) == 1)

@pytest.mark.unit
def test_record_invalid(client):
    data = [
        (HTTPStatus.UNPROCESSABLE_ENTITY, {'weight': 0.1, 'datetime': 2000000000}),
        (HTTPStatus.BAD_REQUEST,          {'datetime': 0}),
        (HTTPStatus.BAD_REQUEST,          {'weight': 0.1}),
        (HTTPStatus.BAD_REQUEST,          {'weight': 'hello', 'datetime': 0}),
        (HTTPStatus.BAD_REQUEST,          {'weight': 0.1, 'datetime': 'hello'})
    ]
    for (expected_code, params) in data:
        params = urllib.parse.urlencode(params)
        response = client.post(ENTRY_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == expected_code

@pytest.mark.integration
def test_record_auth(client):
    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    url = ENTRY_URL + '?' + params

    auth_tests.run_tests(client.post, url, expected_status=HTTPStatus.CREATED)

@pytest.mark.integration
def test_record_commits(client, monkeypatch):
    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    url = ENTRY_URL + '?' + params

    test_db.count_commits(client.post, url, monkeypatch, expected_cc=1, headers=auth_tests.AUTH_HEADERS, expected_status=HTTPStatus.CREATED)

    def fakeTime():
        raise Exception("asdf")

    monkeypatch.setattr('time.time', fakeTime)
    test_db.count_commits(client.post, url, monkeypatch, expected_cc=0, headers=auth_tests.AUTH_HEADERS, expected_exception=Exception)

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
@pytest.mark.parametrize("entry_id,params", [
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", {'datetime':1592435016, 'weight':123.45}),
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", {                       'weight':123.45}),
    ("148064f1-48bc-415d-9ff8-8a57d7ad8687", {'datetime':1592435016,                }),
])
def test_entry_update_happy(app, client, entry_id, params):
    with app.app_context():
        db = LifeLogServer.database.get_db()
        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 1)

        db = LifeLogServer.database.get_db()
        sParams = urllib.parse.urlencode(params)
        response = client.put(ENTRY_URL + f'/{entry_id}?{sParams}', headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == HTTPStatus.NO_CONTENT

        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 1)
        row = results[0]

        for key in params.keys():
            assert(params[key] == row[key])

@pytest.mark.unit
def test_entry_update_no_params(app, client):
    entry_id = '148064f1-48bc-415d-9ff8-8a57d7ad8687'
    with app.app_context():
        db = LifeLogServer.database.get_db()
        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 1)

        db = LifeLogServer.database.get_db()
        sParams = urllib.parse.urlencode({})
        response = client.put(ENTRY_URL + f'/{entry_id}?{sParams}', headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.unit
def test_entry_update_nonexistant(app, client):
    entry_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    with app.app_context():
        db = LifeLogServer.database.get_db()
        results = db.execute('SELECT * FROM weight WHERE userid=? AND id=?', (auth_tests.AUTH_USERID, entry_id)).fetchall()
        assert(len(results) == 0)

        db = LifeLogServer.database.get_db()
        sParams = urllib.parse.urlencode({'datetime':1592435016, 'weight':123.45})
        response = client.put(ENTRY_URL + f'/{entry_id}?{sParams}', headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
