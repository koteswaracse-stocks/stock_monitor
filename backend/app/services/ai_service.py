from __future__ import annotations

from typing import Any, Dict, Optional

from openai import OpenAI

from app.config import settings
from app.services.scoring_engine import build_ai_analyst


class AIAnalystService:
    def __init__(self) -> None:
        self.client = None
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_summary(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        if self.client is None:
            return build_ai_analyst(stock)

        prompt = (
            "You are a cautious stock analyst. Provide a concise investment assessment for the provided stock "
            "using fundamentals, momentum, volume support, and market context. Keep the response as valid JSON "
            "with keys: symbol, current_price, signal, score, summary, bullet_points."
            f"\nStock data: {stock}"
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a senior investment analyst."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"
            payload = self._parse_json(content)
            if payload:
                return payload
        except Exception:
            pass

        return build_ai_analyst(stock)

    @staticmethod
    def _parse_json(raw_content: str) -> Optional[Dict[str, Any]]:
        import json

        try:
            return json.loads(raw_content)
        except Exception:
            return None
