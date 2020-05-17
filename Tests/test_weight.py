import time
import urllib
from http import HTTPStatus

import LifeLogServer

AUTH_HEADER='token'
AUTH_TOKEN='test-key'
AUTH_TOKEN_BAD=AUTH_TOKEN+'oiawejklfxcvkjlweeeoisdvwe'
DEFAULT_HEADERS={AUTH_HEADER:AUTH_TOKEN}

GET_URL='/api/v1/weight/get'
GET_HAPPY_PARAMS={'since':150, 'before':450, 'limit':1, 'offset':1}
GET_HAPPY_RESULTS=b'300, 300.0\n'

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
    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0', headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 5

    response = client.post('/api/v1/weight/record?weight=0.1&datetime=450', headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    assert response.charset == 'utf-8'

    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0', headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    results = response.data.decode(response.charset, "strict").rstrip().split('\n')
    assert len(results) == 6
    assert '450, 0.1' in results

def test_record_future(client):
    response = client.post(f'/api/v1/weight/record?weight=0.1&datetime=2000000000', headers=DEFAULT_HEADERS)
    assert response.status_code == 400
def test_record_missing_weight(client):
    response = client.post(f'/api/v1/weight/record?datetime=0', headers=DEFAULT_HEADERS)
    assert response.status_code == 400
def test_record_missing_date(client):
    response = client.post(f'/api/v1/weight/record?weight=0.1', headers=DEFAULT_HEADERS)
    assert response.status_code == 400

def test_record_invalid_weight(client):
    response = client.post('/api/v1/weight/record?weight=hello&datetime=456', headers=DEFAULT_HEADERS)
    assert response.status_code == 400
def test_record_invalid_date(client):
    response = client.post('/api/v1/weight/record?weight=1&datetime=hello', headers=DEFAULT_HEADERS)
    assert response.status_code == 400
