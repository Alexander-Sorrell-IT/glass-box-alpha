"""CLI entry point for the backtest harness.

Usage:
    python3 scripts/run_backtest.py                          # synthetic data, 90 days
    python3 scripts/run_backtest.py --market MNT/USDC        # different market
    python3 scripts/run_backtest.py --days 180 --seed 7      # longer history, different seed
    python3 scripts/run_backtest.py --real                   # try fetching real Mantle history from DeFiLlama

Output: human-readable summary + JSON report at runs/backtest-<timestamp>.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Make `agents` importable regardless of CWD
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.backtest.harness import format_report, run_backtest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", default="mETH/USDC", help="e.g. mETH/USDC, MNT/USDC")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--real", action="store_true", help="try to fetch real DeFiLlama data")
    parser.add_argument("--runs-dir", default="runs", help="where to dump JSON report")
    args = parser.parse_args()

    print(f"Running backtest: {args.market} × {args.days} days × seed={args.seed} × real={args.real}\n")
    report = run_backtest(
        market=args.market, days=args.days, seed=args.seed,
        prefer_real_data=args.real,
    )
    print(format_report(report))

    out_dir = Path(args.runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    out_path = out_dir / f"backtest-{ts}.json"
    payload = {
        **report.to_dict(),
        "daily_results": [
            {
                "day": r.day,
                "bar_return": r.bar_return,
                "fold_signal": r.fold_signal,
                "fold_confidence": r.fold_confidence,
                "fold_pnl": r.fold_pnl,
                "baseline_signal": r.baseline_signal,
                "baseline_pnl": r.baseline_pnl,
                "agent_signals": r.agent_signals,
            }
            for r in report.daily_results
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"\nFull JSON report written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
