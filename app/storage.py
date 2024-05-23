import logging
import httpx
import tempfile
from uuid import uuid4

from app.utils import is_dev
from minio import Minio
from minio.error import S3Error
from app import config

is_minio_secure = not is_dev()

client = Minio(
    config.STORAGE_HOST,
    access_key=config.STORAGE_ACCESS_KEY,
    secret_key=config.STORAGE_SECRET_KEY,
    secure=is_minio_secure,
)


def upload_image(url: str) -> str | None:
    # Given an file_url it'll download it then upload it to the bucket + filename.
    filename = f"{uuid4()}.webp"
    bucket_name = "images"
    logging.info(
        f"File from '{url}' is uploading as '{filename}' to bucket '{bucket_name}'"
    )

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        with tempfile.NamedTemporaryFile() as tmp_file:
            for chunk in response.iter_bytes():
                tmp_file.write(chunk)

            try:
                client.fput_object(bucket_name, filename, tmp_file.name)

                scheme = "https" if is_minio_secure else "http"
                final_url = (
                    f"{scheme}://{config.STORAGE_HOST}/{bucket_name}/{tmp_file.name}"
                )

                logging.info(
                    f"File from '{url}' is successfully uploaded as '{filename}' to bucket '{bucket_name}' with location: {final_url}"
                )

                return final_url

            except S3Error:
                logging.exception(
                    f"File from '{url}' is failed to upload as '{filename}' to bucket '{bucket_name}'."
                )
