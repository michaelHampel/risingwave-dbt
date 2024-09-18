{{ config(materialized='materialized_view') }}
SELECT 
  device_id, 
  owner_id,
  SUM(((energy).consumption)."wattHours") as consumption_wh
FROM
  {{ ref('smartmeter_data_with_user_info')}} 
WHERE
  read_ts > (NOW() - INTERVAL '1' MINUTE)
GROUP BY
  device_id, owner_id
ORDER BY 
  consumption_wh DESC