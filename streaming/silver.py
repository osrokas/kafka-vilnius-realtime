import os

import pandas as pd
from dotenv import load_dotenv

from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env", override=True)

# Kafka topic name
TOPIC = os.getenv("KAFKA_TOPIC", "gps_data")

# Spark packages for Iceberg and Kafka
packages = (
    "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,"
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

# Set Arrow optimization
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

schema = StructType([
    StructField("rows", ArrayType(ArrayType(StringType())), True),
    StructField("header", ArrayType(StringType()), True)
])

@pandas_udf(schema, PandasUDFType.SCALAR)
def parse_raw_udf(raw_series: pd.Series) -> pd.DataFrame:
    rows_out = []
    header_out = None

    for raw in raw_series:
        if raw is None:
            rows_out.append([])
            continue

        # 1) decode escape sequences: \\n → \n, \\uXXXX → unicode
        decoded = raw.encode('utf-8').decode('unicode_escape')

        # 2) strip wrapping double quotes
        if decoded.startswith('"') and decoded.endswith('"'):
            decoded = decoded[1:-1]

        # 3) split lines
        lines = decoded.split("\n")

        # header
        header = lines[0].split(",")
        if header[-1] == "":
            header[-1] = "None"

        header.append("timestamp")  # add timestamp column

        # data rows
        data_rows = [l.split(",") for l in lines[1:] if l.strip()]

        timestamp = data_rows.pop()  # remove timestamp row

        # normalize rows
        cleaned_rows = []
        for r in data_rows:
            # empty string → None
            r = [v if v != "" else None for v in r]

            # fix rows that split a field because of comma inside
            if len(r) > len(header):
                # join the 13th & 14th (0-based → 12 & 13)
                r[13] = str(r[12]) + "," + str(r[13])
                del r[12]

            cleaned_rows.append(r)

            # add timestamp at the end
            r.append(timestamp[-1])

        rows_out.append(cleaned_rows)
        header_out = header  # same header for all rows

    return pd.DataFrame({
        "rows": rows_out,
        "header": [header_out] * len(rows_out)
    })

@pandas_udf(StringType())
def decode_lithuanian_udf(series: pd.Series) -> pd.Series:
    # Re-encode as latin1, decode as utf-8
    return series.fillna('').apply(lambda x: x.encode('latin1').decode('utf-8') if x else x)


# Read from Iceberg table
df = spark.readStream.format("iceberg") \
    .load("public_transport.bronze.gps_data")

# Parse raw messages
parsed = df.select(parse_raw_udf(col("raw_message")).alias("parsed"))

# Extract header
header = [
    "Transportas", "Marsrutas", "ReisoID", "MasinosNumeris",
    "Ilguma", "Platuma", "Greitis", "Azimutas", "ReisoPradziaMinutemis",
    "NuokrypisSekundemis", "MatavimoLaikas", "MasinosTipas",
    "KryptiesTipas", "KryptiesPavadinimas", "ReisoIdGTFS",
    "IntervalasPries", "IntervalasPaskui", "None", "timestamp"
]
parsed = df.select(parse_raw_udf(col("raw_message")).alias("parsed"))

# header = parsed.select("parsed.header").first()[0]

# Extract data rows
exploded = parsed.select(explode("parsed.rows").alias("row"))

# Create DataFrame with proper construction
df = exploded.select([
    col("row")[i].alias(el) for i, el in enumerate(header)
])

# Define new column names mapping
new_cols = {
    "Transportas": "transport",
    "Marsrutas": "route", 
    "ReisoID": "trip_id", 
    "MasinosNumeris": "vehicle_number", 
    "Ilguma": "longitude", 
    "Platuma": "latitude", 
    "Greitis": "speed",
    "Azimutas": "azimuth",
    "ReisoPradziaMinutemis": "trip_start_minutes",
    "NuokrypisSekundemis": "delay_seconds", 
    "MatavimoLaikas": "measurement_time",
    "MasinosTipas": "vehicle_type",
    "KryptiesTipas": "direction_type",
    "KryptiesPavadinimas": "direction_name",
    "ReisoIdGTFS": "gtfs_trip_id",
    "IntervalasPries": "interval_before",
    "IntervalasPaskui": "interval_after", 
}

# Rename columns
df = df.select([col(c).alias(new_cols.get(c, c)) for c in df.columns])

# Drop unnecessary column
df = df.drop("None")

# Drop rows with null timestamp
df = df.filter(col("timestamp").isNotNull())

# Cast timestamp column to proper timestamp type
df = df.withColumn(
    "timestamp",
    to_timestamp("timestamp", " dd MMM yyyy HH:mm:ss 'GMT'")
)

# Cast latitude & longitude to float with proper decimal point
df = df.withColumn(
    "longitude",
    concat(substring("longitude", 1, 2), lit("."), substring("longitude", 3, 100)).cast("float")
)
df = df.withColumn(
    "latitude",
    concat(substring("latitude", 1, 2), lit("."), substring("latitude", 3, 100)).cast("float")
)

# Decode Lithuanian characters from latin1 to utf-8
df = df.withColumn("direction_name", decode_lithuanian_udf(col("direction_name")))

# Cast other columns to proper types
df = df.withColumn("trip_id", col("trip_id").cast("bigint"))
df = df.withColumn("vehicle_number", col("vehicle_number").cast("int"))
df = df.withColumn("speed", col("speed").cast("int"))
df = df.withColumn("azimuth", col("azimuth").cast("int"))
df = df.withColumn("trip_start_minutes", col("trip_start_minutes").cast("int"))
df = df.withColumn("delay_seconds", col("delay_seconds").cast("int"))
df = df.withColumn("measurement_time", col("measurement_time").cast("bigint"))
df = df.withColumn("interval_before", col("interval_before").cast("int"))
df = df.withColumn("interval_after", col("interval_after").cast("int"))

# Save to Iceberg table
query = df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("truncate", "false") \
    .outputMode("append") \
    .option("checkpointLocation", "/data/warehouse/checkpoints/public_transport/silver/gps_data") \
    .toTable("public_transport.silver.gps_data")

# Await termination of the streaming query
query.awaitTermination()