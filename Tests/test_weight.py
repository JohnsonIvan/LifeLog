import time
import urllib
from http import HTTPStatus

import LifeLogServer

AUTH_HEADER='token'
AUTH_TOKEN='test-key'
AUTH_TOKEN_BAD=AUTH_TOKEN+'oiawejklfxcvkjlweeeoisdvwe'
DEFAULT_HEADERS={AUTH_HEADER:AUTH_TOKEN}

WEIGHT_URL='/api/v1/weight'

GET_URL=f'{WEIGHT_URL}/get'
GET_HAPPY_PARAMS={'since':150, 'before':450, 'limit':1, 'offset':1}
GET_HAPPY_RESULTS=b'300, 300.0\n'

GET_ALL_SINCE=0
GET_ALL_BEFORE=1000
GET_ALL_COUNT=5
GET_ALL_PARAMS={'since':GET_ALL_SINCE, 'before':GET_ALL_BEFORE, 'limit':2*GET_ALL_COUNT+100, 'offset':0}

RECORD_URL=f'{WEIGHT_URL}/record'

def test_get_happy(client):
    params = urllib.parse.urlencode(GET_HAPPY_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=DEFAULT_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.charset == 'utf-8'
    assert response.mimetype == 'text/csv'
    assert response.data == GET_HAPPY_RESULTS

def test_get_missingParam(client):
    for key in ['since', 'before', 'limit', 'offset']:
        params = GET_HAPPY_PARAMS.copy()
        params.pop(key, None)
        params = urllib.parse.urlencode(params)
        url = GET_URL + '?' + params
        response = client.get(url, headers=DEFAULT_HEADERS)
        status = response.status_code
        assert status == HTTPStatus.BAD_REQUEST, f'key = "{key}"; url = "{url}"; status = {status}'

def test_get_auth(client):
    params = urllib.parse.urlencode(GET_HAPPY_PARAMS)
    url = GET_URL + '?' + params


    response = client.get(url, headers=DEFAULT_HEADERS)
    assert response.status_code == HTTPStatus.OK

    headers = DEFAULT_HEADERS.copy()
    headers.pop(AUTH_HEADER, None)
    response = client.get(url, headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    headers = DEFAULT_HEADERS.copy()
    headers[AUTH_HEADER] = AUTH_TOKEN_BAD
    response = client.get(url, headers=headers)
    assert response.status_code == HTTPStatus.FORBIDDEN

def test_record_happy(client):
    params = urllib.parse.urlencode(GET_ALL_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 5


    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    response = client.post(RECORD_URL + '?' + params, headers=DEFAULT_HEADERS)
    assert response.status_code == 200


    params = urllib.parse.urlencode(GET_ALL_PARAMS)
    response = client.get(GET_URL + '?' + params, headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 6
    assert '450, 0.1' in results

def test_record_invalid(client):
    param_arr = [{'weight': 0.1, 'datetime': 2000000000},
                 {'datetime': 0},
                 {'weight': 0.1},
                 {'weight': 'hello', 'datetime': 0},
                 {'weight': 0.1, 'datetime': 'hello'}]
    for params in param_arr:
        params = urllib.parse.urlencode(params)
        response = client.post(RECORD_URL + '?' + params, headers=DEFAULT_HEADERS)
        assert response.status_code == 400

def test_record_auth(client):
    params = urllib.parse.urlencode({'weight':0.1, 'datetime':450})
    url = RECORD_URL + '?' + params


    response = client.post(url, headers=DEFAULT_HEADERS)
    assert response.status_code == HTTPStatus.OK

    headers = DEFAULT_HEADERS.copy()
    headers.pop(AUTH_HEADER, None)
    response = client.post(url, headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    headers = DEFAULT_HEADERS.copy()
    headers[AUTH_HEADER] = AUTH_TOKEN_BAD
    response = client.post(url, headers=headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
