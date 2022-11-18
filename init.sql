CREATE EXTENSION IF NOT EXISTS 'uuid-ossp';

CREATE TABLE [IF NOT EXISTS] user (
  id uuid DEFAULT uuid_generate_v4(),
  name VARCHAR(255)
)

CREATE TABLE [IF NOT EXISTS] asset
