from __future__ import annotations

from typing import Dict, List


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def compute_score(stock: Dict) -> float:
    momentum = clamp(stock.get("week_change_pct", 0) * 8 + stock.get("month_change_pct", 0) * 2.5)
    valuation = 100 - min(abs(stock.get("pe_ratio", 20) - 25) * 2, 45)
    volume_score = clamp((stock.get("volume", 0) / max(stock.get("avg_volume", 1), 1)) * 40)
    trend_bias = clamp((stock.get("day_change_pct", 0) * 8) + (stock.get("week_change_pct", 0) * 3), 0, 100)
    score = round((0.4 * momentum) + (0.2 * valuation) + (0.2 * volume_score) + (0.2 * trend_bias), 2)
    return round(clamp(score), 2)


def categorize_signal(stock: Dict) -> str:
    if stock.get("score", 0) >= 80:
        return "Strong Buy"
    if stock.get("score", 0) >= 65:
        return "Buy"
    if stock.get("score", 0) >= 50:
        return "Watch"
    if stock.get("score", 0) >= 35:
        return "Hold"
    return "Avoid"


def score_stock(stock: Dict) -> Dict:
    score = compute_score(stock)
    stock["score"] = score
    stock["signal"] = categorize_signal(stock)
    stock["summary"] = (
        f"{stock['name']} is tracking a {stock['signal']} setup with momentum of "
        f"{stock.get('week_change_pct', 0):.2f}% over the past week and a price of ${stock['price']:.2f}."
    )
    return stock


def rank_opportunities(stocks: List[Dict], limit: int = 5) -> List[Dict]:
    scored = [score_stock(stock) for stock in stocks]
    ranked = sorted(scored, key=lambda item: item["score"], reverse=True)
    opportunities = []
    for stock in ranked[:limit]:
        reason = (
            f"Momentum is strong in the {stock['sector']} sector, volume is above its average, "
            f"and the short-term trend remains positive."
        )
        risk_level = "Medium"
        if stock["score"] >= 80:
            risk_level = "Medium"
        elif stock["score"] < 50:
            risk_level = "High"

        opportunities.append(
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "sector": stock["sector"],
                "price": stock["price"],
                "signal": stock["signal"],
                "score": stock["score"],
                "reason": reason,
                "risk_level": risk_level,
            }
        )
    return opportunities


def build_ai_analyst(stock: Dict) -> Dict:
    signal = stock.get("signal", "Watch")
    score = stock.get("score", 0)
    summary = (
        f"{stock['name']} ({stock['symbol']}) is currently showing a {signal.lower()} bias. "
        f"The stock trades at ${stock['price']:.2f}, is moving {stock.get('week_change_pct', 0):.2f}% over the past week, "
        f"and the combined score is {score:.2f}/100."
    )
    bullet_points = [
        f"Price momentum: {stock.get('week_change_pct', 0):.2f}% weekly change",
        f"Relative volume: {stock.get('volume', 0) / max(stock.get('avg_volume', 1), 1):.2f}x average",
        f"Sector context: {stock['sector']} remains in an active trading regime",
    ]
    return {
        "symbol": stock["symbol"],
        "current_price": stock["price"],
        "signal": signal,
        "score": score,
        "summary": summary,
        "bullet_points": bullet_points,
    }
