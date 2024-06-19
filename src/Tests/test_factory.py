# This file is a fork of sample code from the Flask project, available here:
# https://web.archive.org/web/20200101161517/https://flask.palletsprojects.com/en/1.1.x/tutorial/tests/
#
# As per https://web.archive.org/web/20200101161535/https://flask.palletsprojects.com/en/1.1.x/license/
# that file is available under this license:
#
# Copyright 2010 Pallets
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1: Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2: Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3: Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import LifeLogServer

import pkg_resources
import pytest

import conftest
import tempfile


@pytest.mark.unit
def test_default_key():
    db_fd, db_path = tempfile.mkstemp()
    with pytest.raises(LifeLogServer.DefaultKeyException):
        app = LifeLogServer.create_app(
            config_file="/dev/null",
            database_file=db_path,
        )


@pytest.mark.unit
def test_testing():
    db_fd, db_path = tempfile.mkstemp()
    app = LifeLogServer.create_app(
        config_file=conftest.DEFAULT_CONFIG_FILE,
        database_file=db_path,
    )
    assert app.testing


@pytest.mark.unit
def test_ping(client):
    response = client.get("/api/v1/ping")
    assert response.data == b"pong\n"


@pytest.mark.unit
def test_apiv(client):
    response = client.get("/api_version")
    assert response.data == bytes(
        pkg_resources.require("LifeLogServer")[0].version, encoding="utf-8"
    )
