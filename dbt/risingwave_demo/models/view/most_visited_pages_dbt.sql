-- The following SQL creates a materialized view which lists the top 3 most visited pages from users with 
-- ages lower than 35 and calculates the number of unique visitors for these pages.

{{ config(materialized='materialized_view') }}
SELECT  
  page_id,
  COUNT(DISTINCT user_id) AS total_visits
FROM 
  {{ ref('website_visits_from_users_dbt')}} 
WHERE user_age < 35
GROUP BY page_id
LIMIT 3 