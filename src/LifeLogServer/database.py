#This file is a fork of sample code from the Flask project, available here:
#https://web.archive.org/web/20200101161533/https://flask.palletsprojects.com/en/1.1.x/tutorial/database/
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

import click
import flask as f
import functools
import LifeLogServer
import packaging.version

from http import HTTPStatus

def get_db(new_connection=False):
    """Connect to the application's configured database. With the default value
    `new_connection==False` the connection is unique for each request and will
    be reused if this is called again.

    This might timeout with an exception if multiple simultaneous connections
    are made. This is generally only a concern if `new_connection` is set to
    true.
    """
    if new_connection:
        db = sqlite3.connect(
            f.current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        return db
    if "db" not in f.g:
        f.g.db = get_db(new_connection=True)

        do_migrations()
    return f.g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = f.g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    """Clear existing data and create new tables."""
    with get_db(new_connection=True) as db:
        with f.current_app.open_resource("schema.sql") as file:
            db.executescript(file.read().decode("utf8"))
            db.execute('INSERT INTO database (versionno) VALUES (?);', (LifeLogServer.API_VERSION,))

def get_db_version():
    db = get_db()

    results = db.execute('SELECT * FROM database').fetchall()
    assert(len(results) == 1)
    result = results[0]

    return result['versionno']

def autocommit_db(func=None, /):
    AUTH_HEADER="token"
    if not func:
        return functools.partial(autocommit_db)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        status_code = f.make_response(ret).status_code

        if status_code < 400 or 600 <= status_code: #if not error
            db = get_db()
            db.commit()

        return ret
    return wrapper

@click.command("init-db")
@f.cli.with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")

__migrations = {}

def __get_migration_name(vBefore, vAfter):
    return f'{vBefore}_mpatxbxgtpamxpapg_{vAfter}'

def migration(vBefore, vAfter):
    def decorator(func, /):
        name = __get_migration_name(vBefore, vAfter)
        assert(name not in __migrations)
        __migrations[name] = func
        return func
    return decorator

# this import statement adds migrations to `__migrations` via the `migration` decorator
from . import database_migrations

def do_migrations():
    db_version = packaging.version.parse(get_db_version())
    cur_version = packaging.version.parse(LifeLogServer.API_VERSION)

    if db_version > cur_version:
        raise Exception(f"Database schema version is newer than the running code version ({db_version}, {cur_version})")
    if db_version == cur_version:
        return

    assert(db_version < cur_version)
    name = __get_migration_name(db_version, cur_version)
    if name not in __migrations:
        raise Exception(f"The code version ({cur_version}) is newer than the database version ({db_version}), and there is no known method for migrating the database directly.")
    func = __migrations[name]
    db = get_db()
    func(db)
    db.execute('UPDATE database SET versionno = ?', (str(cur_version),))

    new_db_version = packaging.version.parse(get_db_version())
    assert(new_db_version == cur_version)

def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
