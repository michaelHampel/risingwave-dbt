import random
import json
from datetime import datetime, timezone
import time
import logging
import psycopg2
import random
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from faker import Faker
from faker.providers import DynamicProvider


class Current:
    def __init__(self, L1, L2, L3):
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3

    def to_dict(self):
        return {
            "L1": self.L1.to_dict(),
            "L2": self.L2.to_dict(),
            "L3": self.L3.to_dict(),
        }


class Measurement:
    def __init__(self, centiAmpere):
        self.centiAmpere = centiAmpere

    def to_dict(self):
        return {"centiAmpere": self.centiAmpere}


class Device:
    def __init__(self, deviceId):
        self.deviceId = deviceId

    def to_dict(self):
        return {"deviceId": self.deviceId.to_dict()}


class Value:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}


class Energy:
    def __init__(self, consumption, feedIn):
        self.consumption = consumption
        self.feedIn = feedIn

    def to_dict(self):
        return {
            "consumption": self.consumption.to_dict(),
            "feedIn": self.feedIn.to_dict(),
        }


class Reading:
    def __init__(self, wattHours):
        self.wattHours = wattHours

    def to_dict(self):
        return {"wattHours": self.wattHours}
    
class Id:
    def __init__(self, id):
        self.id = id

    def to_dict(self):
        return {"id": self.id}


class Meter:
    def __init__(self, meterId, systemTitle):
        self.meterId = meterId
        self.systemTitle = systemTitle

    def to_dict(self):
        return {
            "meterId": self.meterId.to_dict(),
            "systemTitle": self.systemTitle.to_dict(),
        }
    
class SystemTitle:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {"data": self.data}
    
class Owner:
    def __init__(self, id):
        self.id = id

    def to_dict(self):
        return {"id": self.id}


class Power:
    def __init__(self, draw, feed):
        self.draw = draw
        self.feed = feed

    def to_dict(self):
        return {
            "draw": self.draw.to_dict(),
            "feed": self.feed.to_dict(),
        }
    
class Watt:
    def __init__(self, watt):
        self.watt = watt

    def to_dict(self):
        return {"watt": self.watt}


class Voltage:
    def __init__(self, L1, L2, L3):
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3

    def to_dict(self):
        return {
            "L1": self.L1.to_dict(),
            "L2": self.L2.to_dict(),
            "L3": self.L3.to_dict(),
        }

class DeciVolt:
    def __init__(self, deciVolt):
        self.deciVolt = deciVolt

    def to_dict(self):
        return {"deciVolt": self.deciVolt}


class SmartMeterData:
    def __init__(
        self,
        current,
        device,
        energy,
        id,
        meter,
        owner,
        power,
        readingFrom,
        receivedAt,
        voltage,
    ):
        self.current = current
        self.device = device
        self.energy = energy
        self.id = id
        self.meter = meter
        self.owner = owner
        self.power = power
        self.readingFrom = readingFrom
        self.receivedAt = receivedAt
        self.voltage = voltage


logging.basicConfig()
logging.root.setLevel(logging.INFO)

rate_per_second = 5

# Kafka topic to produce messages to
topic = 'smartMeter-incoming'

kafka_config = {
    'bootstrap.servers': "localhost:9092"
}

# Kafka producer
producer = Producer(**kafka_config)

schema_registry_url = "http://localhost:8083"  

# Create clients
schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
string_serializer = StringSerializer('utf_8')


def postgres_connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect( 
            host="localhost", 
            port=5432, 
            user="postgres", 
            dbname="postgres"
        ) as conn:
            logging.info('Connected to PostgreS.')
            conn.autocommit = True
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        logging.error(error)

def get_owner_ids_and_device_ids(conn):
    """
    Selects all owner_ids and device_ids from the enox_users table.

    Args:
        conn: A psycopg2 connection object.

    Returns:
        A list of tuples, where each tuple contains an owner_id and a device_id.
    """

    with conn.cursor() as cur:
        cur.execute("SELECT owner_id, device_id FROM enox_users")
        rows = cur.fetchall()
    return rows

def random_owner_and_device(conn, num_iterations):
    """
    Randomly chooses an owner_id and device_id from the pg_enox_users table in a loop.

    Args:
        conn: A psycopg2 connection object.
        num_iterations: The number of iterations to run the loop.
    """

    owner_ids_and_device_ids = get_owner_ids_and_device_ids(conn)

    for _ in range(num_iterations):
        random_index = random.randint(0, len(owner_ids_and_device_ids) - 1)
        owner_id, device_id = owner_ids_and_device_ids[random_index]
        print(f"Random owner_id: {owner_id}, device_id: {device_id}")



def smartMeterData_to_dict(data, ctx):
        return {
            "current": data.current.to_dict(),
            "device": data.device.to_dict(),
            "energy": data.energy.to_dict(),
            "id": data.id.to_dict(),
            "meter": data.meter.to_dict(),
            "owner": data.owner.to_dict(),
            "power": data.power.to_dict(),
            "readingFrom": data.readingFrom,
            "receivedAt": data.receivedAt,
            "voltage": data.voltage.to_dict(),
        }


