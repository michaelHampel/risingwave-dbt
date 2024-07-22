-- SQL query to calculate, for each page_id, the number of total visits, the number of unique visitors, and the timestamp 
-- when the page was most recently visited.

{{ config(materialized='materialized_view') }}
SELECT 
  window_start AS report_ts,
  page_id,
  COUNT(*) AS total_visits,
  COUNT(DISTINCT user_id) AS unique_visitors,
  MAX(timestamp) AS last_visit_time
FROM 
    TUMBLE (
        {{ ref('kafka_website_visits_stream')}},
        timestamp,
        INTERVAL '1' MINUTE
    )
GROUP BY 
    window_start,
    page_id