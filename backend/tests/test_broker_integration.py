from app.services.broker_service import BrokerService


def test_broker_service_returns_safe_demo_snapshot():
    service = BrokerService()
    snapshot = service.get_account_snapshot()

    assert snapshot["broker"] in {"demo", "robinhood"}
    assert "cash" in snapshot
    assert "positions" in snapshot
    assert isinstance(snapshot["positions"], list)
