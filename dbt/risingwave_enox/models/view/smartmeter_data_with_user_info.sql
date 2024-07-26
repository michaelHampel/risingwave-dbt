-- The following SQL creates a materialized view which joins the data from the Kafka topic and 
-- the PostgreSQL table by the owner ID.

{{ config(materialized='materialized_view') }}
SELECT  
  owner_id,
  device_id,
  smartmeter_mac,
  street,
  house_nr,
  town,
  post_code,
  country_code,
  current,
  energy,
  power,
  "readingFrom" as read_ts,
  "receivedAt" as received_ts,
  voltage
FROM 
  {{ ref('smartmeter_readings_stream_kafka')}} K INNER JOIN {{ ref('pg_enox_users_table')}} P on (K.owner).id = P.owner_id