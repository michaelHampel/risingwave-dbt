import random
import json
from datetime import datetime, timezone
import time
import logging
from confluent_kafka import Producer

logging.basicConfig()
logging.root.setLevel(logging.INFO)

rate_per_second = 5


# Check if broker is available
def is_broker_available():
    global producer
    try:
        return True
    except Exception as e:
        logging.error(f"Broker not available: {e}")
        return False

# Generate a random product ID
def generate_action():
    actions = ['click', 'scroll', 'view']
    return random.choice(actions)

# Generate random purchase event
def generate_purchase_event():
    action = generate_action()
    user_id = random.randint(1,10)
    page_id = random.randint(1,15)
    current_time_utc = datetime.now(timezone.utc)
    action_time = current_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    return {
        "page_id": page_id,
        "user_id": user_id,
        "action": action,
        "timestamp": action_time,
    }

# Kafka topic to produce messages to
topic = 'rw-test'

kafka_config = {
    'bootstrap.servers': "localhost:9092"
}

# Kafka producer
producer = Producer(**kafka_config)

if __name__ == "__main__":

    nr = 0

    try:
    # Produce messages to the Kafka topic
        if is_broker_available():
            logging.info(f"Sending 20,000 records to Kafka")
            while nr < 20000:

                message = generate_purchase_event()
                message_str = json.dumps(message).encode('utf-8')
                key_str = str(message["user_id"]).encode('utf-8')

                producer.produce(topic, value=message_str, key=key_str)

                time.sleep(1/rate_per_second)
                nr += 1
                if nr % 100 == 0:
                    logging.info(f"Sent {nr} records")

    finally:

        print('Producer closed')

        # Wait for any outstanding messages to be delivered and delivery reports received
        producer.flush() 

