import sqlite3

import pytest

from http import HTTPStatus

import flask
import LifeLogServer
import uuid


_count = 0
@LifeLogServer.cache.cache
def _foo():
    global _count
    _count += 1
    return "foo"

_default_headers = {LifeLogServer.auth.AUTH_HEADER: 'asdf'}

def _simple_test(app, headers):
    initial = _count
    with app.test_request_context(headers=headers):
        _foo()
        assert _count == initial + 1
        _foo()
        _foo()
        assert _count == initial + 1

__uuid_1 = 'b6a003f7-bf11-4e9c-825a-9e4c5241a740'
__uuid_2 = '10279e15-2fc9-4bff-b1a1-1b978fe7e7f8'

@pytest.mark.unit
def test_authenticated(app):
    headers = _default_headers.copy()

    headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_1
    _simple_test(app, headers)

@pytest.mark.unit
def test_bad_cacheid(app):
    headers = _default_headers.copy()

    headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_1+'a'

    with app.test_request_context(headers=headers):
        ret = _foo()
        status_code = flask.make_response(ret).status_code
        assert(status_code == HTTPStatus.BAD_REQUEST)

@pytest.mark.unit
def test_unauthenticated(app):
    headers = _default_headers.copy()
    del headers[LifeLogServer.auth.AUTH_HEADER]
    headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_1
    _simple_test(app, headers)

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

    with app.app_context():
        headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_1
        _simple_test(app, headers)

        headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_2
        _simple_test(app, headers)

        count = _count

        headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_1
        with app.test_request_context(headers=headers):
            _foo()
            assert _count == count

        headers[LifeLogServer.cache.CACHE_HEADER] = __uuid_2
        with app.test_request_context(headers=headers):
            _foo()
            assert _count == count
