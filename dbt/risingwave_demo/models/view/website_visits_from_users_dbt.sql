-- The following SQL creates a materialized view which joins the data from the Kafka topic and 
-- the PostgreSQL table by the user ID.

{{ config(materialized='materialized_view') }}
SELECT  
  timestamp, 
  user_id,
  last_name AS user_name,
  age AS user_age,
  page_id,
  action
FROM 
  {{ ref('kafka_website_visits_stream')}} K INNER JOIN {{ ref('pg_users_table')}} P on K.user_id = P.id
