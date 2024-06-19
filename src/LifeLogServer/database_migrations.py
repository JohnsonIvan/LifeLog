from . import database

@database.migration("0.7.0", "0.7.2")
@database.migration("0.7.1", "0.7.2")
@database.migration("0.7.2", "0.8.0a0.dev0")
def migrate_noop(db):  # pragma: no cover
    pass


@database.migration("0.7.0a0.dev0", "0.7.0a0.dev1")
def migrate_0_7_0a0_dev0_to_dev1(db):
    print("RUNNING MIGRATION FOR 0.7.0a0.dev0 -> 0.7.0a0.dev1")
    db.execute("ALTER TABLE weight RENAME COLUMN weight to weight_kg")


# SQLite apparently doesn't support the addition of foreign key constraints to
# existing tables (https://stackoverflow.com/a/1884841), and there aren't enough
# users of v0.7.0a0.dev1 to justify working around this issue with SQL code. The
# recommended workaround is using the web API to fetch all your data,
# reinitialize the database in the dev2 configuration, and POST all the data
# back in.
#
# @database.migration('0.7.0a0.dev1', '0.7.0a0.dev2')
# def migrate_0_7_0a0_dev1_to_dev2(db):
#    pass


@database.migration("0.7.0a0.dev2", "0.7.0")
def migrate_0_7_0a0_dev2_to_0_7_0(db):  # pragma: no cover
    db.execute(
        "CREATE TABLE weight_goal (   userid TEXT NOT NULL,   datetime_start INTEGER NOT NULL,   weight_kg_start REAL NOT NULL,   weight_change_kg_per_year REAL NOT NULL,   FOREIGN KEY(userid) REFERENCES users(userid),   PRIMARY KEY (userid, datetime_start) )"
    )


@database.migration("0.7.0a0.dev2", "0.8.0a0.dev0")
def migrate_0_7_0a0_dev2_to_0_8_0a0_dev0(db):  # pragma: no cover
    migrate_0_7_0a0_dev2_to_0_7_0(db)
    # Updating from 0.7.0 -> 0.8.0a0.dev0 is a no-op
