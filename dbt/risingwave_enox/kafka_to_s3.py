from confluent_kafka import Consumer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import MessageField, SerializationContext

import json
from datetime import datetime
import os
import boto3
from domain import *

# Credentials and Connection Info
access_key = "minioadmin"
secret_key = "minio123"
endpoint = "http://localhost:9301"  # MinIO endpoint
region = "eu-west-1"

# Initialize Boto3 S3 client
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
s3 = session.client('s3', endpoint_url=endpoint, region_name=region)

# Schema Registry Configuration
schema_registry_url = "http://localhost:8085"
schema_subject = 'smartMeter-incoming-value'

schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
schema_version = schema_registry_client.get_latest_version(schema_subject)
schema_id = schema_version.schema_id
schema = schema_registry_client.get_schema(schema_id)
json_deserializer = JSONDeserializer(schema, from_dict=dict_to_smartMeterData)

# Configure Kafka Consumer
consumer_config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": 'group-1'
}
consumer = Consumer(consumer_config)
consumer.subscribe(['smartMeter-incoming'])

# Main processing loop
print("Listening..")
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        byte_message = msg.value()
        if byte_message is None:
            print("Received tombstone message, skipping...")
            continue
        
        print(f"byte message: {byte_message}, Type: {type(byte_message)}")
        
        # Deserialize JSON message
        decoded_message = json_deserializer(byte_message, SerializationContext(msg.topic(), MessageField.VALUE))
        print(f"Decoded message: {decoded_message}, Type: {type(decoded_message)}")
        
        # Convert dictionary to JSON string
        json_data = json.dumps(decoded_message.__dict__)
        

        # Upload JSON data to MinIO
        bucket_name = 'my-test'
        current_datetime = datetime.now()
        current_date = current_datetime.strftime("%Y-%m-%d")
        current_time = current_datetime.strftime("%H-%M-%S")
        object_key = f'devices/{current_date}/devices_{current_time}.json'

        # Ensure directory exists in MinIO
        directory_path = os.path.dirname(object_key)
        print(f"directory path: {directory_path}")
        s3.put_object(Bucket=bucket_name, Key=f'{directory_path}/')

        # Upload JSON data as an object to MinIO
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_data)

        s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)
        print(f"S3 response: {s3_response}, Type: {type(s3_response)}")
        j = json.loads(s3_response['Body'].read())
        sm_data = SmartMeterData(**j)
        print(f"S3 smartMeter data: {sm_data}, Type: {type(sm_data)}")




        
    
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
