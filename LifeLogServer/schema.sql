CREATE TABLE database (
  versionno TEXT NOT NULL
);

CREATE TABLE weight (
  id TEXT,
  userid TEXT NOT NULL,
  datetime INTEGER,
  weight_kg REAL,
  FOREIGN KEY(userid) REFERENCES users(userid),
  PRIMARY KEY (id)
);

CREATE TABLE users (
  userid TEXT,
  PRIMARY KEY (userid)
);

CREATE TABLE tokens (
  token TEXT,
  userid TEXT,
  description TEXT,
  FOREIGN KEY(userid) REFERENCES users(userid),
  PRIMARY KEY(token)
);

CREATE TABLE token_perms (
  token TEXT,
  permission TEXT,
  PRIMARY KEY (token, permission)
);

CREATE TABLE cache (
  uuid TEXT,
  token TEXT,
  request_time INTEGER,
  response BLOB,
  FOREIGN KEY(token) REFERENCES tokens(token),
  PRIMARY KEY (uuid)
);
