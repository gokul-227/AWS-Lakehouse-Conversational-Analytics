# LakeChat AI Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAKECHAT AI                              │
│               Conversational Data Lake Analytics                │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────────────┐     ┌──────────────┐
│   Browser    │────▶│   S3 Static Hosting  │     │   React +    │
│   (User)     │     │   (Frontend Assets)  │◀────│   Vite +     │
│              │     └──────────────────────┘     │   Tailwind   │
└──────┬───────┘                                  └──────────────┘
       │
       │ API Requests
       ▼
┌──────────────────────┐
│    API Gateway       │
│    (HTTP API)        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐     ┌──────────────────────┐
│   Lambda Function    │────▶│   S3 Bucket          │
│   (FastAPI + Mangum) │     │   (Datasets +        │
│                      │     │    Metadata)          │
│   ┌──────────────┐   │     └──────────────────────┘
│   │ SQL Generator│   │
│   │ (AI Engine)  │   │     ┌──────────────────────┐
│   └──────────────┘   │────▶│   Athena             │
│   ┌──────────────┐   │     │   (SQL Execution)    │
│   │ Chart        │   │     └──────────┬───────────┘
│   │ Recommender  │   │                │
│   └──────────────┘   │                ▼
└──────────────────────┘     ┌──────────────────────┐
                             │  Glue Data Catalog   │
                             │  (Table Definitions) │
                             └──────────────────────┘

Data Flow:
1. User uploads CSV/JSON/Parquet ──▶ S3
2. Schema inferred ──▶ Athena DDL creates table in Glue Catalog
3. User asks natural language question
4. AI SQL Generator converts to SQL
5. Athena executes query on S3 data
6. Chart Recommender suggests visualization
7. Results + chart returned to user
```
