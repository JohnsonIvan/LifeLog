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

@pytest.mark.unit
def test_authenticated(app):
    headers = _default_headers.copy()

    headers[LifeLogServer.cache.CACHE_HEADER] = 'b6a003f7-bf11-4e9c-825a-9e4c5241a740'
    _simple_test(app, headers)

@pytest.mark.unit
def test_unauthenticated(app):
    headers = _default_headers.copy()
    del headers[LifeLogServer.auth.AUTH_HEADER]
    headers[LifeLogServer.cache.CACHE_HEADER] = '10279e15-2fc9-4bff-b1a1-1b978fe7e7f8'
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

#TODO: SHOW IT CACHES MORE THAN THE MOST RECENT QUERY
