import sqlite3

import pytest

from http import HTTPStatus

import flask
import LifeLogServer
import uuid


@pytest.mark.unit
def test_cache(app, monkeypatch):
    headers = {LifeLogServer.auth.AUTH_HEADER: 'asdf'}

    count = 0
    @LifeLogServer.cache.cache
    def foo():
        nonlocal count
        count += 1
        return "foo"

    headers[LifeLogServer.cache.CACHE_HEADER] = 'b6a003f7-bf11-4e9c-825a-9e4c5241a740'
    with app.test_request_context(headers=headers):
        foo()
        assert count == 1
        foo()
        foo()
        assert count == 1

    del headers[LifeLogServer.auth.AUTH_HEADER]
    headers[LifeLogServer.cache.CACHE_HEADER] = '10279e15-2fc9-4bff-b1a1-1b978fe7e7f8'
    with app.test_request_context(headers=headers):
        foo()
        assert count == 2
        foo()
        foo()
        assert count == 2

    #TODO: SPLIT INTO MULTIPLE TESTS
    #TODO: TEST W/O CACHEID
    #TODO: SHOW IT CACHES MORE THAN THE MOST RECENT QUERY
