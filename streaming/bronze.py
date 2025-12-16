import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

if os.path.exists(".env"):
    load_dotenv(".env", override=True)

TOPIC = os.getenv("KAFKA_TOPIC", "gps_data")

packages = (
    "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,"
    "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.13:0.104.5,"
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1,"
    "org.apache.kafka:kafka-clients:3.6.0,"
    "org.apache.hadoop:hadoop-client:3.4.1"
)


spark = SparkSession \
    .builder \
    .appName("GPSIcebergStream") \
    .config("spark.jars.packages", packages) \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions," 
            "org.projectnessie.spark.extensions.NessieSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog") \
    .config("spark.sql.catalog.iceberg.uri", "http://localhost:19120/api/v1") \
    .config("spark.sql.catalog.iceberg.ref", "main") \
    .config(
        "spark.sql.catalog.iceberg.warehouse",
        "hdfs://localhost:9000/iceberg/warehouse"
    ) \
    .config("spark.eventLog.enabled", "false") \
    .getOrCreate()

spark.sql("CREATE DATABASE IF NOT EXISTS iceberg.bronze")

spark.sql("""
    CREATE TABLE IF NOT EXISTS iceberg.bronze.gps_data (
        raw_message STRING
    ) USING ICEBERG
""")

print("Reading from Kafka...")
streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

raw_df = streaming_df.select(col("value").cast("string").alias("raw_message"))

print("Starting stream write to Iceberg...")
query = raw_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint/gps_data_iceberg") \
    .toTable("iceberg.bronze.gps_data") \
    
print("Stream started. Awaiting termination...")
query.awaitTermination()