import logging
import os
from datetime import datetime

import clickhouse_connect
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MinioSparkJob")

CURRENT_DATE = datetime.now().strftime("%Y%m%d")

from dotenv import load_dotenv

load_dotenv()


# REFERENCES
# https://stackoverflow.com/questions/75770134/bitnami-spark-installation-of-jars-and-connection-to-bitnami-minio
# https://stackoverflow.com/questions/69680552/minio-spark-integration
# https://blog.min.io/spark-minio-kubernetes/

def load_config(spark_context: SparkContext):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key",
                                                 os.getenv("AWS_ACCESS_KEY_ID"),
                                                 )

    spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key",
                                                 os.getenv("AWS_SECRET_ACCESS_KEY"),
                                                 )

    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint",
                                                 os.getenv("MINIO_ENDPOINT"))  # container name or ip / host

    spark_context._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

    spark_context._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")

    spark_context._jsc.hadoopConfiguration().set("fs.s3a.attempts.maximum", "1")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.connection.establish.timeout", "5000")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.connection.timeout", "10000")


@udf
def to_boolean(s):
    return 'true' if s == '1' else 'false'


if __name__ == '__main__':

    if os.getenv('LOCAL', 'True') == 'True':
        spark = SparkSession.builder.appName("MinioSparkJob").getOrCreate()
        df = spark.read.option("header", "true").csv(f"data/spark/datasets/customer_booking.csv")
    else:
        spark = SparkSession.builder.master("spark://spark-master:7077").appName(
            "MinioSparkJob").getOrCreate()  # CLUSTER
        load_config(spark.sparkContext)
        df = spark.read.option("header", "true").csv(f"s3a://project/customer_booking.csv")

    origins = df.select('booking_origin').distinct()

    client = clickhouse_connect.create_client(host=os.getenv('CLICKHOUSE_HOST'),
                                              port=int(os.getenv('CLICKHOUSE_PORT')),
                                              username=os.getenv('CLICKHOUSE_ADMIN_USER'),
                                              password=os.getenv('CLICKHOUSE_ADMIN_PASSWORD'),
                                              database=os.getenv('CLICKHOUSE_DATABASE'), secure=False)

    for i in origins.collect():
        df_origin = df.filter(
            (df.booking_complete == 0) & (df.sales_channel == 'Internet') & (df.booking_origin == i.booking_origin))

        # cast booleans
        df_origin = df_origin.withColumn("wants_extra_baggage", to_boolean("wants_extra_baggage"))
        df_origin = df_origin.withColumn("wants_preferred_seat", to_boolean("wants_preferred_seat"))
        df_origin = df_origin.withColumn("wants_in_flight_meals", to_boolean("wants_in_flight_meals"))
        df_origin = df_origin.withColumn("booking_complete", to_boolean("booking_complete"))

        logger.info(f"Filter by sales channel == Internet & booking_complete == 0 & booking_origin == {i}")

        # Data Lake
        df_origin.repartition(1).write.format("csv").option("header", "true").mode('overwrite').save(
            f"s3a://{os.getenv('MINIO_DEFAULT_BUCKET')}/{i.booking_origin}/{CURRENT_DATE}")
        logger.info(f"Data Lake updated successfully - {i.booking_origin} - {CURRENT_DATE}")
        try:
            # Data Warehouse
            client.command(
                f"INSERT INTO bookings SELECT * FROM s3('{os.getenv('MINIO_ENDPOINT')}/{os.getenv('MINIO_DEFAULT_BUCKET')}/{i.booking_origin}/{CURRENT_DATE}/*', '{os.getenv('AWS_ACCESS_KEY_ID')}', '{os.getenv('AWS_SECRET_ACCESS_KEY')}', 'CSVWithNames')")
            logger.info(f"Data Warehouse updated successfully - {i.booking_origin} - {CURRENT_DATE}")
        except Exception as e:
            logger.error(e)
