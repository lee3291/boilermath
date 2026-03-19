import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()
bucket = os.getenv("AWS_BUCKET_NAME")
region = os.getenv("AWS_REGION")


def upload_image(image_path: str, key: str):

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(image_path, bucket, key)
    except ClientError as e:
        logging.error(e)
        return "Failed"

    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
