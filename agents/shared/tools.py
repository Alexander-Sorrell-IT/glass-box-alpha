"""External data tool functions for the 4 agents.

Mock-first design: each function returns realistic-shape data even without API
keys, so the orchestrator and frontend can be developed in isolation. When
NANSEN_API_KEY and ELFA_API_KEY are set in env, real calls activate.
"""
from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from loguru import logger


_NANSEN_BASE = "https://api.nansen.ai"
_ELFA_BASE = "https://api.elfa.ai"


async def nansen_smart_money_flows(asset: str, lookback_hours: int = 24) -> dict[str, Any]:
    """Pull smart-money wallet flow data for an asset on Mantle.

    Returns: {"net_flow_usd": float, "wallet_count": int, "top_wallets": [...]}
    """
    api_key = os.environ.get("NANSEN_API_KEY")
    if not api_key:
        return _mock_nansen_flows(asset, lookback_hours)

    url = f"{_NANSEN_BASE}/v1/smart-money/flows"
    params = {"asset": asset, "chain": "mantle", "hours": lookback_hours}
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            logger.warning(f"Nansen API error, falling back to mock: {e}")
            return _mock_nansen_flows(asset, lookback_hours)


async def nansen_wallet_history(wallet: str, days: int = 30) -> list[dict[str, Any]]:
    """Historical trades for a specific wallet on Mantle."""
    api_key = os.environ.get("NANSEN_API_KEY")
    if not api_key:
        return _mock_wallet_history(wallet, days)

    url = f"{_NANSEN_BASE}/v1/wallets/{wallet}/history"
    params = {"chain": "mantle", "days": days}
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json().get("trades", [])
        except httpx.HTTPError as e:
            logger.warning(f"Nansen history error, falling back to mock: {e}")
            return _mock_wallet_history(wallet, days)


async def elfa_sentiment(ticker: str, lookback_hours: int = 24) -> dict[str, Any]:
    """Sentiment time-series for a ticker via Elfa AI.

    Returns: {"avg_score": float, "delta_24h": float, "volume": int, "series": [...]}
    """
    api_key = os.environ.get("ELFA_API_KEY")
    if not api_key:
        return _mock_elfa_sentiment(ticker, lookback_hours)

    url = f"{_ELFA_BASE}/v1/sentiment"
    params = {"ticker": ticker, "hours": lookback_hours}
    headers = {"x-api-key": api_key}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            logger.warning(f"Elfa API error, falling back to mock: {e}")
            return _mock_elfa_sentiment(ticker, lookback_hours)


async def mantle_dex_price(asset_pair: str) -> dict[str, Any]:
    """Spot price + 24h volume from Mantle DEX aggregator (DeFiLlama fallback)."""
    url = f"https://api.llama.fi/v2/historicalChainTvl/mantle"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            # Simplified: pull latest TVL as proxy for "market context"
            data = r.json()
            return {"pair": asset_pair, "latest_tvl_usd": data[-1].get("tvl", 0) if data else 0}
        except (httpx.HTTPError, IndexError, KeyError) as e:
            logger.warning(f"DeFiLlama error: {e}")
            return {"pair": asset_pair, "latest_tvl_usd": 0}


# ---------- Mock data (used until API keys set) ----------

def _mock_nansen_flows(asset: str, lookback_hours: int) -> dict[str, Any]:
    rng = random.Random(f"{asset}-{lookback_hours}")
    return {
        "asset": asset,
        "chain": "mantle",
        "lookback_hours": lookback_hours,
        "net_flow_usd": rng.uniform(-2_000_000, 2_000_000),
        "wallet_count": rng.randint(8, 40),
        "top_wallets": [
            {
                "address": f"0x{rng.getrandbits(160):040x}",
                "net_usd": rng.uniform(-500_000, 500_000),
                "win_rate_30d": round(rng.uniform(0.45, 0.78), 3),
            }
            for _ in range(5)
        ],
        "_mock": True,
    }


def _mock_wallet_history(wallet: str, days: int) -> list[dict[str, Any]]:
    rng = random.Random(wallet)
    now = datetime.now(timezone.utc)
    trades = []
    for i in range(rng.randint(8, 24)):
        ts = now - timedelta(hours=rng.uniform(0, days * 24))
        trades.append({
            "timestamp": ts.isoformat(),
            "asset_in": rng.choice(["USDC", "mETH", "MNT", "USDY", "fBTC"]),
            "asset_out": rng.choice(["USDC", "mETH", "MNT", "USDY", "fBTC"]),
            "amount_usd": rng.uniform(5_000, 250_000),
            "pnl_realized": rng.uniform(-0.15, 0.22),
        })
    return sorted(trades, key=lambda t: t["timestamp"])


def _mock_elfa_sentiment(ticker: str, lookback_hours: int) -> dict[str, Any]:
    rng = random.Random(f"elfa-{ticker}-{lookback_hours}")
    series = [
        {"hour": i, "score": round(rng.uniform(-1.0, 1.0), 3)}
        for i in range(lookback_hours)
    ]
    return {
        "ticker": ticker,
        "lookback_hours": lookback_hours,
        "avg_score": round(sum(s["score"] for s in series) / len(series), 3),
        "delta_24h": round(rng.uniform(-0.4, 0.4), 3),
        "volume": rng.randint(120, 4_500),
        "series": series,
        "_mock": True,
    }
