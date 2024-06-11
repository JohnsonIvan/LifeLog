import pytest

import LifeLogServer

@pytest.mark.unit
def test_weight_to_weightkg(app):
    with app.app_context():
        db = LifeLogServer.database.get_db()
        db.execute('DROP TABLE weight')
        db.execute('CREATE TABLE weight (id TEXT, userid TEXT NOT NULL, datetime INTEGER, weight REAL, PRIMARY KEY (id));')
        LifeLogServer.database_migrations.migrate_0_7_0a0_dev0_to_dev1(db)
        foo=db.execute('pragma table_info(\'weight\');').fetchall()
        assert(len(foo) == 4)
        assert(foo[0]['name'] == 'id')
        assert(foo[0]['type'] == 'TEXT')

        assert(foo[1]['name'] == 'userid')
        assert(foo[1]['type'] == 'TEXT')

        assert(foo[2]['name'] == 'datetime')
        assert(foo[2]['type'] == 'INTEGER')

        assert(foo[3]['name'] == 'weight_kg')
        assert(foo[3]['type'] == 'REAL')
