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

# UniswapV2-style Swap(address,uint,uint,uint,uint,address) — the topic the engine
# reads first-party off Mantle. Used here only to prove a chain-read happened.
_V2_SWAP_TOPIC = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"


def _prov(source: str, mode: str, ref: str = "") -> str:
    """Canonical provenance tag committed into the receipt's `data_sources`.

    Format: ``"<source>:<mode>[@<ref>]"`` — e.g. ``"nansen:live"``,
    ``"nansen:mock"``, ``"mantle-rpc:live@block=12345"``. ``mode`` is one of
    ``live | mock | unavailable``. The tag is stamped at the data's ORIGIN
    (never inferred from key-presence), so a key-present-but-call-failed run is
    provably ``mock`` — a receipt can no longer claim mock data was live.
    """
    return f"{source}:{mode}@{ref}" if ref else f"{source}:{mode}"


def collect_provenance(*payloads: Any) -> list[str]:
    """Extract each payload's ``_provenance`` tag (dict payloads only) for the
    agent to hand back to ``base.reason()`` as the receipt's ``data_sources``.
    Order/dedup is normalized downstream in ``reason()`` (sorted set)."""
    return [p["_provenance"] for p in payloads
            if isinstance(p, dict) and isinstance(p.get("_provenance"), str)]


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
            data = r.json()
            data["_provenance"] = _prov("nansen", "live")
            return data
        except httpx.HTTPError as e:
            logger.warning(f"Nansen API error, falling back to mock: {e}")
            return _mock_nansen_flows(asset, lookback_hours)


async def nansen_wallet_history(wallet: str, days: int = 30) -> dict[str, Any]:
    """Historical trades for a specific wallet on Mantle.

    Returns ``{"trades": [...], "_provenance": "nansen-wallets:<mode>"}``. It carries its
    OWN provenance — distinct from the flows endpoint — so a run where flows are live but a
    wallet-history call fell back to mock is committed as exactly that (mixed), never as
    all-live. (Previously this returned a bare list whose mock-ness vanished from the receipt.)
    """
    api_key = os.environ.get("NANSEN_API_KEY")
    if not api_key:
        return {"trades": _mock_wallet_history(wallet, days),
                "_provenance": _prov("nansen-wallets", "mock")}

    url = f"{_NANSEN_BASE}/v1/wallets/{wallet}/history"
    params = {"chain": "mantle", "days": days}
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return {"trades": r.json().get("trades", []),
                    "_provenance": _prov("nansen-wallets", "live")}
        except httpx.HTTPError as e:
            logger.warning(f"Nansen history error, falling back to mock: {e}")
            return {"trades": _mock_wallet_history(wallet, days),
                    "_provenance": _prov("nansen-wallets", "mock")}


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
            data = r.json()
            data["_provenance"] = _prov("elfa", "live")
            return data
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
            return {
                "pair": asset_pair,
                "latest_tvl_usd": data[-1].get("tvl", 0) if data else 0,
                "_provenance": _prov("defillama", "live"),
            }
        except (httpx.HTTPError, IndexError, KeyError) as e:
            logger.warning(f"DeFiLlama error: {e}")
            return {"pair": asset_pair, "latest_tvl_usd": 0,
                    "_provenance": _prov("defillama", "unavailable")}


# ---------- Settlement-grade price read (never silently mock) ----------

_LLAMA_COINS_URL = "https://coins.llama.fi/prices/current/"
# Mantle-mainnet token addresses — mirror of the settler's _resolve_tokens map.
_PRICE_TOKEN_ADDRS = {
    "USDC": "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9",
    "mETH": "0xcDA86A272531e8640cD7F1a92c01839911B90bb0",
    "MNT": "0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8",  # WMNT
    "USDY": "0x5bE26527e817998A7206475496fDE1E68957c5A6",
    "fBTC": "0xC96dE26018A54D51c097160568752c4E3BD6C364",
}
_PRICE_MIN_CONFIDENCE = 0.9  # DeFiLlama's own guidance: confidence < 0.9 is unreliable


def _parse_llama_pair(coins: dict[str, Any], market_id: str) -> dict[str, Any] | None:
    """Pure parse of a DeFiLlama /prices/current ``coins`` payload into a pair price.

    Returns ``{"base_usd", "quote_usd", "price", "timestamp"}`` or None if either leg
    is missing or below the confidence floor. Pure so the parse/pair math is testable
    offline — the house style has no HTTP mocking. Response keys echo the request's
    address casing, so lookups use the exact `_PRICE_TOKEN_ADDRS` strings.
    """
    base_sym, quote_sym = market_id.split("/")
    legs: dict[str, float] = {}
    stamps: list[int] = []
    for leg, sym in (("base_usd", base_sym), ("quote_usd", quote_sym)):
        entry = coins.get(f"mantle:{_PRICE_TOKEN_ADDRS[sym]}")
        if not entry or entry.get("confidence", 0) < _PRICE_MIN_CONFIDENCE:
            return None
        legs[leg] = float(entry["price"])
        stamps.append(int(entry["timestamp"]))
    return {
        **legs,
        "price": legs["base_usd"] / legs["quote_usd"],
        # The OLDER of the two observations — the honest bound on staleness.
        "timestamp": min(stamps),
    }


