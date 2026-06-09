"""Mood — sentiment as orthogonal-to-price signal agent."""
from __future__ import annotations

from typing import Any

from ..shared.base import GlassBoxAgent
from ..shared.tools import collect_provenance, elfa_sentiment


class Mood(GlassBoxAgent):
    name = "mood"

    async def gather_context(self, market_id: str) -> dict[str, Any]:
        base_asset = market_id.split("/")[0] if "/" in market_id else market_id

        sentiment_24h = await elfa_sentiment(base_asset, lookback_hours=24)
        sentiment_7d = await elfa_sentiment(base_asset, lookback_hours=24 * 7)

        return {
            "market_id": market_id,
            "asset": base_asset,
            "sentiment_24h": sentiment_24h,
            "sentiment_7d": sentiment_7d,
            "note": (
                "Compute sentiment magnitude × (1 - correlation_with_price). "
                "High orthogonal value = decoupled from price = leading indicator."
            ),
            "_provenance": collect_provenance(sentiment_24h, sentiment_7d),
        }
