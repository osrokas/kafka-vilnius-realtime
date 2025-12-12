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
WAREHOUSE = "file:///home/osrokas/warehouse"

# # Configure Spark with Iceberg
# spark = SparkSession.builder \
#     .appName("IcebergStreaming") \
#     .enableHiveSupport() \
#     .config("spark.jars.packages", packages) \
#     .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
#     .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
#     .config("spark.sql.catalog.spark_catalog.type", "hive") \
#     .config("spark.sql.catalog.spark_catalog.uri", "thrift://localhost:9083") \
#     .config("spark.sql.catalog.spark_catalog.warehouse", WAREHOUSE) \
#     .config("spark.sql.warehouse.dir", WAREHOUSE) \
#     .config("hive.metastore.warehouse.dir", WAREHOUSE) \
#     .getOrCreate()

spark = SparkSession \
    .builder \
    .appName("HiveConnection") \
    .config("spark.sql.warehouse.dir", "hdfs://localhost:9000/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .config("spark.sql.hive.metastore.version", "4.1.0") \
    .enableHiveSupport() \
    .getOrCreate()

# Set log level
# spark.sparkContext.setLogLevel("INFO")

# print("=" * 60)
# print("SparkSession created successfully!")
# print("=" * 60)

# # Test connection - Show databases
# print("\nAvailable Databases:")
# print("-" * 60)
spark.sql("SHOW DATABASES").show()

spark.sparkContext.setLogLevel("INFO")
    # .config("spark.sql.warehouse.dir", "/var/lib/docker/volumes/warehouse_data/_data") \
# Check spark version
# print("Spark Version:", spark.version)
# spark.sql("REFRESH DATABASE")
# spark.sql("REFRESH SCHEMA")
# spark.catalog.clearCache()
# spark.sql("SHOW DATABASES").show()
# # # spark.sql("CREATE TABLE test_table2 (id INT, name STRING) STORED AS PARQUET")
# spark.sql("SHOW TABLES").show()


# Create table if not exists
# spark.sql("""
# CREATE TABLE IF NOT EXISTS public_transport.default.bbb (raw_message STRING) 
# USING ICEBERG
# """)


# # Read from Kafka topic
# streaming_df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", "localhost:9092") \
#     .option("subscribe", TOPIC) \
#     .option("startingOffsets", "latest") \
#     .load()

# # Retrieve the raw message value as string
# raw_df = streaming_df.select(col("value").cast("string").alias("raw_message"))

# # Save to Iceberg table
# query = raw_df.writeStream \
#     .format("iceberg") \
#     .outputMode("append") \
#     .option("truncate", "false") \
#     .outputMode("append") \
#     .option("checkpointLocation", "/tmp/checkpoint/gps_data") \
#     .toTable("public_transport.default.gps_data")

# # Await termination of the streaming query
# query.awaitTermination()