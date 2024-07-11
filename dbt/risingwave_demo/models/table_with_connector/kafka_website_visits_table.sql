-- You can also create a table to connect to the Kafka topic. Compared to creating a source, 
-- a table persists the data from the stream by default. 
-- In this way, you can still query the table data even after the Kafka environment has been shut down or 
-- messages got deleted in Kafka (TTL).

{{ config(materialized='table_with_connector') }}
CREATE TABLE IF NOT EXISTS {{ this }} (
  user_id integer,
  page_id integer,
  action varchar,
  timestamp timestamptz
) 
INCLUDE key AS msg_key
INCLUDE partition AS msg_partition
INCLUDE offset AS msg_offset
INCLUDE timestamp AS msg_timestamp
INCLUDE header AS msg_header
WITH (
  connector='kafka',
  topic='rw-test',
  properties.bootstrap.server='redpanda-0:19092',
  scan.startup.mode='earliest'
) FORMAT PLAIN ENCODE JSON