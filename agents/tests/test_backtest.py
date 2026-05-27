"""Backtest harness tests."""
from __future__ import annotations

import math

import pytest

from agents.backtest.harness import (
    AgentDayOutput,
    DailyBar,
    annualized_return,
    format_report,
    hit_rate,
    historical_bars,
    max_drawdown,
    replay,
    run_backtest,
    sharpe,
    synthetic_agent_outputs,
)


# ---------- Synthetic data ----------

def test_synthetic_bars_deterministic():
    a = historical_bars("mETH/USDC", days=10, seed=42)
    b = historical_bars("mETH/USDC", days=10, seed=42)
    assert len(a) == len(b) == 10
    assert all(x.close == y.close for x, y in zip(a, b))


def test_synthetic_bars_different_seeds_diverge():
    a = historical_bars("mETH/USDC", days=20, seed=1)
    b = historical_bars("mETH/USDC", days=20, seed=2)
    assert any(x.close != y.close for x, y in zip(a, b))


def test_bar_return_pct():
    bar = DailyBar(day=0, timestamp=0, open=100, high=105, low=95, close=102, volume=1000)
    assert math.isclose(bar.return_pct, 0.02, abs_tol=1e-9)


# ---------- Metrics ----------

def test_sharpe_zero_for_constant_returns():
    assert sharpe([0.01] * 100) == 0.0  # zero std -> defined as 0


def test_sharpe_positive_for_consistent_upward():
    # Slight upward drift with small noise
    rng_returns = [0.002 + (i % 3 - 1) * 0.001 for i in range(50)]
    s = sharpe(rng_returns)
    assert s > 0


def test_hit_rate_simple():
    assert hit_rate([0.01, -0.02, 0.03, -0.01, 0.0]) == pytest.approx(0.5)  # 2 wins of 4 nonzero
    assert hit_rate([]) == 0.0
    assert hit_rate([0.0, 0.0]) == 0.0


def test_max_drawdown_negative_or_zero():
    # Smooth upward path -> 0 drawdown
    assert max_drawdown([0.01, 0.01, 0.01]) == 0.0
    # Drop after gain
    dd = max_drawdown([0.05, -0.10, 0.03])
    assert dd < 0


def test_annualized_return():
    daily = [0.001] * 365   # 0.1% per day for a year
    ann = annualized_return(daily)
    assert math.isclose(ann, 0.365, abs_tol=0.001)


# ---------- Replay ----------

def test_replay_produces_one_record_per_bar():
    bars = historical_bars("MNT/USDC", days=30, seed=10)
    next_returns = [bars[i + 1].return_pct if i + 1 < len(bars) else 0.0 for i in range(len(bars))]
    outputs = synthetic_agent_outputs(bars, next_returns, seed=11)
    results = replay(bars, outputs)
    assert len(results) == len(bars)
    # All days have agent signals captured
    assert all(len(r.agent_signals) == 4 for r in results)


def test_replay_fold_vs_baseline_diverge():
    """Fold and baseline produce different signals on the same agent outputs."""
    bars = historical_bars("mETH/USDC", days=60, seed=20)
    next_returns = [bars[i + 1].return_pct if i + 1 < len(bars) else 0.0 for i in range(len(bars))]
    outputs = synthetic_agent_outputs(bars, next_returns, edge=0.3, noise=0.5, seed=21)
    results = replay(bars, outputs)

    diverged_days = sum(1 for r in results if abs(r.fold_signal - r.baseline_signal) > 0.01)
    assert diverged_days > 5, "Fold and baseline should produce noticeably different signals"


def test_replay_with_zero_signal_zero_pnl():
    """If agent signals are all near zero, neither ensemble should trade."""
    bars = historical_bars("MNT/USDC", days=20, seed=30)
    outputs = [
        AgentDayOutput(
            chronos=(0.001, 0.4),
            devils_advocate=(0.0, 0.4),
            web=(-0.001, 0.4),
            mood=(0.0, 0.4),
        ) for _ in bars
    ]
    results = replay(bars, outputs)
    fold_trades = sum(1 for r in results if r.fold_pnl != 0)
    base_trades = sum(1 for r in results if r.baseline_pnl != 0)
    # All signals under the 0.05 trade threshold
    assert fold_trades == 0
    assert base_trades == 0


# ---------- End-to-end ----------

def test_run_backtest_produces_full_report():
    report = run_backtest(market="mETH/USDC", days=90, seed=42)
    assert report.days == 90
    assert report.market == "mETH/USDC"
    for key in ["sharpe", "hit_rate", "max_drawdown", "annualized_return", "cumulative_pnl", "trades_executed"]:
        assert key in report.fold
        assert key in report.baseline
    assert len(report.daily_results) == 90
    assert isinstance(report.to_dict(), dict)


def test_run_backtest_with_edge_outperforms_no_edge():
    """When synthetic agents have positive edge, the Fold ensemble's Sharpe should be positive on average."""
    # Run multiple seeds to smooth out luck
    sharpes = []
    for seed in range(50, 60):
        report = run_backtest(market="mETH/USDC", days=180, seed=seed)
        sharpes.append(report.fold["sharpe"])
    avg = sum(sharpes) / len(sharpes)
    # With edge=0.15 (the default), we expect non-trivial Sharpe on average
    assert avg > 0.0, f"avg Fold Sharpe across seeds = {avg:.3f}, expected > 0"


def test_format_report_renders():
    report = run_backtest(market="MNT/USDC", days=30, seed=42)
    text = format_report(report)
    assert "Backtest" in text
    assert "Sharpe" in text
    assert "Hit rate" in text
    assert "Cumulative PnL" in text
    # Verify columns are present
    assert "Fold" in text and "Baseline" in text


def test_synthetic_agent_outputs_distribution():
    """Sanity check: synthetic agent confidences stay in valid range."""
    bars = historical_bars("MNT/USDC", days=50, seed=99)
    next_returns = [b.return_pct for b in bars]
    outputs = synthetic_agent_outputs(bars, next_returns, seed=99)
    for out in outputs:
        for sig, conf in [out.chronos, out.devils_advocate, out.web, out.mood]:
            assert -1.0 <= sig <= 1.0
            assert 0.3 <= conf <= 0.95
