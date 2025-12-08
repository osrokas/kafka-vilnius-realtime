from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
import time

from sqlalchemy import create_engine

if os.path.exists(".env"):
    load_dotenv(".env", override=True)

# Load environment variables
API_URL = os.getenv("GPS_URL")
TOPIC_NAME = os.getenv("KAFKA_TOPIC")

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKERS", "localhost:9092")

consumer = KafkaConsumer(
    TOPIC_NAME,  # topic to subscribe
    bootstrap_servers=KAFKA_BROKER,  # Kafka broker address
    auto_offset_reset="latest",  # start reading at the earliest message
    enable_auto_commit=True,  # commit offsets automatically
    group_id="my-group",  # consumer group id
    value_deserializer=lambda x: x.decode("utf-8"),  # decode bytes to string
)


def load_data():

    engine = create_engine("postgresql://postgres:password@localhost/postgres")
    # get message from Kafka
    for message in consumer:
        data = message.value

        # Assuming the data is in JSON format
        data = json.loads(data)

        # Parse data into lines
        lines = data.split("\n")

        # First line is header
        header = lines[0].split(",")

        lines = [line.split(",") for line in lines[1:] if line.strip() != ""]

        # Last line is timestamp
        timestamp_line = lines.pop(-1)[-1]

        # Add key from header and value from line to each line
        json_data = []
        for line in lines:
            record = {}
            for i in range(len(header)):
                record[header[i]] = line[i]
                record["timestamp"] = timestamp_line
            json_data.append(record)
    
        # simulate delay for new data
        time.sleep(5)


if __name__ == "__main__":
    load_data()
    print("Starting GPS data streaming...")
