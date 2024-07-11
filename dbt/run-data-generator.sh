#!/bin/bash

# create necessary redpanda topics
# blocks until redpanda is reachable
rpk topic list 

echo -e 'Creating redpanda topics'
rpk topic create rw-test
rpk topic create rw-sink

echo -e 'Successfully created the following topics:'
rpk topic list 

echo -e 'Starting data generator...'

# Activate the virtual environment
source .venv/bin/activate

# Run the Python script
python data-generator.py