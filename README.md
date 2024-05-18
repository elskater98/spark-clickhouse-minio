# MINIO

Firstly, you need to create a ACCESS KEY to work with MINIO via API. So, create it and save the credentials in secure
place.

Secondly, to test the connection you can use the below script:

    # pip install minio

    from minio import Minio

    client = Minio("localhost:9000",
        access_key="<ACCESS_KEY>",
        secret_key="<SECRET_KEY>",
        secure=False ## Set the value True if you use HTTPS.
    )

    client.list_buckets()

Upload `data/spark/datasets/customer_booking.csv` to the bucket `project`.

# Environment Variables

    LOCAL = False
    MINIO_ENDPOINT=http://minio:9000 # container name, ip container or host
    MINIO_DEFAULT_BUCKET=project
    AWS_ACCESS_KEY_ID=Yrg1PWyaB1x1DcaR5wHx # example KEY ID
    AWS_SECRET_ACCESS_KEY=6tJdw7vgxBoKKTQ7ZXpX6ukomcgugzzR4xJQ8Ejo # example ACCESS KEY
    
    CLICKHOUSE_HOST=clickhouse # ip, dns, localhost
    CLICKHOUSE_PORT=8123 # port
    CLICKHOUSE_ADMIN_USER=admin # clichouse user
    CLICKHOUSE_ADMIN_PASSWORD=password # clickhouse pwd
    CLICKHOUSE_DATABASE=project # default database

# Spark

Add env. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `MINIO_ENDPOINT` variables to spark environment.

Inside `spark-master` container execute the command `spark-submit` to run the job :

    spark-submit scripts/main.py