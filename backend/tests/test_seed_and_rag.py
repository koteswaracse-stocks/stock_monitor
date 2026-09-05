from app.db import SessionLocal, seed_stock_data
from app.models import StockRecord
from app.services.rag_service import RAGService


def test_seed_stock_data_adds_records():
    db = SessionLocal()
    try:
        db.query(StockRecord).delete()
        inserted = seed_stock_data(db)
        assert inserted > 0
        assert db.query(StockRecord).count() > 0
    finally:
        db.close()


def test_rag_search_returns_relevant_results():
    service = RAGService()
    results = service.search("momentum and volume")
    assert len(results) > 0
    assert results[0]["title"]
