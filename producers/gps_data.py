import os
import time
import json

from kafka import KafkaProducer

from src.decorators import load_env_vars
from src.public_transport import fetch_gps_data


@load_env_vars
def main():
    # Load environment variables
    API_URL = os.getenv("GPS_URL")
    TOPIC_NAME = os.getenv("KAFKA_TOPIC")
    KAFKA_BROKER = os.getenv("KAFKA_BROKERS", "localhost:9092")

    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    print("Kafka producer initialized.")

    # Fetch and send GPS data to Kafka topic
    while True:

        print("Fetching GPS data...")
        data = fetch_gps_data(API_URL)

        # Check if data is not empty and send to Kafka
        if data:
            producer.send(TOPIC_NAME, value=data)

        print("Data sent to Kafka successfully.")

        time.sleep(3)  # fetch every 3 seconds


if __name__ == "__main__":
    main()
