from . import database

@database.migration('0.7.0a0.dev0', '0.7.0a0.dev1')
def migrate_0_7_0a0_dev0_to_dev1(db):
    print("RUNNING MIGRATION FOR 0.7.0a0.dev0 -> 0.7.0a0.dev1")
    db.execute('ALTER TABLE weight RENAME COLUMN weight to weight_kg')
