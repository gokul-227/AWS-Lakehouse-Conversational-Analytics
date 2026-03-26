"""
LakeChat AI — FastAPI Backend Entry Point
Conversational analytics engine for querying data lakes via natural language.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()

from api.datasets import router as datasets_router
from api.queries import router as queries_router
from api.health import router as health_router

app = FastAPI(
    title="LakeChat AI",
    description="Conversational AI for querying data lakes with natural language",
    version="1.0.0",
)

cors_origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(datasets_router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(queries_router, prefix="/api/queries", tags=["Queries"])

# AWS Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
