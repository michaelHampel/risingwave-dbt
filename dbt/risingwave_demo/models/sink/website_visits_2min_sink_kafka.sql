{{ config(materialized='sink') }}
CREATE SINK IF NOT EXISTS {{ this }} 
FROM {{ ref('website_visits_2min_dbt')}} 
WITH (
   connector='kafka',
   properties.bootstrap.server='redpanda-0:19092',
   topic='rw-sink'
)
FORMAT PLAIN ENCODE JSON (
   force_append_only='true'
)