import logging
import httpx
import tempfile
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app import config
from urllib.parse import urlparse, urlunparse


def format_s3_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.rstrip("/").split("/")
    last_part = path_parts[-1]

    if last_part == "s3":
        # Supabase urls have s3 as the end of their URL.
        # but we need a different url for the public url.
        new_path = "/".join(path_parts[:-1])
        new_url = urlunparse(parsed_url._replace(path=new_path))
        return str(new_url) + "/object/public"

    # locally we don't do anything to the url.
    return url


# Create the S3 client with the correct configuration
s3_client = boto3.client(
    "s3",
    endpoint_url=config.STORAGE_HOST,
    aws_access_key_id=config.STORAGE_ACCESS_KEY,
    aws_secret_access_key=config.STORAGE_SECRET_KEY,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)


def upload_image(url: str) -> str | None:
    # Given an file_url it'll download it then upload it to the bucket + filename.
    filename = f"{uuid4()}.webp"
    bucket_name = "imagesv3"
    logging.info(
        f"File from '{url}' is uploading as '{filename}' to bucket '{bucket_name}'"
    )

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name, ACL="public-read")

    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        with tempfile.NamedTemporaryFile() as tmp_file:
            for chunk in response.iter_bytes():
                tmp_file.write(chunk)

            try:
                tmp_file.seek(0)
                s3_client.upload_fileobj(tmp_file, bucket_name, filename)

                final_url = (
                    f"{format_s3_url(config.STORAGE_HOST)}/{bucket_name}/{filename}"
                )

                logging.info(
                    f"File from '{url}' is successfully uploaded as '{filename}' to bucket '{bucket_name}' with location: {final_url}"
                )

                return final_url
            except:
                logging.exception(
                    f"File from '{url}' failed to upload as '{filename}' to bucket '{bucket_name}'."
                )
                raise
