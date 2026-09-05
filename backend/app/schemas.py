from typing import List, Optional

from pydantic import BaseModel


class StockBase(BaseModel):
    symbol: str
    name: str
    sector: str
    price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    volume: int
    avg_volume: int
    day_change_pct: float
    week_change_pct: float
    month_change_pct: float
    score: float
    signal: str
    summary: str


class StockCreate(StockBase):
    pass


class StockOut(StockBase):
    id: int

    class Config:
        from_attributes = True


class Opportunity(BaseModel):
    symbol: str
    name: str
    sector: str
    price: float
    signal: str
    score: float
    reason: str
    risk_level: str


class ComparisonItem(BaseModel):
    symbol: str
    name: str
    price: float
    score: float
    signal: str
    day_change_pct: float
    pe_ratio: Optional[float]


class AnalystResponse(BaseModel):
    symbol: str
    current_price: float
    signal: str
    score: float
    summary: str
    bullet_points: List[str]


class RAGSearchResult(BaseModel):
    title: str
    content: str
    score: float
