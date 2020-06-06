DROP TABLE IF EXISTS weight;
CREATE TABLE weight (
  id INTEGER AUTOINCREMENT,
  datetime INTEGER,
  weight REAL,
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS auth_token;
CREATE TABLE auth_token (
  id INTEGER,
  token TEXT UNIQUE,
  PRIMARY KEY (id)
);


DROP TABLE IF EXISTS cache;
CREATE TABLE cache (
  uuid TEXT,
  token TEXT,
  request_time INTEGER,
  response BLOB,
  PRIMARY KEY (uuid)
)
