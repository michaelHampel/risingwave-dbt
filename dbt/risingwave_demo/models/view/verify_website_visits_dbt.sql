-- By creating a source, RisingWave has been connected to Kafka. However, to ingest data from Kafka, we need to create some materialized views.
-- Using the following SQL, a materialized view is created to grab all existing data from the source and continuously capture
-- newly inserted events from Kafka.

{{ config(materialized='materialized_view') }}
SELECT *
FROM {{ ref('kafka_website_visits_stream')}}