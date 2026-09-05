import json
from pathlib import Path
from typing import Dict, List, Optional

from app.services.scoring_engine import build_ai_analyst, rank_opportunities, score_stock

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_stocks.json"


def load_stocks() -> List[Dict]:
    try:
        from app.db import fetch_stocks_db

        rows = fetch_stocks_db()
        if rows:
            stocks = []
            for row in rows:
                stocks.append({
                    "id": row.id,
                    "symbol": row.symbol,
                    "name": row.name,
                    "sector": row.sector,
                    "price": row.price,
                    "market_cap": row.market_cap,
                    "pe_ratio": row.pe_ratio,
                    "dividend_yield": row.dividend_yield,
                    "volume": row.volume,
                    "avg_volume": row.avg_volume,
                    "day_change_pct": row.day_change_pct,
                    "week_change_pct": row.week_change_pct,
                    "month_change_pct": row.month_change_pct,
                    "score": row.score,
                    "signal": row.signal,
                    "summary": row.summary,
                })
            return stocks
    except Exception:
        pass

    with DATA_FILE.open("r", encoding="utf-8") as file:
        stocks = json.load(file)

    unique_stocks = {}
    for stock in stocks:
        symbol = stock["symbol"].upper()
        if symbol not in unique_stocks:
            unique_stocks[symbol] = score_stock(stock)

    scored = list(unique_stocks.values())
    for index, stock in enumerate(scored, start=1):
        stock["id"] = index
    return scored


def get_stock_by_symbol(symbol: str) -> Optional[Dict]:
    for stock in load_stocks():
        if stock["symbol"].upper() == symbol.upper():
            return stock
    return None


def get_opportunities(limit: int = 5) -> List[Dict]:
    return rank_opportunities(load_stocks(), limit=limit)


def compare_stocks(symbols: List[str]) -> List[Dict]:
    items = []
    for symbol in symbols:
        stock = get_stock_by_symbol(symbol)
        if stock:
            items.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "price": stock["price"],
                "score": stock["score"],
                "signal": stock["signal"],
                "day_change_pct": stock.get("day_change_pct", 0),
                "pe_ratio": stock.get("pe_ratio"),
            })
    return items


def build_portfolio_summary(symbols: List[str]) -> Dict:
    items = compare_stocks(symbols)
    if not items:
        return {
            "symbols": [],
            "average_score": 0.0,
            "top_signal": "None",
            "total_value": 0.0,
            "best_symbol": None,
        }

    average_score = round(sum(item["score"] for item in items) / len(items), 2)
    top_stock = max(items, key=lambda item: item["score"])
    total_value = round(sum(item["price"] for item in items), 2)
    signal_counts = {}
    for item in items:
        signal_counts[item["signal"]] = signal_counts.get(item["signal"], 0) + 1

    top_signal = max(signal_counts.items(), key=lambda entry: entry[1])[0]
    return {
        "symbols": [item["symbol"] for item in items],
        "average_score": average_score,
        "top_signal": top_signal,
        "total_value": total_value,
        "best_symbol": top_stock["symbol"],
    }


def create_analyst_summary(symbol: str) -> Dict:
    stock = get_stock_by_symbol(symbol)
    if not stock:
        raise ValueError(f"Unknown symbol: {symbol}")
    return build_ai_analyst(stock)
