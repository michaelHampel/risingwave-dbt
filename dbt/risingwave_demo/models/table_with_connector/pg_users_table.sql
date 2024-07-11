-- Create a table to read CDC data from Postgres
-- Any updates made to the users table in PostgreSQL will automatically be reflected in the pg_users_table in RisingWave.

{{ config(materialized='table_with_connector') }}
CREATE TABLE IF NOT EXISTS {{ this }} (
  id INTEGER primary key,
  first_name VARCHAR,
  last_name VARCHAR,
  age INTEGER
) WITH (
  connector = 'postgres-cdc',
  hostname = 'postgres-0',
  port = '5432',
  username = 'postgres',
  password = '',
  database.name = 'postgres',
  schema.name = 'public',
  table.name = 'users' 
)