DROP TABLE IF EXISTS weight;
CREATE TABLE weight (
  id TEXT,
  userid TEXT NOT NULL,
  datetime INTEGER,
  weight REAL,
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userid TEXT UNIQUE,
  token TEXT UNIQUE,
  PRIMARY KEY (userid, token)
);


DROP TABLE IF EXISTS cache;
CREATE TABLE cache (
  uuid TEXT,
  token TEXT,
  request_time INTEGER,
  response BLOB,
  PRIMARY KEY (uuid)
)
