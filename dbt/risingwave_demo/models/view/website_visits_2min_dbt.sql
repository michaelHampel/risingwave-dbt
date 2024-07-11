-- a materialized view that tracks how many actions each user performs on each web page within a two minutes window.
-- The following SQL query uses the tumble function to map events into two-minute windows, 
-- https://docs.risingwave.com/docs/current/sql-function-time-window/#tumble-time-window-function
-- then groups by user_id, page_id, and window_end to count the number of actions each user performs on each web page within 
-- the designated time window. Finally, we join the resulting table with the users table to see 
-- the corresponding first_name, last_name, and age of each user.

{{ config(materialized='materialized_view') }}
SELECT  
  user_id, 
  first_name, 
  last_name, 
  age, 
  page_id, 
  num_actions, 
  window_end
FROM 
  ( SELECT 
        user_id, 
        page_id, 
        COUNT(action) AS num_actions, 
        window_end 
    FROM TUMBLE ( {{ ref('kafka_website_visits_stream')}}, timestamp, INTERVAL '2 MINUTES')
    GROUP BY user_id, page_id, window_end
  ) T
LEFT JOIN {{ ref('pg_users_table')}} P ON T.user_id = P.id