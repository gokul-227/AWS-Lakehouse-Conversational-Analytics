"""Dataset management API routes."""

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel

from services.s3_service import S3Service
from services.athena_service import AthenaService
from utils.helpers import infer_schema, detect_file_type, parse_preview_rows
from utils.auth import get_current_user
from utils.logger import log_event

router = APIRouter()
s3 = S3Service()
athena = AthenaService()


class DatasetResponse(BaseModel):
    dataset_id: str
    name: str
    file_type: str
    size_bytes: int
    row_count: int
    columns: list
    s3_key: str
    created_at: str
    status: str


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a dataset file (CSV, JSON, or Parquet) to the data lake."""
    file_type = detect_file_type(file.filename)
    if file_type not in ("csv", "json", "parquet"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload CSV, JSON, or Parquet.",
        )

    dataset_id = str(uuid.uuid4())[:8]
    contents = await file.read()
    size_bytes = len(contents)

    if size_bytes == 0:
        raise HTTPException(status_code=400, detail="File is empty.")

    if size_bytes > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit.")

    schema, row_count, df = infer_schema(contents, file_type, file.filename)
    safe_name = file.filename.rsplit(".", 1)[0].lower().replace(" ", "_").replace("-", "_")
    s3_key = f"datasets/{dataset_id}/{file.filename}"

    try:
        s3.upload_file(contents, s3_key, file_type)
        table_name = f"{safe_name}_{dataset_id}"
        athena.create_external_table(table_name, schema, s3_key, file_type)

        metadata = {
            "dataset_id": dataset_id,
            "name": file.filename,
            "table_name": table_name,
            "file_type": file_type,
            "size_bytes": size_bytes,
            "row_count": row_count,
            "columns": [col["name"] for col in schema],
            "schema": schema,
            "s3_key": s3_key,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        s3.save_dataset_metadata(dataset_id, metadata)
        
        log_event("UPLOAD_DATASET", "success", current_user.get("sub"), {"dataset_id": dataset_id, "file": file.filename})
        return DatasetResponse(**{k: v for k, v in metadata.items() if k in DatasetResponse.model_fields})
    except Exception as e:
        log_event("UPLOAD_DATASET", "error", current_user.get("sub"), {"error": str(e), "file": file.filename})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_datasets(current_user: dict = Depends(get_current_user)):
    """List all uploaded datasets."""
    datasets = s3.list_dataset_metadata()
    return {"datasets": datasets, "total": len(datasets)}


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """Get dataset details by ID."""
    metadata = s3.get_dataset_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return metadata


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: str, 
    rows: int = Query(default=10, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Preview sample rows from a dataset."""
    metadata = s3.get_dataset_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    content = s3.download_file(metadata["s3_key"])
    preview = parse_preview_rows(content, metadata["file_type"], rows)
    return {"dataset_id": dataset_id, "rows": preview, "total_rows": metadata["row_count"]}


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a dataset and its associated resources."""
    metadata = s3.get_dataset_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    s3.delete_file(metadata["s3_key"])
    athena.drop_table(metadata.get("table_name", ""))
    s3.delete_dataset_metadata(dataset_id)

    return {"message": f"Dataset {dataset_id} deleted successfully."}
