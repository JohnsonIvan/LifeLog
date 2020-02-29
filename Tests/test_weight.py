import time

import LifeLogServer


def test_get_happy(client):
    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0')
    assert response.status_code == 200
    assert response.charset == 'utf-8'
    assert response.mimetype == 'text/csv'
    assert response.data == b'123, 80.0\n'

def test_get_badSince(client):
    response = client.get('/api/v1/weight/get?before=2000000000&limit=3000&offset=0')
    assert response.status_code == 400
def test_get_badBefore(client):
    response = client.get('/api/v1/weight/get?since=0&limit=3000&offset=0')
    assert response.status_code == 400
def test_get_badLimit(client):
    response = client.get('/api/v1/weight/get?since=0&before=2000000000&offset=0')
    assert response.status_code == 400
def test_get_badOffset(client):
    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000')
    assert response.status_code == 400


def test_record_happy(client):
    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0')
    assert response.status_code == 200

    response = client.post('/api/v1/weight/record?weight=0.1&datetime=456')
    assert response.status_code == 200
    assert response.charset == 'utf-8'

    response = client.get('/api/v1/weight/get?since=0&before=2000000000&limit=3000&offset=0')
    assert response.status_code == 200
    assert response.data.decode(response.charset, "strict").count('\n') == 2

def test_record_future(client):
    response = client.post(f'/api/v1/weight/record?weight=0.1&datetime=2000000000')
    assert response.status_code == 400
def test_record_missing_weight(client):
    response = client.post(f'/api/v1/weight/record?datetime=0')
    assert response.status_code == 400
def test_record_missing_date(client):
    response = client.post(f'/api/v1/weight/record?weight=0.1')
    assert response.status_code == 400

def test_record_invalid_weight(client):
    response = client.post('/api/v1/weight/record?weight=hello&datetime=456')
    assert response.status_code == 400
def test_record_invalid_date(client):
    response = client.post('/api/v1/weight/record?weight=1&datetime=hello')
    assert response.status_code == 400
