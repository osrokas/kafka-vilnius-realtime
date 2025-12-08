import os

from dotenv import load_dotenv

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env", override=True)

# Kafka topic name
TOPIC = os.getenv("KAFKA_TOPIC", "gps_data")

# Spark packages for Iceberg and Kafka
packages = (
    "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,"
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1,"
    "org.apache.kafka:kafka-clients:3.6.0"
)

# Configure Spark with Iceberg
spark = SparkSession.builder \
    .appName("IcebergStreaming") \
    .config("spark.jars.packages", packages) \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.public_transport", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.public_transport.type", "hadoop") \
    .config("spark.sql.catalog.public_transport.warehouse", "/data/warehouse/public_transport") \
    .getOrCreate()

# Read from Kafka topic
streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Retrieve the raw message value as string
raw_df = streaming_df.select(col("value").cast("string").alias("raw_message"))

# Save to Iceberg table
query = raw_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("truncate", "false") \
    .outputMode("append") \
    .option("checkpointLocation", "/data/warehouse/checkpoints/public_transport/bronze/gps_data") \
    .toTable("public_transport.bronze.gps_data")

# Await termination of the streaming query
query.awaitTermination()