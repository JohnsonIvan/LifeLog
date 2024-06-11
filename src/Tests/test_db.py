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


@pytest.mark.unit
def test_get_close_db(app):
    with app.app_context():
        db = LifeLogServer.database.get_db()
        assert db is LifeLogServer.database.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

@pytest.mark.unit
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('LifeLogServer.database.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

@pytest.mark.unit
@pytest.mark.parametrize("vOld,migration_vOld,expected_exception", [
    ('0.0.0', '0.0.0', None),
    ('0.0.1', '0.0.2', Exception),
    ('1000!0.0.0', '0.0.3', Exception),
])
def test_migration_system(app, vOld, migration_vOld, expected_exception):
    vNew=LifeLogServer.API_VERSION

    migration_call_count = 0

    with app.app_context():
        @LifeLogServer.database.migration(migration_vOld, vNew)
        def tmp_migration(db):
            nonlocal migration_call_count
            migration_call_count += 1

        conn = LifeLogServer.database.get_db(new_connection=True)
        conn.execute('UPDATE database SET versionno=?', (vOld,))
        conn.commit()

        #trigger the migration
        caught = False
        try:
            LifeLogServer.database.get_db()
        except expected_exception:
            caught = True
        if expected_exception is not None:
            if not caught:
                raise Exception("Did not receive the expected exception")
            return

        assert(migration_call_count == 1)

        db = LifeLogServer.database.get_db()
        results = db.execute('SELECT * FROM database').fetchall()
        assert(len(results) == 1)
        result = results[0]
        assert(result['versionno'] == vNew)


def count_commits(app, method, url, monkeypatch, expected_cc, headers={}, expected_exception=None, expected_status=HTTPStatus.OK):
    realGetDB = LifeLogServer.database.get_db
    commit_call_count = 0
    getdb_call_count = 0
    def fakeGetDB(new_connection=False):
        nonlocal getdb_call_count
        getdb_call_count = getdb_call_count+ 1
        if "ans" in fakeGetDB.__dict__:
            return fakeGetDB.ans

        db = realGetDB(new_connection=new_connection)
        def fakeCommit(*args, **kwargs):
            nonlocal commit_call_count
            commit_call_count = commit_call_count + 1
            return db.commit(*args, **kwargs)

        class FakeDB: # we can't just say db.commit = fakeCommit, because `commit` is read-only -_-
            def __getattribute__(self, name):
                if name == "commit":
                    return fakeCommit
                else:
                    return db.__getattribute__(name)
        fakeGetDB.ans = FakeDB()
        return fakeGetDB.ans

    with app.app_context():
        # Counter resets are necessary because get_db itself now makes commits on
        # the first get so that it can validate db versions
        fakeGetDB(new_connection=True)
    commit_call_count = 0
    getdb_call_count = 0

    monkeypatch.setattr('LifeLogServer.database.get_db', fakeGetDB)
    caught = False
    try:
        response = method(url, headers=headers)
        assert response.status_code == expected_status
    except expected_exception:
        caught = True
    if expected_exception is not None and not caught:
        raise Exception("Did not receive the expected exception")
    monkeypatch.setattr('LifeLogServer.database.get_db', realGetDB)


    assert commit_call_count == expected_cc

    del fakeGetDB.ans
