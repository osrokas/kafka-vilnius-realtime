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

spark = SparkSession \
    .builder \
    .appName("HiveConnection") \
    .config("spark.jars.packages", packages) \
    .config("spark.sql.warehouse.dir", "hdfs://localhost:9000/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .enableHiveSupport() \
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
    .option("checkpointLocation", "/tmp/checkpoint/gps_data") \
    .toTable("public_transport.default.gps_data")

# Await termination of the streaming query
query.awaitTermination()