"""S3 service — handles file storage and metadata persistence."""

import os
import json
import boto3
from botocore.exceptions import ClientError

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class S3Service:
    """Manages S3 interactions for datasets, metadata, and query records."""

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME", "lakechat-datasets")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        if ENVIRONMENT == "development":
            self.client = boto3.client("s3", region_name=self.region)
        else:
            self.client = boto3.client("s3")

    # ── File operations ──────────────────────────────────────────────

    def upload_file(self, content: bytes, key: str, file_type: str):
        """Upload file bytes to S3."""
        content_types = {
            "csv": "text/csv",
            "json": "application/json",
            "parquet": "application/octet-stream",
        }
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=content_types.get(file_type, "application/octet-stream"),
        )

    def download_file(self, key: str) -> bytes:
        """Download file bytes from S3."""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def delete_file(self, key: str):
        """Delete a file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except ClientError:
            pass

    # ── Dataset metadata ─────────────────────────────────────────────

    def save_dataset_metadata(self, dataset_id: str, metadata: dict):
        """Save dataset metadata as a JSON file in S3."""
        key = f"metadata/datasets/{dataset_id}.json"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(metadata, default=str),
            ContentType="application/json",
        )

    def get_dataset_metadata(self, dataset_id: str) -> dict | None:
        """Retrieve dataset metadata from S3."""
        key = f"metadata/datasets/{dataset_id}.json"
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read())
        except ClientError:
            return None

    def list_dataset_metadata(self) -> list:
        """List all dataset metadata entries."""
        prefix = "metadata/datasets/"
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            datasets = []
            for obj in response.get("Contents", []):
                data = self.client.get_object(Bucket=self.bucket, Key=obj["Key"])
                datasets.append(json.loads(data["Body"].read()))
            return datasets
        except ClientError:
            return []

    def delete_dataset_metadata(self, dataset_id: str):
        """Delete dataset metadata."""
        key = f"metadata/datasets/{dataset_id}.json"
        self.delete_file(key)

    # ── Query records ────────────────────────────────────────────────

    def save_query_record(self, query_id: str, record: dict):
        """Save a query record."""
        key = f"metadata/queries/{query_id}.json"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(record, default=str),
            ContentType="application/json",
        )

    def get_query_record(self, query_id: str) -> dict | None:
        """Retrieve a query record."""
        key = f"metadata/queries/{query_id}.json"
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read())
        except ClientError:
            return None

    def list_query_records(self) -> list:
        """List all query records."""
        prefix = "metadata/queries/"
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            records = []
            for obj in response.get("Contents", []):
                data = self.client.get_object(Bucket=self.bucket, Key=obj["Key"])
                records.append(json.loads(data["Body"].read()))
            return records
        except ClientError:
            return []
