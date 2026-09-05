from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.schemas import AnalystResponse, ComparisonItem, Opportunity, StockOut
from app.services.ai_service import AIAnalystService
from app.services.broker_service import BrokerService
from app.services.rag_service import RAGService
from app.services.sample_data import compare_stocks, create_analyst_summary, get_opportunities, get_stock_by_symbol, load_stocks

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI trading intelligence trial app for stock monitoring and analysis.",
)
app.state.ai_analyst = AIAnalystService()
app.state.rag = RAGService()
app.state.broker = BrokerService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.get("/api/stocks", response_model=List[StockOut])
def get_all_stocks() -> List[dict]:
    return load_stocks()


@app.get("/api/stocks/db")
def get_stock_records() -> list:
    try:
        from app.db import fetch_stocks_db

        rows = fetch_stocks_db()
        return [
            {
                "id": row.id,
                "symbol": row.symbol,
                "name": row.name,
                "sector": row.sector,
                "price": row.price,
                "score": row.score,
                "signal": row.signal,
            }
            for row in rows
        ]
    except Exception:
        return []


@app.get("/api/stocks/{symbol}", response_model=StockOut)
def get_stock(symbol: str) -> dict:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    return stock


@app.get("/api/opportunities", response_model=List[Opportunity])
def opportunities(limit: int = Query(5, ge=1, le=10)) -> List[dict]:
    return get_opportunities(limit=limit)


@app.get("/api/compare", response_model=List[ComparisonItem])
def compare(symbols: List[str] = Query(..., min_length=1)) -> List[dict]:
    items = compare_stocks(symbols)
    if not items:
        raise HTTPException(status_code=404, detail="No matching symbols found")
    return items


@app.get("/api/portfolio")
def portfolio(symbols: List[str] = Query(..., min_length=1)) -> dict:
    from app.services.sample_data import build_portfolio_summary

    summary = build_portfolio_summary(symbols)
    if not summary["symbols"]:
        raise HTTPException(status_code=404, detail="No matching symbols found")
    return summary


@app.get("/api/broker/account")
def broker_account() -> dict:
    return app.state.broker.get_account_snapshot()


@app.get("/api/broker/status")
def broker_status() -> dict:
    return app.state.broker.get_connection_status()


@app.get("/api/analyst/{symbol}", response_model=AnalystResponse)
def analyst(symbol: str) -> dict:
    try:
        stock = get_stock_by_symbol(symbol)
        if not stock:
            raise ValueError(f"Unknown symbol: {symbol}")
        return app.state.ai_analyst.generate_summary(stock)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/rag/search")
def rag_search(query: str, limit: int = Query(3, ge=1, le=5)) -> list:
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")
    return app.state.rag.search(query, k=limit)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
