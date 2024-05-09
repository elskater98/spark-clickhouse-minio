import logging
import os
from pyspark import SparkContext
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MinioSparkJob")


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


if __name__ == '__main__':
    spark = SparkSession.builder.appName("MinioSparkJob").getOrCreate()

    load_config(spark.sparkContext)

    df = spark.read.option("header", "true").csv(f"s3a://project/customer_booking.csv")

    df = df.filter(
        (df.booking_complete == 0) & (df.sales_channel == 'Internet') & (df.booking_origin == 'South Korea'))

    logger.info("Filter by sales channel == Internet & booking_complete == 0 & booking_origin == South Korea")

    df.write.format("csv").option("header", "true").mode('overwrite').save('s3a://project/customer_booking_OUTPUT')
