import time
import urllib
from http import HTTPStatus

import LifeLogServer


import auth_tests
import test_db
import pytest

WEIGHT_URL='/api/v1/weight'

GET_URL=f'{WEIGHT_URL}/get'
GET_HAPPY_PARAMS={'since':150, 'before':450, 'limit':1, 'offset':1}
GET_HAPPY_RESULTS=b'300, 300.0\n'

GET_ALL_SINCE=0
GET_ALL_BEFORE=1000
GET_ALL_COUNT=5
GET_ALL_PARAMS={'since':GET_ALL_SINCE, 'before':GET_ALL_BEFORE, 'limit':2*GET_ALL_COUNT+100, 'offset':0}

RECORD_URL=f'{WEIGHT_URL}/record'

@pytest.mark.unit
def test_get_happy(client):
    params = urllib.parse.urlencode(GET_HAPPY_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.charset == 'utf-8'
    assert response.mimetype == 'text/csv'
    assert response.data == GET_HAPPY_RESULTS

@pytest.mark.unit
def test_get_missingParam(client):
    for key in ['since', 'before', 'limit', 'offset']:
        params = GET_HAPPY_PARAMS.copy()
        params.pop(key, None)
        params = urllib.parse.urlencode(params)
        url = GET_URL + '?' + params
        response = client.get(url, headers=auth_tests.AUTH_HEADERS)
        status = response.status_code
        assert status == HTTPStatus.BAD_REQUEST, f'key = "{key}"; url = "{url}"; status = {status}'

@pytest.mark.integration
def test_get_auth(client):
    params = urllib.parse.urlencode(GET_HAPPY_PARAMS)
    url = GET_URL + '?' + params

    auth_tests.run_tests(client.get, url)


@pytest.mark.unit
def test_record_happy(client):
    params = urllib.parse.urlencode(GET_ALL_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 5


    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    response = client.post(RECORD_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == 200


    params = urllib.parse.urlencode(GET_ALL_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 6
    assert '450, 0.1' in results

@pytest.mark.unit
def test_record_invalid(client):
    param_arr = [{'weight': 0.1, 'datetime': 2000000000},
                 {'datetime': 0},
                 {'weight': 0.1},
                 {'weight': 'hello', 'datetime': 0},
                 {'weight': 0.1, 'datetime': 'hello'}]
    for params in param_arr:
        params = urllib.parse.urlencode(params)
        response = client.post(RECORD_URL + '?' + params, headers=auth_tests.AUTH_HEADERS)
        assert response.status_code == 400

@pytest.mark.integration
def test_record_auth(client):
    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    url = RECORD_URL + '?' + params

    auth_tests.run_tests(client.post, url)

@pytest.mark.integration
def test_record_commits(client, monkeypatch):
    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    url = RECORD_URL + '?' + params

    test_db.count_commits(client.post, url, monkeypatch, expected_cc=1, headers=auth_tests.AUTH_HEADERS)

    def fakeTime():
        raise Exception("asdf")

    monkeypatch.setattr('time.time', fakeTime)
    test_db.count_commits(client.post, url, monkeypatch, expected_cc=0, headers=auth_tests.AUTH_HEADERS, expected_exception=Exception)
