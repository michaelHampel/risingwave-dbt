{{ config(materialized='materialized_view') }}
SELECT  
  AVG(((energy).consumption)."wattHours") as consumption_wh,
  AVG(((energy)."feedIn")."wattHours") as feedin_wh,
  window_start,
  window_end
FROM
  TUMBLE(
    {{ ref('smartmeter_data_with_user_info')}},
    read_ts,
    INTERVAL '5' MINUTE
  )
GROUP BY
  window_start, window_end
ORDER BY 
  feedin_wh DESC