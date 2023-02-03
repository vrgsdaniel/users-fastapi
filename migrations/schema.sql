CREATE SCHEMA IF NOT EXISTS users;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE users.user_type AS ENUM ('ADMIN', 'CUSTOMER');

CREATE TABLE users.users (
    id uuid DEFAULT uuid_generate_v4() primary key,
    passhash varchar not null,
    email varchar(64) not null unique,
    user_type users.user_type default 'CUSTOMER',
    created_at timestamp default now(),
    updated_at timestamp
);
