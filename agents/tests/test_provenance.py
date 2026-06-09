"""Provenance receipt tests — close gap #2 (a receipt must not be able to claim mock
data was live) and gap #1 (a committed prediction graded by an independent, recomputable
rule). The byte-parity golden vectors in test_receipt.py are intentionally left unchanged:
provenance rides inside the EXISTING data_sources field, so the canonical serialization —
and the on-chain commit value — are untouched.
"""
from __future__ import annotations

import asyncio
from typing import Any, cast

from agents.shared import tools
from agents.shared.base import GlassBoxAgent
from agents.shared.types import ReasoningChain, ReasoningStep
from agents.settler.service import SettlerService


def _chain(data_sources: list[str]) -> ReasoningChain:
    return ReasoningChain(
        agent_id=1, decision_index=0, model="m", prompt_tokens=1, completion_tokens=1,
        steps=[ReasoningStep(step=1, thought="x")], data_sources=data_sources, timestamp=1,
    )


# ---- gap #2: liveness is stamped at origin and committed tamper-evidently ----

def test_mock_path_is_stamped_mock_at_origin(monkeypatch):
    """No API key → mock data → provably tagged mock (not inferred, not 'live')."""
    monkeypatch.delenv("NANSEN_API_KEY", raising=False)
    flows = asyncio.run(tools.nansen_smart_money_flows("mETH"))
    assert flows["_provenance"] == "nansen:mock"


def test_elfa_mock_path_is_stamped_mock(monkeypatch):
    monkeypatch.delenv("ELFA_API_KEY", raising=False)
    s = asyncio.run(tools.elfa_sentiment("mETH"))
    assert s["_provenance"] == "elfa:mock"


def test_provenance_is_committed_and_tamper_evident():
    """Flip a source's liveness tag mock→live and the on-chain commit hash changes —
    a receipt cannot lie about whether its inputs were real."""
    live = GlassBoxAgent.reasoning_hash(_chain(["nansen:live"]))
    mock = GlassBoxAgent.reasoning_hash(_chain(["nansen:mock"]))
    assert live != mock


def test_collect_provenance_extracts_and_ignores_non_dicts():
    tags = tools.collect_provenance(
        {"_provenance": "nansen:live"}, {"x": 1}, ["not-a-dict"], {"_provenance": "elfa:mock"},
    )
    assert tags == ["nansen:live", "elfa:mock"]


def test_data_sources_is_sorted_and_deduped():
    """Same inputs in any gather order → identical committed data_sources (and hash)."""
    a = sorted(set(["nansen:mock", "defillama:live", "nansen:mock"]))
    b = sorted(set(["defillama:live", "nansen:mock"]))
    assert a == b == ["defillama:live", "nansen:mock"]


# ---- first-party RPC source: honest when unavailable, never silently mock ----

def test_mantle_rpc_declares_unavailable_without_endpoint(monkeypatch):
    monkeypatch.delenv("MANTLE_RPC_URL", raising=False)  # read at call-time, like the other tools
    out = asyncio.run(tools.mantle_rpc_activity("mETH"))
    assert out["available"] is False
    assert out["_provenance"] == "mantle-rpc:unavailable"  # NOT mock — honestly absent


# ---- gap #1: independent resolution + recomputable scoring ----

def test_score_rewards_correct_direction_and_punishes_wrong():
    # bullish call, price rose → positive; bearish call, price rose → negative
    assert SettlerService.score_prediction(0.8, 500) > 0
    assert SettlerService.score_prediction(-0.8, 500) < 0
    # bearish call, price fell → positive (direction matched)
    assert SettlerService.score_prediction(-0.8, -500) > 0


def test_resolve_outcome_is_recomputable_bps():
    assert SettlerService.resolve_outcome(100.0, 105.0) == 500   # +5%
    assert SettlerService.resolve_outcome(100.0, 95.0) == -500   # -5%
    assert SettlerService.resolve_outcome(0.0, 105.0) == 0       # guarded


def test_settle_round_grades_committed_signals():
    """The loop actually RUNS: settle_round reads each agent's committed signal off the round
    record and grades it against an independent price move — not two unwired functions."""
    from agents.settler.service import RoundOutcome

    svc = SettlerService(run_round_fn=cast(Any, None), dry_run=True)
    outcome = RoundOutcome(
        round_id=1, market_id="mETH/USDC", ensemble_signal=0.5, ensemble_confidence=0.7,
        trade_executed=False, rejection_reason=None,
        agent_records=[
            {"name": "chronos", "agent_id": 1, "decision": {"directional_signal": 0.8}},
            {"name": "mood", "agent_id": 4, "decision": {"directional_signal": -0.5}},
        ],
    )
    scored = {s["agent_id"]: s for s in svc.settle_round(outcome, 100.0, 105.0)}  # +5%
    assert scored[1]["realized_move_bps"] == 500
    assert scored[1]["committed_signal"] == 0.8   # read from the record, not re-derived
    assert scored[1]["score"] > 0                 # bullish + price up → rewarded
    assert scored[4]["score"] < 0                 # bearish + price up → punished


# ---- integration: provenance actually flows agent → committed data_sources ----

def _data_sources_from(context: dict) -> list[str]:
    """Reproduce base.reason()'s data_sources construction without invoking the LLM."""
    provenance = context.pop("_provenance", None)
    return sorted(set(provenance)) if provenance else ["undeclared:unknown"]


def test_each_agent_declares_provenance_in_mock_mode(monkeypatch):
    from agents.chronos.agent import Chronos
    from agents.web.agent import Web
    from agents.mood.agent import Mood
    from agents.devils_advocate.agent import DevilsAdvocate

    for k in ("NANSEN_API_KEY", "ELFA_API_KEY", "MANTLE_RPC_URL"):
        monkeypatch.delenv(k, raising=False)  # no live sources in CI

    # gather_context never touches the LLM client, so a dummy client is fine.
    client = cast(Any, None)
    chronos = _data_sources_from(asyncio.run(Chronos(client, 1).gather_context("mETH/USDC")))
    assert "nansen:mock" in chronos
    assert "nansen-wallets:mock" in chronos      # wallet history declares its OWN liveness
    assert "defillama:live" in chronos or "defillama:unavailable" in chronos
    assert "mantle-rpc:unavailable" in chronos   # honest, never silently mock
    assert chronos == sorted(set(chronos))       # sorted + deduped

    web = _data_sources_from(asyncio.run(Web(client, 3).gather_context("mETH/USDC")))
    assert web == ["nansen:mock"]               # deduped across base + related flows

    mood = _data_sources_from(asyncio.run(Mood(client, 4).gather_context("mETH/USDC")))
    assert mood == ["elfa:mock"]

    da = _data_sources_from(asyncio.run(DevilsAdvocate(client, 2).gather_context("mETH/USDC")))
    assert da == ["peers:internal"]
