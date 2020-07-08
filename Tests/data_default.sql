INSERT INTO users (userid) VALUES ("cf1f8a6d-c3de-4987-9478-ed14fff7fe33");
INSERT INTO tokens (token, userid, description) VALUES ("test-key-1", "cf1f8a6d-c3de-4987-9478-ed14fff7fe33", "Ultimate token for user 1");
INSERT INTO token_perms (token, permission) VALUES ("test-key-1", "ultimate");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("39dff980-265b-4d27-8e0e-d7c1f8dfc254", 100, 111, "cf1f8a6d-c3de-4987-9478-ed14fff7fe33");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("9319a4e7-44ad-4008-8178-2c3f29f1501a", 200, 222, "cf1f8a6d-c3de-4987-9478-ed14fff7fe33");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("148064f1-48bc-415d-9ff8-8a57d7ad8687", 300, 333, "cf1f8a6d-c3de-4987-9478-ed14fff7fe33");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("689a747f-555d-4306-99b7-fceb649f929e", 400, 444, "cf1f8a6d-c3de-4987-9478-ed14fff7fe33");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("ed58697b-2704-41eb-80b6-98982e33a079", 500, 555, "cf1f8a6d-c3de-4987-9478-ed14fff7fe33");


INSERT INTO users (userid) VALUES ("32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");
INSERT INTO tokens (token, userid, description) VALUES ("test-key-2", "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38", "Ultimate token for user 2");
INSERT INTO token_perms (token, permission) VALUES ("test-key-2", "ultimate");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("71215e6a-1117-47ff-8cd3-0967b7cca70f", 100, 111, "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("76af87ed-3268-466c-82c2-578d6ec6b530", 200, 222, "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("89b11f90-e74b-426e-8ee6-56c0ce5b1291", 300, 333, "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("e08867b9-4d9a-4ee8-8f61-d19002989398", 400, 444, "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");
INSERT INTO weight (id, datetime, weight_kg, userid) VALUES ("943baa5b-b0db-487a-b3a0-8291cd24df7e", 500, 555, "32e6f3bd-f9ca-48db-8ee4-dc1fd1dc4f38");


INSERT INTO users (userid) VALUES ("4d970c06-359a-4440-aec3-899a8a472319");
INSERT INTO tokens (token, userid, description) VALUES ("test-key-auth-ult", "4d970c06-359a-4440-aec3-899a8a472319", "Ultimate token for the auth test user");
INSERT INTO token_perms (token, permission) VALUES ("test-key-auth-ult", "ultimate");
INSERT INTO tokens (token, userid, description) VALUES ("test-key-auth-a", "4d970c06-359a-4440-aec3-899a8a472319", "Token for the auth test user; has perm a");
INSERT INTO token_perms (token, permission) VALUES ("test-key-auth-a", "a");
INSERT INTO tokens (token, userid, description) VALUES ("test-key-auth-b", "4d970c06-359a-4440-aec3-899a8a472319", "Token for the auth test user; has perm a");
INSERT INTO token_perms (token, permission) VALUES ("test-key-auth-b", "b");
