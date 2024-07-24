#!/bin/bash

# run in risingwave_enox dir

# create necessary redpanda topics
# blocks until redpanda is reachable
rpk topic list 

echo -e 'Creating redpanda topics'
rpk topic create smartMeter-incoming

echo -e 'Successfully created the following topics:'
rpk topic list 

echo -e 'Register JSON Schema with Karapace Schema Registry'
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data @smartMeter_schema.json \
     http://localhost:8083/subjects/smartMeter-incoming-value/versions

echo -e 'Registered Scema subjects: '
curl -X GET http://localhost:8083/subjects 

echo -e 'Starting smart-meter data generator...'

# Activate the virtual environment
source ../.venv/bin/activate

# Run the Python script
python data-generator.py