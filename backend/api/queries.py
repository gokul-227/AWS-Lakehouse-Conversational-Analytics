"""Query API routes — natural language to SQL."""

import uuid
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.s3_service import S3Service
from services.athena_service import AthenaService
from ai.sql_generator import SQLGenerator
from ai.chart_recommender import ChartRecommender
from utils.auth import get_current_user
from utils.logger import log_event

router = APIRouter()
s3 = S3Service()
athena = AthenaService()
sql_gen = SQLGenerator()
chart_rec = ChartRecommender()


class QueryRequest(BaseModel):
    question: str
    dataset_id: str


class QueryResponse(BaseModel):
    query_id: str
    question: str
    generated_sql: str
    results: list
    columns: list
    row_count: int
    chart_type: str
    chart_config: dict
    execution_time_ms: int
    created_at: str


@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Convert a natural language question to SQL and execute it."""
    metadata = s3.get_dataset_metadata(request.dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    table_name = metadata.get("table_name", "")
    schema = metadata.get("schema", [])
    columns = metadata.get("columns", [])

    try:
        generated_sql = sql_gen.generate(
            question=request.question,
            table_name=table_name,
            schema=schema,
            sample_columns=columns,
        )
    except Exception as e:
        log_event("SQL_GENERATION", "error", current_user.get("sub"), {"error": str(e), "question": request.question})
        raise HTTPException(status_code=400, detail=f"Could not generate SQL: {str(e)}")

    start_time = time.time()
    try:
        results, result_columns = athena.execute_query(generated_sql)
    except Exception as e:
        log_event("QUERY_EXECUTION", "error", current_user.get("sub"), {"error": str(e), "sql": generated_sql})
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
    execution_time_ms = int((time.time() - start_time) * 1000)

    chart_type, chart_config = chart_rec.recommend(
        question=request.question,
        columns=result_columns,
        results=results,
    )

    query_id = str(uuid.uuid4())[:8]
    query_record = {
        "query_id": query_id,
        "question": request.question,
        "generated_sql": generated_sql,
        "dataset_id": request.dataset_id,
        "results": results[:500],
        "columns": result_columns,
        "row_count": len(results),
        "chart_type": chart_type,
        "chart_config": chart_config,
        "execution_time_ms": execution_time_ms,
        "created_at": datetime.utcnow().isoformat(),
    }
    s3.save_query_record(query_id, query_record)
    log_event("ASK_QUESTION", "success", current_user.get("sub"), {"query_id": query_id, "question": request.question})

    return QueryResponse(**query_record)


@router.get("/history")
async def query_history(
    dataset_id: Optional[str] = None, 
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve query history."""
    records = s3.list_query_records()
    if dataset_id:
        records = [r for r in records if r.get("dataset_id") == dataset_id]
    records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"queries": records[:limit], "total": len(records)}


@router.get("/{query_id}")
async def get_query(query_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific query record."""
    record = s3.get_query_record(query_id)
    if not record:
        raise HTTPException(status_code=404, detail="Query not found.")
    return record
