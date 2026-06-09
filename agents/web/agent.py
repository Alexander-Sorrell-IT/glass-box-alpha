"""Web — cross-asset correlation / linked-variable analysis agent."""
from __future__ import annotations

from typing import Any

from ..shared.base import GlassBoxAgent
from ..shared.tools import collect_provenance, nansen_smart_money_flows


_CORRELATED_ASSETS = {
    "mETH": ["ETH", "USDC", "wstETH"],
    "USDY": ["USDC", "Treasuries"],
    "MNT": ["mETH", "USDC", "BTC"],
    "fBTC": ["BTC", "WBTC", "mETH"],
    "USDC": ["MNT", "mETH"],
}


class Web(GlassBoxAgent):
    name = "web"

    async def gather_context(self, market_id: str) -> dict[str, Any]:
        base_asset = market_id.split("/")[0] if "/" in market_id else market_id
        related = _CORRELATED_ASSETS.get(base_asset, [])

        # Pull smart-money flows for the base asset and each related asset
        base_flows = await nansen_smart_money_flows(base_asset, lookback_hours=24)
        related_flows = [
            {"asset": asset, "flows": await nansen_smart_money_flows(asset, lookback_hours=24)}
            for asset in related
        ]

        return {
            "market_id": market_id,
            "base_asset_flows": base_flows,
            "related_asset_flows": related_flows,
            "candidate_linkages": related,
            "note": "Find cross-asset wallet cohorts: when one moves, which others follow within 4h?",
            "_provenance": collect_provenance(base_flows, *(r["flows"] for r in related_flows)),
        }
