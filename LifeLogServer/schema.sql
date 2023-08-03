CREATE TABLE database (
  versionno TEXT NOT NULL
);



CREATE TABLE users (
  userid TEXT NOT NULL,
  PRIMARY KEY (userid)
);

CREATE TABLE tokens (
  token TEXT NOT NULL,
  userid TEXT NOT NULL,
  description TEXT,
  FOREIGN KEY(userid) REFERENCES users(userid),
  PRIMARY KEY(token)
);

CREATE TABLE token_perms (
  token TEXT NOT NULL,
  permission TEXT NOT NULL,
  PRIMARY KEY (token, permission)
);



CREATE TABLE cache (
  uuid TEXT NOT NULL,
  token TEXT NOT NULL,
  request_time INTEGER NOT NULL,
  response BLOB NOT NULL,
  FOREIGN KEY(token) REFERENCES tokens(token),
  PRIMARY KEY (uuid, token)
);



CREATE TABLE weight (
  id TEXT NOT NULL,
  userid TEXT NOT NULL,
  datetime INTEGER NOT NULL,
  weight_kg REAL NOT NULL,
  FOREIGN KEY(userid) REFERENCES users(userid),
  PRIMARY KEY (id)
);
