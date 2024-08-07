-- To connect to the data stream in Kafka, we need to create a source using the CREATE SOURCE command. 
-- Once the connection is established, RisingWave will be able to read any new messages from Kafka in real time.
-- The following SQL query creates a source named kafka_website_visits_stream. 
-- We also define a schema here to map fields from the JSON data to the streaming data.

{{ config(materialized='source') }}
CREATE SOURCE IF NOT EXISTS {{ this }}
INCLUDE key AS msg_key
INCLUDE partition AS msg_partition
INCLUDE offset AS msg_offset
INCLUDE timestamp AS msg_timestamp
INCLUDE header AS msg_header
WITH (
  connector='kafka',
  topic='smartMeter-incoming',
  properties.bootstrap.server='redpanda-0:19092',
  scan.startup.mode='earliest'
) 
FORMAT PLAIN ENCODE JSON (
    schema.registry = 'http://karapace-registry:8085'
) 