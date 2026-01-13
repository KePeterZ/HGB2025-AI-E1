from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, window, lower, count
)

spark = SparkSession.builder \
    .appName("Crash Monitoring Per User") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Kafka source
logs_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "logs") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON payload
parsed_df = logs_df.selectExpr(
    "CAST(value AS STRING) as json"
).selectExpr(
    "from_json(json, 'user_id STRING, severity STRING, content STRING, timestamp TIMESTAMP') as data"
).select("data.*")

# Filter crash events
crash_df = parsed_df.filter(
    (lower(col("content")).contains("crash")) &
    (col("severity").isin("High", "Critical"))
)

# Event-time windowed aggregation
agg_df = crash_df \
    .withWatermark("timestamp", "30 seconds") \
    .groupBy(
        window(col("timestamp"), "10 seconds"),
        col("user_id")
    ) \
    .agg(
        count("*").alias("crash_count")
    ) \
    .filter(col("crash_count") > 2)

# Output to console
query = agg_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()