async def mantle_spot_price(market_id: str) -> dict[str, Any]:
    """Settlement-grade pair spot price (base/quote in quote units) from the keyless
    DeFiLlama coins API.

    This is the read ``settle_round`` grades against, so the mantle-rpc rule applies
    even harder: NO mock fallback, ever — a grade computed on invented prices would be
    a fabricated outcome wearing a real signature. Unknown pair, HTTP failure, missing
    token, or DeFiLlama confidence < 0.9 all declare ``defillama-price:unavailable``
    honestly and let the caller decide to retry. A live read is anchored to the API's
    own observation time: ``defillama-price:live@ts=N``. ``LLAMA_PRICE_URL`` is read at
    CALL time (tests point it at a dead port to exercise the unavailable path offline).
    """
    base_url = os.environ.get("LLAMA_PRICE_URL", _LLAMA_COINS_URL)
    try:
        base_sym, quote_sym = market_id.split("/")
        keys = f"mantle:{_PRICE_TOKEN_ADDRS[base_sym]},mantle:{_PRICE_TOKEN_ADDRS[quote_sym]}"
    except (ValueError, KeyError):
        return {"market_id": market_id, "available": False,
                "_provenance": _prov("defillama-price", "unavailable")}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(base_url + keys)
            r.raise_for_status()
            parsed = _parse_llama_pair(r.json().get("coins", {}), market_id)
    except Exception as e:  # settlement must never grade on faked prices — declare, don't invent
        logger.warning(f"DeFiLlama price unavailable, declaring it (not faking live): {e}")
        return {"market_id": market_id, "available": False,
                "_provenance": _prov("defillama-price", "unavailable")}
    if parsed is None:
        return {"market_id": market_id, "available": False,
                "_provenance": _prov("defillama-price", "unavailable")}
    return {"market_id": market_id, "available": True, **parsed,
            "_provenance": _prov("defillama-price", "live", f"ts={parsed['timestamp']}")}


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
        "_provenance": _prov("nansen", "mock"),
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
        "_provenance": _prov("elfa", "mock"),
    }


# ---------- First-party on-chain read (structurally unmockable) ----------

def _words(data: str) -> list[int]:
    """Split ABI hex data into 32-byte words as ints (engine swap-decode convention)."""
    h = data[2:] if data.startswith("0x") else data
    return [int(h[i:i + 64], 16) for i in range(0, len(h) - len(h) % 64, 64)]


async def _eth_rpc(rpc_url: str, method: str, params: list) -> Any:
    """One JSON-RPC call to OUR OWN Mantle node — no third party in the path, so the
    result cannot be mocked upstream of us. This is what backs `mantle-rpc:live`."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(rpc_url,
                              json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        r.raise_for_status()
        body = r.json()
        if "error" in body:
            raise httpx.HTTPError(str(body["error"]))
        return body["result"]


async def mantle_rpc_activity(asset: str, blocks: int = 300) -> dict[str, Any]:
    """First-party on-chain read: count recent V2 Swap logs straight off our own Mantle
    RPC, anchored to a concrete tip block.

    The point is provenance, not signal sophistication: unlike Nansen/Elfa this path has
    NO third party and NO mock fallback. ``MANTLE_RPC_URL`` is read at CALL time (so a
    `load_dotenv()` that runs after import is still picked up). If it is unset, the node is
    unreachable, or ANY error occurs, it declares ``mantle-rpc:unavailable`` *honestly* and
    never crashes the agent round — it never silently substitutes mock data. So a receipt
    carrying ``mantle-rpc:live@block=N`` proves the decision read the chain itself (an empty
    window is still a real read: ``swap_logs=0`` with a live tag means the chain was queried
    and had no V2 swaps, not a failure). Full per-token V2/V3/LB directional decoding is the
    engine's job — see ../glass-box-engine.
    """
    rpc_url = os.environ.get("MANTLE_RPC_URL", "")
    if not rpc_url:
        return {"asset": asset, "available": False,
                "_provenance": _prov("mantle-rpc", "unavailable")}
    try:
        tip = int(await _eth_rpc(rpc_url, "eth_blockNumber", []), 16)
        frm = max(0, tip - blocks + 1)
        logs = await _eth_rpc(rpc_url, "eth_getLogs", [{
            "fromBlock": hex(frm), "toBlock": hex(tip), "topics": [_V2_SWAP_TOPIC],
        }])
    except Exception as e:  # one optional source must never crash the whole round
        logger.warning(f"Mantle RPC unavailable, declaring it (not faking live): {e}")
        return {"asset": asset, "available": False,
                "_provenance": _prov("mantle-rpc", "unavailable")}

    decoded = sum(1 for lg in logs if len(_words(lg.get("data", "0x"))) >= 4)
    return {
        "asset": asset, "available": True, "tip_block": tip, "from_block": frm,
        "swap_logs": len(logs), "decoded": decoded,
        "_provenance": _prov("mantle-rpc", "live", f"block={tip}"),
    }
