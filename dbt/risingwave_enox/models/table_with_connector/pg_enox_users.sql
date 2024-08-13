-- Create RW table from Postgres CDC source
-- Use automatic schema mapping to ingest all columns from the source table
{{ config(materialized='table_with_connector') }} 
CREATE TABLE IF NOT EXISTS {{ this }} (*)
FROM {{ ref('pg_source')}} TABLE 'public.enox_users';