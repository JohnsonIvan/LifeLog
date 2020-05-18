#This file is a fork of sample code from the Flask project, available here:
#https://web.archive.org/web/20200101161517/https://flask.palletsprojects.com/en/1.1.x/tutorial/tests/
#
#As per https://web.archive.org/web/20200101161535/https://flask.palletsprojects.com/en/1.1.x/license/
#that file is available under this license:
#
#Copyright 2010 Pallets
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#1: Redistributions of source code must retain the above copyright notice, this
#list of conditions and the following disclaimer.
#
#2: Redistributions in binary form must reproduce the above copyright notice,
#this list of conditions and the following disclaimer in the documentation
#and/or other materials provided with the distribution.
#
#3: Neither the name of the copyright holder nor the names of its contributors
#may be used to endorse or promote products derived from this software without
#specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import sqlite3

import pytest

from http import HTTPStatus


import LifeLogServer


def test_get_close_db(app):
    with app.app_context():
        db = LifeLogServer.database.get_db()
        assert db is LifeLogServer.database.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('LifeLogServer.database.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

def test_autocommitter(runner, monkeypatch):
    class FakeDB():
        foo = True
        committed = False
        def commit(self):
            self.committed = True

    fakeDB = FakeDB()

    def getFakeDB():
        return fakeDB

    monkeypatch.setattr('LifeLogServer.database.get_db', getFakeDB)

    @LifeLogServer.database.get_autocommit_db()
    def fun1(arg1, arg2, /, arg3, arg4, *, db, arg5=5, arg6, code):
        assert arg1 == 1
        assert arg2 == 2
        assert arg3 == 3
        assert arg4 == 4
        assert arg5 == 5
        assert arg6 == 6
        assert db is fakeDB
        assert not db.committed
        return ("yolo", code)

    fun1(1, 2, 3, arg5=5, arg6=6, arg4=4, code=HTTPStatus.OK)
    assert fakeDB.committed
    fakeDB.committed = False
    fun1(1, 2, 3, arg5=5, arg6=6, arg4=4, code=HTTPStatus.BAD_REQUEST) # arbitrary code != OK
    assert not fakeDB.committed
