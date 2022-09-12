import sqlite3

import pytest

from http import HTTPStatus

import flask
import LifeLogServer
import random
import uuid

_count = 0
@LifeLogServer.cache.cache
def _foo():
    global _count
    _count += 1
    return "foo"

_rd = random.Random()
_rd.seed(0)
_default_headers = {LifeLogServer.auth.AUTH_HEADER: 'asdf'}

def _new_uuid_str():
    return str(uuid.UUID(int=_rd.getrandbits(128)))


def _simple_test(app, headers):
    initial = _count
    with app.test_request_context(headers=headers):
        _foo()
        assert _count == initial + 1
        _foo()
        _foo()
        assert _count == initial + 1

@pytest.mark.unit
def test_authenticated(app):
    headers = _default_headers.copy()

    headers[LifeLogServer.cache.CACHE_HEADER] = _new_uuid_str()
    _simple_test(app, headers)

@pytest.mark.unit
def test_bad_cacheid(app):
    headers = _default_headers.copy()

    headers[LifeLogServer.cache.CACHE_HEADER] = _new_uuid_str() + 'a'

    with app.test_request_context(headers=headers):
        ret = _foo()
        status_code = flask.make_response(ret).status_code
        assert(status_code == HTTPStatus.BAD_REQUEST)

@pytest.mark.unit
def test_noncaching(app):
    headers = _default_headers.copy()
    if LifeLogServer.cache.CACHE_HEADER in headers:
        del headers[LifeLogServer.cache.CACHE_HEADER]

    initial = _count
    with app.test_request_context(headers=headers):
        _foo()
        assert _count == initial + 1
        _foo()
        assert _count == initial + 2
        _foo()
        assert _count == initial + 3

@pytest.mark.unit
def test_multi_request(app):
    headers = _default_headers.copy()

    uuid1 = _new_uuid_str()
    uuid2 = _new_uuid_str()
    with app.app_context():
        headers[LifeLogServer.cache.CACHE_HEADER] = uuid1
        _simple_test(app, headers)

        headers[LifeLogServer.cache.CACHE_HEADER] = uuid2
        _simple_test(app, headers)

        count = _count

        headers[LifeLogServer.cache.CACHE_HEADER] = uuid1
        with app.test_request_context(headers=headers):
            _foo()
            assert _count == count

        headers[LifeLogServer.cache.CACHE_HEADER] = uuid2
        with app.test_request_context(headers=headers):
            _foo()
            assert _count == count
