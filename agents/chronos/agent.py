"""Chronos — timeline / historical-analog reasoning agent."""
from __future__ import annotations

from typing import Any

from ..shared.base import GlassBoxAgent
from ..shared.tools import (
    collect_provenance,
    mantle_dex_price,
    mantle_rpc_activity,
    nansen_smart_money_flows,
    nansen_wallet_history,
)


class Chronos(GlassBoxAgent):
    name = "chronos"

    async def gather_context(self, market_id: str) -> dict[str, Any]:
        base_asset = market_id.split("/")[0] if "/" in market_id else market_id

        flows_24h = await nansen_smart_money_flows(base_asset, lookback_hours=24)
        flows_7d = await nansen_smart_money_flows(base_asset, lookback_hours=24 * 7)
        flows_30d = await nansen_smart_money_flows(base_asset, lookback_hours=24 * 30)
        market = await mantle_dex_price(market_id)
        # First-party chain read — the one source that cannot be mocked upstream.
        onchain = await mantle_rpc_activity(base_asset)

        # Pull histories of the top-2 wallets for analog mining
        top_wallets = flows_24h.get("top_wallets", [])[:2]
        wallet_results = [
            await nansen_wallet_history(w["address"], days=30) for w in top_wallets
        ]
        wallet_histories = [r["trades"] for r in wallet_results]

        return {
            "market_id": market_id,
            "flows_24h_net_usd": flows_24h.get("net_flow_usd"),
            "flows_7d_net_usd": flows_7d.get("net_flow_usd"),
            "flows_30d_net_usd": flows_30d.get("net_flow_usd"),
            "top_wallets": top_wallets,
            "top_wallet_histories": wallet_histories,
            "mantle_tvl_context": market,
            "mantle_onchain_activity": onchain,
            # Every source — including each wallet-history call — declares its own liveness.
            "_provenance": collect_provenance(
                flows_24h, flows_7d, flows_30d, market, onchain, *wallet_results
            ),
        }
