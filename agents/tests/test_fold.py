"""Smoke tests for the Fold ensemble — sign-preserving geometric mean behavior."""
from __future__ import annotations

import math

from agents.shared.ensemble import fold_ensemble


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


def test_split_signal_collapses_to_low():
    """Disagreement (2 bull, 2 bear) should produce low-magnitude signal."""
    signal, conf = fold_ensemble(
        chronos_signal=0.8, da_signal=-0.7, web_signal=0.6, mood_signal=-0.5,
        chronos_conf=0.9, da_conf=0.9, web_conf=0.9, mood_conf=0.9,
    )
    # Down-arrow component sign = sum of 3 down-arrow agent signs.
    # DA = -1, Web = +1, Mood = -1 → sum = -1 → negative down.
    # Up (Chronos) is positive. Product is negative → signal is negative.
    assert abs(signal) < 0.8, f"split signal should collapse below 0.8, got {abs(signal)}"


def test_zero_when_any_agent_zero():
    """If any agent has zero signal magnitude, product zeroes out — Fold returns 0."""
    signal, conf = fold_ensemble(
        chronos_signal=0.0, da_signal=0.7, web_signal=0.5, mood_signal=0.6,
        chronos_conf=0.5, da_conf=0.8, web_conf=0.7, mood_conf=0.6,
    )
    assert signal == 0.0
    assert conf == 0.0


def test_confidence_is_geometric_mean():
    """Final confidence = (c1 * c2 * c3 * c4) ** 0.25."""
    _, conf = fold_ensemble(
        chronos_signal=0.5, da_signal=0.5, web_signal=0.5, mood_signal=0.5,
        chronos_conf=0.8, da_conf=0.8, web_conf=0.8, mood_conf=0.8,
    )
    assert math.isclose(conf, 0.8, abs_tol=0.001)


def test_signal_bounded_by_inputs():
    """Final signal magnitude should not exceed max input magnitude."""
    inputs = [(0.9, 0.7, 0.6, 0.5), (0.3, 0.4, 0.5, 0.6), (0.1, 0.1, 0.1, 0.1)]
    for chronos_s, da_s, web_s, mood_s in inputs:
        signal, _ = fold_ensemble(
            chronos_signal=chronos_s, da_signal=da_s, web_signal=web_s, mood_signal=mood_s,
            chronos_conf=0.9, da_conf=0.9, web_conf=0.9, mood_conf=0.9,
        )
        max_input = max(abs(chronos_s), abs(da_s), abs(web_s), abs(mood_s))
        assert abs(signal) <= max_input + 0.01, f"signal {signal} exceeds max input {max_input}"
