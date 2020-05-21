import sqlite3

import pytest

from http import HTTPStatus

import flask
import LifeLogServer
import uuid

@pytest.mark.unit
def test_cache(app, monkeypatch):
    count = 0
    @LifeLogServer.cache.cache
    def foo():
        nonlocal count
        count += 1
        return "foo"

    args = {}
    args['cacheid'] = 'b6a003f7-bf11-4e9c-825a-9e4c5241a740'
    with app.test_request_context(query_string=args):
        foo()
        assert count == 1
        foo()
        foo()
        assert count == 1

    args['cacheid'] = '10279e15-2fc9-4bff-b1a1-1b978fe7e7f8'
    with app.test_request_context(query_string=args):
        foo()
        assert count == 2
        foo()
        foo()
        assert count == 2
