"""Settler service tests — dry-run mode, no on-chain dependencies."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from agents.settler.service import RiskConfig, RoundOutcome, SettlerService
from agents.shared.types import Decision, DecisionType


def _agent_payload(agent_name: str, agent_id: int, signal: float, conf: float,
                   kind: DecisionType = DecisionType.SPOT_SWAP, size_bps: int = 500) -> dict[str, Any]:
    decision = Decision(
        agent_id=agent_id,
        decision_index=0,
        timestamp=0,
        kind=kind,
        market_id="mETH/USDC",
        directional_signal=signal,
        size_bps=size_bps,
        confidence=conf,
    ).model_dump()
    return {
        "name": agent_name,
        "agent_id": agent_id,
        "decision": decision,
        "reasoning_hash": "aa" * 32,
        "reasoning_chain": {"steps": [], "model": "test"},
    }


async def _stub_run_round_bullish(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
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


async def _stub_run_round_da_veto(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
    return {
        "market_id": market_id,
        "ensemble": {"directional_signal": 0.62, "confidence": 0.74},
        "agents": [
            _agent_payload("chronos", agent_ids["chronos"], 0.7, 0.8),
            _agent_payload("web", agent_ids["web"], 0.5, 0.7),
            _agent_payload("mood", agent_ids["mood"], 0.6, 0.65),
            _agent_payload("devils_advocate", agent_ids["devils_advocate"], 0.0, 0.7, DecisionType.HOLD, 0),
        ],
    }


async def _stub_run_round_low_conf(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
    return {
        "market_id": market_id,
        "ensemble": {"directional_signal": 0.62, "confidence": 0.40},  # below 50% floor
        "agents": [
            _agent_payload("chronos", agent_ids["chronos"], 0.7, 0.5),
            _agent_payload("web", agent_ids["web"], 0.5, 0.4),
            _agent_payload("mood", agent_ids["mood"], 0.6, 0.3),
            _agent_payload("devils_advocate", agent_ids["devils_advocate"], -0.2, 0.4),
        ],
    }


AGENT_IDS = {"chronos": 1, "web": 2, "mood": 3, "devils_advocate": 4}


def test_risk_config_validate_happy_path():
    cfg = RiskConfig()
    is_safe, reason = cfg.validate_decision(ensemble_signal=0.6, ensemble_conf=0.7,
                                             da_signal=-0.3, da_conf=0.6)
    assert is_safe, reason


def test_risk_config_blocks_da_veto():
    cfg = RiskConfig()
    is_safe, reason = cfg.validate_decision(ensemble_signal=0.6, ensemble_conf=0.7,
                                             da_signal=0.0, da_conf=0.7)
    assert not is_safe
    assert "veto" in reason.lower()


def test_risk_config_blocks_low_confidence():
    cfg = RiskConfig()
    is_safe, reason = cfg.validate_decision(ensemble_signal=0.6, ensemble_conf=0.49,
                                             da_signal=-0.2, da_conf=0.5)
    assert not is_safe
    assert "confidence" in reason.lower()


def test_risk_config_blocks_weak_signal():
    cfg = RiskConfig()
    is_safe, reason = cfg.validate_decision(ensemble_signal=0.04, ensemble_conf=0.8,
                                             da_signal=-0.1, da_conf=0.5)
    assert not is_safe


def test_signal_to_size_caps_at_max():
    cfg = RiskConfig()
    # signal=1.0, conf=1.0 → raw size = 500 (the cap)
    assert cfg.signal_to_size_bps(1.0, 1.0) == 500
    # signal=0.5, conf=0.5 → raw = 125
    assert cfg.signal_to_size_bps(0.5, 0.5) == 125
    # signal=1.5 (out of bounds, but should still cap)
    assert cfg.signal_to_size_bps(1.5, 1.0) == 500


def test_signal_to_size_minimum_one():
    cfg = RiskConfig()
    # tiny signal+conf must still produce at least 1 bps
    assert cfg.signal_to_size_bps(0.001, 0.001) == 1


def test_settler_executes_bullish_round():
    svc = SettlerService(run_round_fn=_stub_run_round_bullish, dry_run=True)
    outcome = asyncio.run(svc.run_one("mETH/USDC", AGENT_IDS))
    assert isinstance(outcome, RoundOutcome)
    assert outcome.trade_executed is True
    assert outcome.rejection_reason is None
    assert outcome.ensemble_signal == 0.62
    assert len(outcome.agent_records) == 4


def test_settler_rejects_da_veto():
    svc = SettlerService(run_round_fn=_stub_run_round_da_veto, dry_run=True)
    outcome = asyncio.run(svc.run_one("mETH/USDC", AGENT_IDS))
    assert outcome.trade_executed is False
    assert "veto" in (outcome.rejection_reason or "").lower()


def test_settler_rejects_low_confidence():
    svc = SettlerService(run_round_fn=_stub_run_round_low_conf, dry_run=True)
    outcome = asyncio.run(svc.run_one("mETH/USDC", AGENT_IDS))
    assert outcome.trade_executed is False
    assert "confidence" in (outcome.rejection_reason or "").lower()


def test_resolve_tokens_bullish_buys_base():
    tokens = SettlerService._resolve_tokens("mETH/USDC", signal=0.5)
    # bullish on mETH → swap USDC -> mETH
    assert tokens["in"] != tokens["out"]
    # USDC address goes in
    import os
    expected_usdc = os.environ.get("MANTLE_USDC", "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9")
    assert tokens["in"] == expected_usdc


def test_resolve_tokens_bearish_sells_base():
    tokens = SettlerService._resolve_tokens("mETH/USDC", signal=-0.5)
    # bearish on mETH → swap mETH -> USDC
    import os
    expected_meth = os.environ.get("MANTLE_METH", "0xcDA86A272531e8640cD7F1a92c01839911B90bb0")
    assert tokens["in"] == expected_meth
