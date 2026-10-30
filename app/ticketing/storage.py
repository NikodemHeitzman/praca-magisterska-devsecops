"""Attachment objects in S3 (docs/adr/0006-przechowywanie-zalacznikow-s3.md)."""

from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

import boto3
from botocore.client import BaseClient

from ticketing.config import get_settings


@lru_cache
def get_s3_client() -> BaseClient:
    # endpoint_url: moto locally and in CI, None (real S3 through the IAM role) in AWS.
    return boto3.client("s3", endpoint_url=get_settings().s3_endpoint_url)


def object_key(ticket_id: int, filename: str) -> str:
    return f"tickets/{ticket_id}/{filename}"


def upload(key: str, content: bytes, content_type: str) -> None:
    get_s3_client().put_object(
        Bucket=get_settings().s3_bucket, Key=key, Body=content, ContentType=content_type
    )


def download(key: str, path: Path) -> None:
    get_s3_client().download_file(get_settings().s3_bucket, key, str(path))


def delete(keys: Iterable[str]) -> None:
    objects = [{"Key": key} for key in keys]
    if objects:
        get_s3_client().delete_objects(
            Bucket=get_settings().s3_bucket, Delete={"Objects": objects, "Quiet": True}
        )
