"""The live-wiring gap, closed and defended.

These tests pin the claim that the round flow is ONE FLAG away from a real chain:
the composition pieces (ABI loading, signing client, chain-seeded decision indices,
round records, settle grading, the never-fake-a-price gates) are all exercised
offline. What remains untested by design is gas + a funded key — that is the
mainnet-deploy step, not a code gap (docs/mainnet-runbook.md).
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from agents.settler import live
from agents.settler.service import SettlerService
from agents.shared import tools
from agents.shared.types import Decision, DecisionType

AGENT_IDS = {"chronos": 1, "web": 2, "mood": 3, "devils_advocate": 4}


def _agent_payload(agent_name: str, agent_id: int, signal: float, conf: float) -> dict[str, Any]:
    decision = Decision(
        agent_id=agent_id,
        decision_index=0,
        timestamp=0,
        kind=DecisionType.SPOT_SWAP,
        market_id="mETH/USDC",
        directional_signal=signal,
        size_bps=400,
        confidence=conf,
    ).model_dump()
    return {
        "name": agent_name,
        "agent_id": agent_id,
        "decision": decision,
        "reasoning_hash": "aa" * 32,
        "reasoning_chain": {"steps": [], "model": "test"},
    }


async def _stub_run_round(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
    return {
        "market_id": market_id,
        "ensemble": {"directional_signal": 0.62, "confidence": 0.74},
        "agents": [
            _agent_payload("chronos", agent_ids["chronos"], 0.7, 0.8),
            _agent_payload("web", agent_ids["web"], 0.5, 0.7),
            _agent_payload("mood", agent_ids["mood"], 0.6, 0.65),
            _agent_payload("devils_advocate", agent_ids["devils_advocate"], -0.2, 0.55),
        ],
    }


def _live_price(price: float, ts: int = 1_717_000_000) -> dict[str, Any]:
    return {"market_id": "mETH/USDC", "available": True, "price": price,
            "base_usd": price, "quote_usd": 1.0, "timestamp": ts,
            "_provenance": f"defillama-price:live@ts={ts}"}


async def _stub_price_live(market_id: str) -> dict[str, Any]:
    return _live_price(100.0)


async def _stub_price_unavailable(market_id: str) -> dict[str, Any]:
    return {"market_id": market_id, "available": False,
            "_provenance": "defillama-price:unavailable"}


# ---- settlement-grade price source ----

def test_spot_price_declares_unavailable_when_endpoint_unreachable(monkeypatch):
    """A dead endpoint must yield an honest 'unavailable' — never a mock price."""
    monkeypatch.setenv("LLAMA_PRICE_URL", "http://127.0.0.1:9/")  # read at call time
    out = asyncio.run(tools.mantle_spot_price("mETH/USDC"))
    assert out["available"] is False
    assert out["_provenance"] == "defillama-price:unavailable"
    assert "price" not in out  # no invented number rides along with the honest tag


def test_spot_price_unknown_pair_is_unavailable():
    out = asyncio.run(tools.mantle_spot_price("FOO/BAR"))
    assert out["available"] is False
    assert out["_provenance"] == "defillama-price:unavailable"


def test_spot_price_parse_computes_pair_and_oldest_timestamp():
    """Pure parse: pair = base_usd/quote_usd; timestamp = the OLDER observation."""
    coins = {
        f"mantle:{tools._PRICE_TOKEN_ADDRS['mETH']}":
            {"price": 1794.71, "timestamp": 1_717_000_100, "confidence": 0.99},
        f"mantle:{tools._PRICE_TOKEN_ADDRS['USDC']}":
            {"price": 1.0069, "timestamp": 1_717_000_000, "confidence": 0.99},
    }
    parsed = tools._parse_llama_pair(coins, "mETH/USDC")
    assert parsed is not None
    assert parsed["price"] == 1794.71 / 1.0069
    assert parsed["timestamp"] == 1_717_000_000  # honest staleness bound


def test_spot_price_parse_rejects_low_confidence():
    """DeFiLlama confidence < 0.9 is unreliable per their own guidance — refuse it."""
    coins = {
        f"mantle:{tools._PRICE_TOKEN_ADDRS['mETH']}":
            {"price": 1794.71, "timestamp": 1, "confidence": 0.5},
        f"mantle:{tools._PRICE_TOKEN_ADDRS['USDC']}":
            {"price": 1.0069, "timestamp": 1, "confidence": 0.99},
    }
    assert tools._parse_llama_pair(coins, "mETH/USDC") is None


# ---- chain wiring (offline) ----

def test_load_abi_exposes_every_shim_function():
    """The composition root loads ABIs the service shims actually call."""
    import pytest
    if not (live._REPO_ROOT / "contracts" / "out").exists():
        pytest.skip("contracts/out not built — run `forge build` in contracts/ first")
    round_state = {entry.get("name") for entry in live.load_abi("RoundState")}
    assert {"openRound", "recordSubmission", "setEnsemble", "settle"} <= round_state
    anchor = {entry.get("name") for entry in live.load_abi("ReasoningHashAnchor")}
    assert {"commit", "getCommit", "verify"} <= anchor


def test_build_w3_installs_signer_and_default_account():
    """Bare .transact() shims need a default_account + local signing — set offline."""
    from eth_account import Account

    key = "0x" + "11" * 32
    w3 = live.build_w3("http://127.0.0.1:9", key)  # HTTPProvider is lazy: no connection
    assert w3.eth.default_account == Account.from_key(key).address


def test_next_decision_index_seeds_from_chain():
    """First index where getCommit REVERTS is free — restart can't recommit history."""
    from web3.exceptions import ContractLogicError

    class _Call:
        def __init__(self, taken: bool) -> None:
            self._taken = taken

        def call(self):
            if not self._taken:
                raise ContractLogicError("execution reverted: no commit")
            return ("0x" + "ab" * 32,)

    class _Functions:
        def getCommit(self, agent_id: int, index: int) -> _Call:
            return _Call(taken=index < 2)  # chain already holds indices 0 and 1

    class _Anchor:
        functions = _Functions()

    assert live.next_decision_index(_Anchor(), agent_id=1) == 2


