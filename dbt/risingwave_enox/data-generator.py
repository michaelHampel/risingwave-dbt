import random
import json
from datetime import datetime, timedelta
import time
import logging
import psycopg2
import random
from zoneinfo import ZoneInfo
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

def get_user_info(conn):
    """
    Selects user_info from the enox_users table.

    Args:
        conn: A psycopg2 connection object.

    Returns:
        A list of triples, where each triple contains owner_id, device_id and smartMeter_mac
    """

    with conn.cursor() as cur:
        cur.execute("SELECT owner_id, device_id, smartMeter_mac FROM enox_users")
        rows = cur.fetchall()
    return rows

def random_owner_and_device(conn, num_iterations):
    """
    Randomly chooses an owner_id and device_id from the pg_enox_users table in a loop.

    Args:
        conn: A psycopg2 connection object.
        num_iterations: The number of iterations to run the loop.
    """

    user_ids = get_user_info(conn)

    for _ in range(num_iterations):
        random_index = random.randint(0, len(user_ids) - 1)
        owner_id, device_id, smartMeter_mac = user_ids[random_index]
        print(f"Random owner_id: {owner_id}, device_id: {device_id}, smartmeter_mac: {smartMeter_mac}")



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

def next_message(fake):
    owner_id, device_id, smartMeter_mac = fake.user_info()
    logging.info(f"Random owner_info: owner_id: {owner_id}, device_id: {device_id}, smartMeter_mac: {smartMeter_mac}")
    read_time = fake.date_time_between(start_date= '-7d', tzinfo=ZoneInfo('Europe/Vienna'))
    received_time = read_time + timedelta(seconds = random.randint(1,5))
    message = SmartMeterData (
        Current(Measurement(random.randint(0,10)), Measurement(random.randint(0,10)), Measurement(random.randint(0,10))),
        Device(Value(device_id)),
        Energy(Reading(random.randint(2, 30)), Reading(random.randint(0, 40))),
        Id(fake.pystr_format()),
        Meter(Value(fake.pystr_format()), SystemTitle(smartMeter_mac)),
        Owner(owner_id),
        Power(Watt(random.randint(5,50)), Watt(random.randint(2,60))),
        str(read_time),
        str(received_time),
        Voltage(DeciVolt(random.randint(100,10000)), DeciVolt(random.randint(200,8000)), DeciVolt(random.randint(300,15000)))
    )
    return message


def send_message(producer, topic, message):
  """
  Sends a JSON message to the specified topic using the provided schema ID.

  Args:
      producer: A Kafka Producer instance.
      topic: The name of the Kafka topic.
      value: JSON message to send and SerializationContext with configured schema.
      on_delivery: callback function or None
  """
  producer.produce (
     topic = topic, 
     key  = string_serializer(message.owner.id),
     value = json_serializer(
        message, 
        SerializationContext(topic, MessageField.VALUE)), 
     on_delivery = None
 )
  

if __name__ == "__main__":

    nr = 0
    rate_per_second = 25

    ps_conn = postgres_connect()

    user_info_provider = DynamicProvider (
        provider_name = "user_info",
        elements = get_user_info(ps_conn),
    )

    fake = Faker()
    fake.add_provider(user_info_provider)

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
                while nr < 20000:
                    send_message(producer, topic, next_message(fake))
                    producer.poll(0)  # Flush outstanding deliveries

                    time.sleep(1/rate_per_second)
                    nr += 1
                    if nr % 100 == 0:
                        logging.info(f"Sent {nr} records")

    finally:
        print('Producer closed')

        # Wait for any outstanding messages to be delivered and delivery reports received
        producer.flush() 