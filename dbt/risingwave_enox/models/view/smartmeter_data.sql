{{ config(materialized='materialized_view') }}
SELECT 
  msg_key,
  msg_timestamp,
  "readingFrom"
FROM {{ ref('smartmeter_readings_stream_kafka')}}