"""Tests for the Fold ensemble — confidence-weighted multi-frame consensus.

The Fold IS a confidence-weighted mean by construction; these tests pin that
definition and its honest properties. We deliberately make NO claim that it beats
a mean (it is one) — the ensemble's value over a single agent is shown in the
backtest (test_backtest.py), not asserted here.
"""
from __future__ import annotations

import math

from agents.shared.ensemble import fold_ensemble


def _weighted_mean(signals, confs):
    weighted = sum(s * c for s, c in zip(signals, confs))
    conf_sum = sum(confs)
    return weighted / conf_sum if conf_sum else 0.0


def test_all_bullish_high_confidence():
    """When all 4 agents are bullish with high confidence, ensemble is bullish."""
    signal, conf = fold_ensemble(
        chronos_signal=0.8, da_signal=0.6, web_signal=0.7, mood_signal=0.5,
        chronos_conf=0.9, da_conf=0.8, web_conf=0.85, mood_conf=0.75,
    )
    assert signal > 0, f"expected bullish, got {signal}"
    assert conf > 0.5, f"expected high confidence, got {conf}"


def test_all_bearish_high_confidence():
    """Symmetric — all bearish should produce bearish signal."""
    signal, conf = fold_ensemble(
        chronos_signal=-0.8, da_signal=-0.6, web_signal=-0.7, mood_signal=-0.5,
        chronos_conf=0.9, da_conf=0.8, web_conf=0.85, mood_conf=0.75,
    )
    assert signal < 0
    assert conf > 0.5


def test_fold_is_confidence_weighted_mean():
    """Defining identity: the Fold signal equals the confidence-weighted mean of the
    four agent signals. This is the whole aggregation — nothing hidden."""
    cases = [
        ((0.8, -0.7, 0.6, -0.5), (0.9, 0.9, 0.9, 0.9)),
        ((0.3, 0.4, -0.2, 0.6), (0.5, 0.9, 0.6, 0.7)),
        ((-0.9, -0.1, -0.4, -0.5), (0.8, 0.4, 0.7, 0.6)),
    ]
    for signals, confs in cases:
        signal, _ = fold_ensemble(*signals, *confs)
        assert math.isclose(signal, _weighted_mean(signals, confs), abs_tol=1e-9)


def test_higher_confidence_agent_pulls_consensus():
    """Confidence weighting works: the same split of signals leans toward whichever
    side is more confident."""
    # Two bulls (+0.6) vs two bears (-0.6); bulls far more confident → net bullish.
    signal, _ = fold_ensemble(
        chronos_signal=0.6, da_signal=0.6, web_signal=-0.6, mood_signal=-0.6,
        chronos_conf=0.95, da_conf=0.95, web_conf=0.35, mood_conf=0.35,
    )
    assert signal > 0


def test_zero_consensus_returns_flat():
    """Perfectly offsetting signals → no position."""
    signal, conf = fold_ensemble(
        chronos_signal=0.5, da_signal=-0.5, web_signal=0.5, mood_signal=-0.5,
        chronos_conf=0.8, da_conf=0.8, web_conf=0.8, mood_conf=0.8,
    )
    assert math.isclose(signal, 0.0, abs_tol=1e-9)


def test_confidence_is_geometric_mean():
    """Final confidence = (c1 * c2 * c3 * c4) ** 0.25 — capped by the least-sure agent."""
    _, conf = fold_ensemble(
        chronos_signal=0.5, da_signal=0.5, web_signal=0.5, mood_signal=0.5,
        chronos_conf=0.8, da_conf=0.8, web_conf=0.8, mood_conf=0.8,
    )
    assert math.isclose(conf, 0.8, abs_tol=0.001)


def test_confidence_capped_by_least_sure_agent():
    """One unsure agent drags overall confidence below the arithmetic mean of confs."""
    _, conf = fold_ensemble(
        chronos_signal=0.5, da_signal=0.5, web_signal=0.5, mood_signal=0.5,
        chronos_conf=0.9, da_conf=0.9, web_conf=0.9, mood_conf=0.3,
    )
    arithmetic = (0.9 + 0.9 + 0.9 + 0.3) / 4
    assert conf < arithmetic


def test_signal_bounded_by_inputs():
    """Final signal magnitude should not exceed max input magnitude (it's a mean)."""
    inputs = [(0.9, 0.7, 0.6, 0.5), (0.3, 0.4, 0.5, 0.6), (0.1, 0.1, 0.1, 0.1)]
    for chronos_s, da_s, web_s, mood_s in inputs:
        signal, _ = fold_ensemble(
            chronos_signal=chronos_s, da_signal=da_s, web_signal=web_s, mood_signal=mood_s,
            chronos_conf=0.9, da_conf=0.9, web_conf=0.9, mood_conf=0.9,
        )
        max_input = max(abs(chronos_s), abs(da_s), abs(web_s), abs(mood_s))
        assert abs(signal) <= max_input + 0.01, f"signal {signal} exceeds max input {max_input}"
