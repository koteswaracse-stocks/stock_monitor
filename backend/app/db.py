from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


def _build_engine():
    database_url = settings.database_url
    if database_url.startswith("postgresql"):
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            return engine
        except Exception:
            fallback = "sqlite:///" + str(Path(__file__).resolve().parent.parent / "stock_monitor.db")
            return create_engine(fallback, connect_args={"check_same_thread": False})
    return create_engine(database_url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_stock_data(db):
    from app.models import StockRecord
    from app.services.sample_data import load_stocks

    if db.query(StockRecord).count() > 0:
        return db.query(StockRecord).count()

    records = []
    for stock in load_stocks():
        records.append(
            StockRecord(
                symbol=stock["symbol"],
                name=stock["name"],
                sector=stock["sector"],
                price=stock["price"],
                market_cap=stock["market_cap"],
                pe_ratio=stock.get("pe_ratio"),
                dividend_yield=stock.get("dividend_yield"),
                volume=stock["volume"],
                avg_volume=stock["avg_volume"],
                day_change_pct=stock["day_change_pct"],
                week_change_pct=stock["week_change_pct"],
                month_change_pct=stock["month_change_pct"],
                score=stock["score"],
                signal=stock["signal"],
                summary=stock["summary"],
                is_active=True,
            )
        )

    db.add_all(records)
    db.commit()
    return len(records)


def fetch_stocks_db():
    from app.models import StockRecord

    with SessionLocal() as db:
        rows = db.query(StockRecord).filter(StockRecord.is_active.is_(True)).all()
        return rows


def fetch_stock_by_symbol_db(symbol: str):
    from app.models import StockRecord

    with SessionLocal() as db:
        return db.query(StockRecord).filter(StockRecord.symbol == symbol.upper()).first()


def init_db():
    # Import models here to ensure SQLAlchemy metadata is registered.
    from app.models import StockRecord

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_stock_data(db)
