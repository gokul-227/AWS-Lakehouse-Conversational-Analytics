"""Utility helpers — schema inference, file detection, row parsing."""

import io
import json
import pandas as pd
from typing import Optional


def detect_file_type(filename: str) -> str:
    """Detect file type from extension."""
    if not filename:
        return "unknown"
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in ("csv", "json", "parquet") else "unknown"


def infer_schema(content: bytes, file_type: str, filename: str = "") -> tuple[list, int, Optional[pd.DataFrame]]:
    """
    Infer the schema from file content.

    Returns:
        Tuple of (schema, row_count, dataframe).
        schema is a list of {"name": str, "type": str} dicts.
    """
    try:
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(content))
        elif file_type == "json":
            df = pd.read_json(io.BytesIO(content))
        elif file_type == "parquet":
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise ValueError(f"Failed to parse file: {str(e)}")

    # Clean column names
    df.columns = [
        col.strip().replace(" ", "_").replace("-", "_").lower()
        for col in df.columns
    ]

    schema = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        schema.append({"name": col, "type": dtype})

    return schema, len(df), df


def parse_preview_rows(content: bytes, file_type: str, max_rows: int = 10) -> list:
    """Parse the first N rows for preview display."""
    try:
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(content), nrows=max_rows)
        elif file_type == "json":
            df = pd.read_json(io.BytesIO(content))
            df = df.head(max_rows)
        elif file_type == "parquet":
            df = pd.read_parquet(io.BytesIO(content))
            df = df.head(max_rows)
        else:
            return []

        df.columns = [
            col.strip().replace(" ", "_").replace("-", "_").lower()
            for col in df.columns
        ]

        return json.loads(df.to_json(orient="records", date_format="iso"))
    except Exception:
        return []