# Check if broker is available
def is_broker_available():
    global producer
    try:
        return True
    except Exception as e:
        logging.error(f"Broker not available: {e}")
        return False
    
def download_latest_schema(schema_registry_client, subject):
  """
  Downloads the latest schema for the given subject from the Schema Registry.

  Args:
      schema_registry_client: A SchemaRegistryClient instance.
      subject: The name of the schema subject.

  Returns:
      The latest schema ID as an integer, or None if no schema is found.
  """
  registered_schema = schema_registry_client.get_latest_version(subject)
  if not registered_schema:
      return None
  print(registered_schema.version)
  print(registered_schema.schema_id)
  print(registered_schema.schema.schema_str)
  return registered_schema.schema.schema_str

def send_message(producer, topic, message):
  """
  Sends a JSON message to the specified topic using the provided schema ID.

  Args:
      producer: A Kafka Producer instance.
      topic: The name of the Kafka topic.
      message: The JSON message to send.
      schema_id: The ID of the schema to use for serialization.
  """
  producer.produce (
     topic = topic, 
     key  = string_serializer("userOne"),
     value = json_serializer(
        message, 
        SerializationContext(topic, MessageField.VALUE)), 
     on_delivery = None
 )
  

if __name__ == "__main__":

    nr = 0

    ps_conn = postgres_connect()

    user_info_provider = DynamicProvider (
        provider_name = "user_info",
        elements = get_owner_ids_and_device_ids(ps_conn),
    )

    fake = Faker()
    fake.add_provider(user_info_provider)

    owner_id, device_id = fake.user_info()
    logging.info(f"Random owner_info: owner_id: {owner_id}, device_id: {device_id}")

    message = SmartMeterData (
        Current(Measurement(0), Measurement(1), Measurement(2)),
        Device(Value('wer1234')),
        Energy(Reading(140118), Reading(2345)),
        Id('miHam'),
        Meter(Value('1KFM0200001600'), SystemTitle('4b464d1020000640')),
        Owner('59c3d063-d6d8-4d07-b1f5-e3a21d884c12'),
        Power(Watt(12), Watt(27)),
        '2024-06-13T22:07:55Z',
        '2024-06-13T20:07:58Z',
        Voltage(DeciVolt(2369), DeciVolt(333), DeciVolt(98765))
    )

    try:
    # Produce messages to the Kafka topic
        if is_broker_available():
            logging.info(f"Sending smartmeter msgs with JSON schema")
            schema_subject = topic + "-value"
            # Download schema ID
            schema = download_latest_schema(schema_registry_client, schema_subject)  
            # Check if schema found
            if schema is None:
                print(f"Error: No schema found for subject {schema_subject}!!")
            else:
                json_serializer = JSONSerializer(schema, schema_registry_client, smartMeterData_to_dict)
                while nr < 10:
                    send_message(producer, topic, message)
                    producer.poll(0)  # Flush outstanding deliveries

                    time.sleep(1/rate_per_second)
                    nr += 1
                    logging.info(f"Sent msg: {message}")

    finally:
        print('Producer closed')

        # Wait for any outstanding messages to be delivered and delivery reports received
        producer.flush() 
    
"""

# Generate a random action
def generate_action():
    actions = ['click', 'scroll', 'view']
    return random.choice(actions)

def generate_value():
    return random.randint(1, 50000)

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

# Generate random purchase event
def generate_purchase_event():
    action = generate_action()
    user_id = random.randint(1,10)
    page_id = random.randint(1,15)
    current_time_utc = datetime.now(timezone.utc)
    action_time = current_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    return {
        "current":
        {
            "L1":{"centiAmpere":0},
            "L2":{"centiAmpere":0},
            "L3":{"centiAmpere":0}
        },
    "device":
        {
            "deviceId":
                {
                    "value":"ECUC012A3101E2.cuculus.net"
                }
        },
    "energy":
        {
            "consumption":
                {
                    "wattHours":140118
                },
            "feedIn":
                {
                    "wattHours":0
                }
        },
    "id":
        {
            "id":"11f82b93-d80d-442d-a2fc-d148422e3700"
        },
    "meter":
        {
            "meterId":
                {
                    "value":"1KFM0200001600"
                },
            "systemTitle":
                {
                    "data":"4b464d1020000640"
                }
        },
    "owner":
        {
            "id":"59c3d063-d6d8-4d07-b1f5-e3a21d884c12"
        },
    "power":
        {
            "draw":
                {
                    "watt":0
                },
            "feed":
                {
                    "watt":0
                }
        },
    "readingFrom":"2024-06-13T22:07:55Z",
    "receivedAt":"2024-06-13T20:07:58Z",
    "voltage":
        {
            "L1":
                {
                    "deciVolt":2369
                },
            "L2":
                {
                    "deciVolt":0
                },
            "L3":
                {
                    "deciVolt":0
                }
        }
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

"""