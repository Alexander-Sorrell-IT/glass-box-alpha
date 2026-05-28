"""Tests for share-card URL + tweet copy generation."""
from __future__ import annotations

from agents.settler.service import RoundOutcome
from agents.settler.share import share_card_url, tweet_copy


def _outcome(executed: bool = True, signal: float = 0.41, reason: str | None = None) -> RoundOutcome:
    return RoundOutcome(
        round_id=17,
        market_id="mETH/USDC",
        ensemble_signal=signal,
        ensemble_confidence=0.66,
        trade_executed=executed,
        rejection_reason=reason,
        agent_records=[
            {"name": "chronos", "agent_id": 1, "decision": {"directional_signal": 0.62}, "reasoning_hash": "a", "reasoning_chain": {}},
            {"name": "devils_advocate", "agent_id": 2, "decision": {"directional_signal": -0.15}, "reasoning_hash": "b", "reasoning_chain": {}},
            {"name": "web", "agent_id": 3, "decision": {"directional_signal": 0.48}, "reasoning_hash": "c", "reasoning_chain": {}},
            {"name": "mood", "agent_id": 4, "decision": {"directional_signal": 0.38}, "reasoning_hash": "d", "reasoning_chain": {}},
        ],
    )


def test_share_url_contains_all_params():
    url = share_card_url(_outcome(), pnl_pct=2.3)
    assert "market=mETH" in url
    assert "signal=0.41" in url
    assert "confidence=66" in url
    assert "chronos=0.62" in url
    assert "da=-0.15" in url
    assert "web=0.48" in url
    assert "mood=0.38" in url
    assert "pnl=2.30" in url
    assert "round=17" in url


def test_share_url_without_pnl():
    url = share_card_url(_outcome(), pnl_pct=None)
    assert "pnl=" not in url


def test_tweet_copy_executed_under_280():
    copy = tweet_copy(_outcome(executed=True), pnl_pct=2.3)
    assert len(copy) <= 280, f"tweet is {len(copy)} chars"
    assert "#MantleAIHackathon" in copy
    assert "Fold ensemble" in copy


def test_tweet_copy_rejected_shows_risk_gate():
    copy = tweet_copy(_outcome(executed=False, reason="Devil's Advocate veto"), pnl_pct=None)
    assert len(copy) <= 280
    assert "SKIPPED" in copy
    assert "veto" in copy.lower()
    assert "Risk gate working" in copy


def test_tweet_copy_bearish_uses_down_arrow():
    copy = tweet_copy(_outcome(signal=-0.3), pnl_pct=None)
    assert "📉" in copy
    assert "bearish" in copy
