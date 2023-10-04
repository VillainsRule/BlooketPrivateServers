CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL,
  username TEXT not null,
  tokens NUMBER not null,
  banned TEXT not null,
  role TEXT not null,
);