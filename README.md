# Stock Monitor AI

A full-stack AI trading intelligence trial project using React + FastAPI + PostgreSQL + sample stock data.

## Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL (with SQLite fallback for local development)
- Data layer: sample JSON stock data + scoring engine
- AI layer: mock RAG and OpenAI-ready integration points

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API

- GET /health
- GET /api/stocks
- GET /api/stocks/{symbol}
- GET /api/opportunities
- GET /api/compare?symbols=AAPL&symbols=MSFT
- GET /api/analyst/{symbol}

## Docker

```bash
docker compose up -d postgres
```
