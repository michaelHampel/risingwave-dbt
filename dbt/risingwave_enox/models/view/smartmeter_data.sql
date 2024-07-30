{{ config(materialized='materialized_view') }}
SELECT 
  "readingFrom"
FROM {{ ref('smartmeter_readings_stream_kafka')}}