def test_next_decision_index_propagates_transport_errors():
    """An RPC outage at probe time must abort BEFORE openRound — a transport error
    read as 'free slot' would seed a stale index and strand an opened round."""
    class _Call:
        def call(self):
            raise ConnectionError("rpc unreachable")

    class _Functions:
        def getCommit(self, agent_id: int, index: int) -> _Call:
            return _Call()

    class _Anchor:
        functions = _Functions()

    try:
        live.next_decision_index(_Anchor(), agent_id=1)
    except ConnectionError:
        pass
    else:
        raise AssertionError("transport error must propagate, not be read as a free slot")


# ---- round records + settle grading ----

def test_run_and_record_writes_grade_ready_record(tmp_path):
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,
    ))
    record = json.loads(path.read_text())
    assert record["live"] is False
    assert record["price_at_commit"]["available"] is True
    assert record["price_at_commit"]["price"] == 100.0
    signals = {a["name"]: a["decision"]["directional_signal"] for a in record["agent_records"]}
    assert signals["chronos"] == 0.7 and signals["devils_advocate"] == -0.2
    assert record["settlement"] is None  # not yet graded


def test_dry_run_records_honest_unavailable_price(tmp_path):
    """Paper rounds stay runnable offline — the record carries the honest tag."""
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_unavailable,
    ))
    record = json.loads(path.read_text())
    assert record["price_at_commit"]["available"] is False
    assert record["price_at_commit"]["_provenance"] == "defillama-price:unavailable"


def test_live_round_refuses_unavailable_commit_price(tmp_path):
    """A LIVE commit without a live price could never be graded — refuse to start."""
    try:
        asyncio.run(live.run_and_record(
            "mETH/USDC", live=True, record_dir=tmp_path,
            run_round_fn=_stub_run_round, price_fn=_stub_price_unavailable,
        ))
    except RuntimeError as e:
        assert "unavailable" in str(e)
    else:
        raise AssertionError("live run must refuse an ungradeable commit")


