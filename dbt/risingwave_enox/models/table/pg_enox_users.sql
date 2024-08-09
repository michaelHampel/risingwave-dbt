{{ config(materialized='table_with_connector') }} 
CREATE TABLE IF NOT EXISTS {{ this }} (*)
FROM {{ ref('pg_source')}} TABLE 'public.enox_users';