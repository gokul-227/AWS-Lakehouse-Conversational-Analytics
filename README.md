# LakeChat AI — Conversational Data Lake Analytics

A modern, serverless web application that lets users upload datasets to an AWS data lake and query them using natural language. The AI engine converts questions into SQL, executes them via Amazon Athena, and returns results with smart chart visualizations.

## 🚀 Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS
- Recharts (Visualization)
- Lucide React (Icons)

### Backend (Serverless)
- Python 3.11 + FastAPI
- Rule-based NL→SQL AI Engine
- Heuristic Chart Recommender
- Mangum (Lambda adapter)

### AWS Services
- **S3** — Dataset storage + frontend hosting
- **Athena** — SQL query execution (free tier: 5GB/month)
- **Glue Data Catalog** — Table definitions
- **Lambda** — Backend compute
- **API Gateway** — HTTP API routing

### Infrastructure
- Terraform (IaC)

## 🏗️ Architecture

```
User ──▶ S3 (Frontend) ──▶ API Gateway ──▶ Lambda (FastAPI)
                                              │
                           ┌──────────────────┼──────────────────┐
                           ▼                  ▼                  ▼
                      S3 (Datasets)     Athena (SQL)     Glue Catalog
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture diagram.

## 📂 Project Structure

```
├── frontend/           # React + Vite + Tailwind
│   └── src/
│       ├── pages/      # Login, Dashboard, Upload, Chat
│       ├── components/ # ChartRenderer, DatasetBrowser, QueryHistory
│       ├── services/   # API client (Axios)
│       └── context/    # Auth context
├── backend/
│   ├── api/            # FastAPI routes (datasets, queries, health)
│   ├── services/       # S3 service, Athena service
│   ├── ai/             # SQL Generator, Chart Recommender
│   └── utils/          # Schema inference, file parsing
├── infra/              # Terraform (S3, Athena, Lambda, API Gateway, IAM)
├── scripts/            # deploy.sh, destroy.sh
├── data/               # Sample datasets
└── docs/               # Architecture diagrams
```

## ✅ Features

- **Dataset Upload** — Drag-and-drop CSV, JSON, or Parquet files
- **Automatic Cataloging** — S3 storage + Glue Data Catalog table creation
- **Natural Language Queries** — Ask questions in plain English
- **AI SQL Generation** — Rule-based NL→SQL with schema awareness
- **Athena Execution** — Serverless SQL on your data lake
- **Smart Visualizations** — Auto-recommended charts (bar, line, pie)
- **SQL Transparency** — View the generated SQL for every query
- **Query History** — Track all past queries with performance metrics
- **Dataset Browser** — Browse uploads with sample row preview
- **Query Performance Metrics** — Execution time tracking

## 🛠 Setup

### Prerequisites

- AWS CLI configured (`aws configure`)
- Terraform v1.0+
- Node.js v18+ & npm
- Python 3.11+

### Local Development

```bash
# Clone
git clone https://github.com/gokul-r-7/AWS-Lakehouse-Conversational-Analytics.git
cd AWS-Lakehouse-Conversational-Analytics

# Backend
cd backend
pip install -r requirements.txt
python main.py
# API runs at http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# UI runs at http://localhost:5173
```

### Deploy to AWS

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Destroy

```bash
chmod +x scripts/destroy.sh
./scripts/destroy.sh
```

## 📡 API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/datasets/upload` | Upload dataset file |
| `GET` | `/api/datasets/` | List all datasets |
| `GET` | `/api/datasets/{id}` | Get dataset details |
| `GET` | `/api/datasets/{id}/preview` | Preview sample rows |
| `DELETE` | `/api/datasets/{id}` | Delete dataset |
| `POST` | `/api/queries/ask` | Ask natural language query |
| `GET` | `/api/queries/history` | Get query history |
| `GET` | `/api/queries/{id}` | Get specific query |

## 📊 Sample Queries

Once you upload the sample sales dataset, try these:
- *"Show total revenue by category"*
- *"What are the top 5 products by quantity?"*
- *"Average price per region"*
- *"Monthly revenue trend"*
- *"How many orders in Electronics?"*

## 🔒 Security

- IAM roles with least privilege
- S3 server-side encryption (AES-256)
- Environment variable configuration
- No hardcoded credentials

## 📄 License

MIT
