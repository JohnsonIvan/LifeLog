from http import HTTPStatus
import flask
import pytest

import LifeLogServer

import auth_tests


@pytest.mark.unit
@pytest.mark.parametrize(
    "token, req_permissions, response_code",
    [
        ("test-key-auth-a", ["a"], HTTPStatus.OK),
        ("test-key-auth-a", ["b"], HTTPStatus.FORBIDDEN),
        ("test-key-auth-a", ["c"], HTTPStatus.FORBIDDEN),
        ("test-key-auth-a", ["a", "b"], HTTPStatus.FORBIDDEN),
        ("test-key-auth-b", ["b"], HTTPStatus.OK),
        ("test-key-auth-ult", ["a", "b", "c"], HTTPStatus.OK),
        (None, ["a"], HTTPStatus.UNAUTHORIZED),
    ],
)
def test_simple(app, token, req_permissions, response_code):
    if token is None:
        headers = {}
    else:
        headers = {auth_tests.AUTH_HEADER: token}

    with app.test_request_context(headers=headers):

        @LifeLogServer.auth.requireAuth(permissions=req_permissions)
        def foo(userid):
            assert userid == "4d970c06-359a-4440-aec3-899a8a472319"
            return f"", HTTPStatus.OK

        response = flask.make_response(foo())
        assert response.status_code == response_code
