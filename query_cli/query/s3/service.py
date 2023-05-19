
import boto3


ADDRESS = "http://localhost:9000"
HIVE_BUCKET_NAME = "hive"


def ensure_hive_bucket() -> None:
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id='minio_root_user',
        aws_secret_access_key='minio_root_password123',
        endpoint_url=ADDRESS,
    )

    # Call S3 to list current buckets
    response = s3_client.list_buckets()

    # Get a list of all bucket names from the response
    if HIVE_BUCKET_NAME in [bucket['Name'] for bucket in response['Buckets']]:
        return

    s3_client.create_bucket(Bucket=HIVE_BUCKET_NAME)