def test_settle_from_record_grades_committed_signals(tmp_path):
    """Settle reads signals off the RECORD (already committed), prices independently."""
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,  # commit price 100.0
    ))

    async def _price_at_settle(market_id: str) -> dict[str, Any]:
        return _live_price(105.0)  # +5% move

    settlement = asyncio.run(live.settle_from_record(path, live=False,
                                                     price_fn=_price_at_settle))
    assert settlement["realized_move_bps"] == 500
    by_name = {s["name"]: s for s in settlement["scores"]}
    # score = direction * realized_bps * |committed signal| — recomputable by anyone.
    assert by_name["chronos"]["score"] == SettlerService.score_prediction(0.7, 500)
    assert by_name["devils_advocate"]["score"] == SettlerService.score_prediction(-0.2, 500)
    assert by_name["chronos"]["score"] > 0 > by_name["devils_advocate"]["score"]
    # The record now carries the settlement, including both price provenances.
    record = json.loads(path.read_text())
    assert record["settlement"]["settled_onchain"] is False
    assert record["settlement"]["price_at_settle"]["_provenance"].startswith("defillama-price:live")


def test_settle_refuses_unavailable_settlement_price(tmp_path):
    """resolve_outcome on an invented price = fabricated outcome. Refuse, retry later."""
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,
    ))
    try:
        asyncio.run(live.settle_from_record(path, live=False,
                                            price_fn=_stub_price_unavailable))
    except RuntimeError as e:
        assert "unavailable" in str(e)
    else:
        raise AssertionError("settle must refuse a non-live settlement price")


def test_settle_live_refuses_dry_run_record(tmp_path):
    """A paper record's pseudo round_id was never opened on-chain — --live must refuse
    (a colliding id could write a fabricated settlement onto someone else's round)."""
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,
    ))
    try:
        asyncio.run(live.settle_from_record(path, live=True, price_fn=_stub_price_live))
    except RuntimeError as e:
        assert "dry-run" in str(e)
    else:
        raise AssertionError("--live settle must refuse a dry-run record")


def test_settle_refuses_already_settled_record(tmp_path):
    """A settlement is an audit artifact — re-grading must never silently rewrite it
    (it could flip settled_onchain true -> false and un-claim an on-chain settlement)."""
    path = asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,
    ))
    first = asyncio.run(live.settle_from_record(path, live=False, price_fn=_stub_price_live))
    try:
        asyncio.run(live.settle_from_record(path, live=False, price_fn=_stub_price_live))
    except RuntimeError as e:
        assert "already settled" in str(e)
    else:
        raise AssertionError("second settle must refuse, not rewrite")
    record = json.loads(path.read_text())
    assert record["settlement"]["realized_move_bps"] == first["realized_move_bps"]


def test_round_records_never_overwritten(tmp_path, monkeypatch):
    """The record is the only copy of the commit-time price — a round_id collision
    must raise, never silently replace an earlier record."""
    monkeypatch.setattr(SettlerService, "_open_round", lambda self, market_id: 1234)
    asyncio.run(live.run_and_record(
        "mETH/USDC", live=False, record_dir=tmp_path,
        run_round_fn=_stub_run_round, price_fn=_stub_price_live,
    ))
    try:
        asyncio.run(live.run_and_record(
            "mETH/USDC", live=False, record_dir=tmp_path,
            run_round_fn=_stub_run_round, price_fn=_stub_price_live,
        ))
    except RuntimeError as e:
        assert "refusing to overwrite" in str(e)
    else:
        raise AssertionError("colliding round_id must refuse, not clobber")


def test_crashed_round_still_leaves_commit_price_on_disk(tmp_path):
    """A mid-flight crash must not orphan the round ungradeable — the commit-time
    price (the one unrecoverable input) is persisted before the first tx."""
    async def _boom(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
        raise TimeoutError("rpc timeout mid-round")

    try:
        asyncio.run(live.run_and_record(
            "mETH/USDC", live=False, record_dir=tmp_path,
            run_round_fn=_boom, price_fn=_stub_price_live,
        ))
    except TimeoutError:
        pass
    [inflight] = sorted(tmp_path.glob("inflight_*.json"))
    record = json.loads(inflight.read_text())
    assert record["status"] == "in_flight"
    assert record["price_at_commit"]["price"] == 100.0
    assert record["price_at_commit"]["_provenance"].startswith("defillama-price:live")
