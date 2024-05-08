from pyspark.sql import SparkSession

if __name__ == '__main__':
    # https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html#
    # https://medium.com/@mehmood9501/using-apache-spark-docker-containers-to-run-pyspark-programs-using-spark-submit-afd6da480e0f

    # https://stackoverflow.com/questions/69680552/minio-spark-integration
    spark = SparkSession.builder.appName("Spark-Test").getOrCreate()

    # TODO: READ FROM MINIO
    df = spark.read.csv('datasets/customer_booking.csv', header=True, inferSchema=True, sep=',')
    df = df.filter((df.booking_complete == 0) & (df.sales_channel == 'Internet'))
    df.groupby('booking_origin')

    # TODO: SAVE DATA TO CLICKHOUSE

