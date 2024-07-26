{{ config(materialized='sink') }}
CREATE SINK IF NOT EXISTS {{ this }} 
FROM {{ ref('smartmeter_data_with_user_info')}} 
WITH (
   connector='kafka',
   properties.bootstrap.server='redpanda-0:19092',
   topic='smartMeter-p-town',
   primary_key='town'
)
FORMAT PLAIN ENCODE JSON (
   force_append_only='true'
)