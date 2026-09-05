from sqlalchemy import Boolean, Column, Float, Integer, String

from app.db import Base


class StockRecord(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=False)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    volume = Column(Integer, nullable=False)
    avg_volume = Column(Integer, nullable=False)
    day_change_pct = Column(Float, nullable=False)
    week_change_pct = Column(Float, nullable=False)
    month_change_pct = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    signal = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
