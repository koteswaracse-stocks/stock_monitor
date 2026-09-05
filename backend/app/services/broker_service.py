from __future__ import annotations

from typing import Any, Dict, List

import httpx

from app.config import settings


class BrokerService:
    """Secure broker adapter for a future Robinhood or similar account connection.

    This service intentionally defaults to a safe demo mode. It never uses personal
    brokerage credentials unless the user explicitly configures a valid access token
    and a supported broker mode in environment variables.
    """

    def __init__(self) -> None:
        self.mode = (settings.broker_mode or "demo").lower()
        self.token = (settings.robinhood_access_token or "").strip()
        self.base_url = (settings.robinhood_base_url or "https://api.robinhood.com").rstrip("/")

    def get_account_snapshot(self) -> Dict[str, Any]:
        if self.mode == "robinhood" and self.token:
            try:
                return self._fetch_live_robinhood_snapshot()
            except Exception:
                return self._demo_snapshot("robinhood")

        return self._demo_snapshot("demo")

    def get_connection_status(self) -> Dict[str, Any]:
        if self.mode == "robinhood" and not self.token:
            return {
                "broker": "robinhood",
                "status": "not_configured",
                "message": "Set ROBINHOOD_ACCESS_TOKEN to enable live account data.",
            }

        return {
            "broker": self.mode or "demo",
            "status": "ready",
            "message": "Broker adapter is configured for server-side access only.",
        }

    def _demo_snapshot(self, broker_name: str) -> Dict[str, Any]:
        return {
            "broker": broker_name,
            "account_id": "demo-account",
            "account_name": "Demo Robinhood Account",
            "status": "demo_mode",
            "cash": 1250.75,
            "buying_power": 2300.15,
            "equity": 54200.0,
            "day_gain": 182.5,
            "total_value": 55450.75,
            "positions": [
                {
                    "symbol": "AAPL",
                    "quantity": 18,
                    "price": 212.5,
                    "market_value": 3810.0,
                    "day_change_pct": 1.2,
                },
                {
                    "symbol": "MSFT",
                    "quantity": 12,
                    "price": 417.45,
                    "market_value": 5009.4,
                    "day_change_pct": 0.9,
                },
                {
                    "symbol": "NVDA",
                    "quantity": 9,
                    "price": 124.6,
                    "market_value": 1121.4,
                    "day_change_pct": 2.3,
                },
            ],
        }

    def _fetch_live_robinhood_snapshot(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        with httpx.Client(timeout=15.0) as client:
            account_response = client.get(f"{self.base_url}/accounts/", headers=headers)
            account_response.raise_for_status()
            account_data = account_response.json()
            account = (account_data.get("results") or [{}])[0]

            positions_response = client.get(f"{self.base_url}/positions/", headers=headers)
            positions_response.raise_for_status()
            positions_payload = positions_response.json()

            positions: List[Dict[str, Any]] = []
            for item in positions_payload.get("results", []):
                quantity = float(item.get("quantity") or 0)
                if quantity <= 0:
                    continue

                instrument_url = item.get("instrument")
                instrument_data: Dict[str, Any] = {}
                if instrument_url:
                    instrument_response = client.get(instrument_url, headers=headers)
                    if instrument_response.is_success:
                        instrument_data = instrument_response.json()

                symbol = instrument_data.get("symbol", "UNKNOWN")
                price = float(item.get("price") or 0.0)
                market_value = quantity * price
                positions.append(
                    {
                        "symbol": symbol,
                        "quantity": quantity,
                        "price": price,
                        "market_value": market_value,
                        "day_change_pct": float(item.get("day_change_pct") or 0.0),
                    }
                )

            total_value = float(account.get("equity") or 0.0)
            cash = float(account.get("cash") or 0.0)
            buying_power = float(account.get("buying_power") or 0.0)

            return {
                "broker": "robinhood",
                "account_id": account.get("account_id", "unknown"),
                "account_name": account.get("account_name", "Robinhood account"),
                "status": "live",
                "cash": cash,
                "buying_power": buying_power,
                "equity": total_value,
                "day_gain": float(account.get("day_trade_count") or 0.0),
                "total_value": total_value,
                "positions": positions,
            }
