-- SQL query to calculate, for each page_id, the number of total visits, the number of unique visitors, and the timestamp 
-- when the page was most recently visited.

{{ config(materialized='materialized_view') }}
SELECT 
  page_id,
  COUNT(*) AS total_visits,
  COUNT(DISTINCT user_id) AS unique_visitors,
  MAX(timestamp) AS last_visit_time
FROM {{ ref('kafka_website_visits_stream')}}
GROUP BY page_id
