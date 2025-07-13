from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
import pandas as pd
import time
import geopandas as gpd
from datetime import datetime

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

    engine = create_engine("postgresql://postgres:password@localhost/mydb")
    # get message from Kafka
    for message in consumer:
        data = message.value

        # Assuming the data is in JSON format
        data = json.loads(data)
        df = pd.DataFrame(data)

        df["Platuma"] = df["Platuma"].astype(str)
        df["Ilguma"] = df["Ilguma"].astype(str)

        # in 2 position add . to string
        df["Platuma"] = df["Platuma"].apply(lambda x: x[:2] + "." + x[2:])
        df["Ilguma"] = df["Ilguma"].apply(lambda x: x[:2] + "." + x[2:])

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["Ilguma"].astype(float), df["Platuma"].astype(float)),
            crs="EPSG:4326",  # Assuming WGS84 coordinate system
        )

        gdf.rename(columns={"MasinosNumeris": "vehicle_id"}, inplace=True)

        gdf["timestamp"] = datetime.now()
        gdf["timestamp"] = pd.to_datetime(gdf["timestamp"])

        gdf = gdf[["vehicle_id", "timestamp", "geometry"]]

        gdf.to_postgis(
            name="gps_data",
            con=engine,
            if_exists="replace",  # replace the table if it exists
            index=False,
        )

        # simulate delay for new data
        time.sleep(5)


if __name__ == "__main__":
    load_data()
    print("Starting GPS data streaming...")
