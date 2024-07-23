-- Create a table to read CDC data from Postgres
-- Any updates made to the users table in PostgreSQL will automatically be reflected in the pg_users_table in RisingWave.

{{ config(materialized='table_with_connector') }}
CREATE TABLE IF NOT EXISTS {{ this }} (
  owner_id VARCHAR primary key,
  first_name VARCHAR,
  last_name VARCHAR,
  birth_date DATE,
  device_id VARCHAR,
  street VARCHAR,
  house_nr INT,
  town VARCHAR,
  post_code INT,
  country_code VARCHAR,
  registered_at timestamptz
) WITH (
  connector = 'postgres-cdc',
  hostname = 'postgres-0',
  port = '5432',
  username = 'postgres',
  password = '',
  database.name = 'postgres',
  schema.name = 'public',
  table.name = 'enox_users' 
)