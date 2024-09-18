{{ config(materialized='materialized_view') }}
SELECT 
  *
FROM {{ ref('smartmeter_readings_stream_kafka')}}