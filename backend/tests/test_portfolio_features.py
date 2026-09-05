from app.services.sample_data import build_portfolio_summary, compare_stocks


def test_compare_stocks_returns_selected_symbols():
    result = compare_stocks(["AAPL", "MSFT", "NVDA"])
    assert len(result) == 3
    assert {item["symbol"] for item in result} == {"AAPL", "MSFT", "NVDA"}


def test_build_portfolio_summary_has_expected_fields():
    summary = build_portfolio_summary(["AAPL", "MSFT", "NVDA"])
    assert summary["average_score"] > 0
    assert summary["best_symbol"] in {"AAPL", "MSFT", "NVDA"}
    assert len(summary["symbols"]) == 3
