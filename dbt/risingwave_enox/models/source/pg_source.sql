-- Create a CDC Postgres source
-- Source can then get referenced and used to create a RW table

{{ config(materialized='source') }}
CREATE SOURCE IF NOT EXISTS {{ this }}
WITH (
  connector = 'postgres-cdc',
  hostname = 'postgres-0',
  port = '5432',
  username = 'postgres',
  password = '',
  database.name = 'postgres',
  schema.name = 'public'
)