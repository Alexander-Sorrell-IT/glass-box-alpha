#!/usr/bin/env python3
"""Contest status — prints days-to-deadline + current build day + today's milestone.

Designed to be wired as a Claude Code hook (UserPromptSubmit / SessionStart) so
every turn stays anchored to the plan + the Mantle Turing Test deadline.

Usage:
    python3 scripts/contest_status.py
"""
from __future__ import annotations

from datetime import datetime, timezone

# Submission deadline — Mantle Turing Test 2026, Phase 2.
DEADLINE = datetime(2026, 6, 15, 10, 59, tzinfo=timezone.utc)

# Day-by-day milestones from MASTER-PLAN.md. Keyed by ISO date.
MILESTONES: dict[str, str] = {
    "2026-05-25": "Day 1 — scaffold + contracts + agents + orchestrator",
    "2026-05-26": "Day 2 — settler + AgentExecutor + ReasoningRepToken + backtest harness",
    "2026-05-27": "Day 3 — frontend scaffold + DeepSeek swap + agent-architecture spec",
    "2026-05-28": "Day 4 — MINT 4 Agent NFTs on Mantle Mainnet · send DevRel outreach · first @GlassBoxAlpha tweet",
    "2026-05-29": "Day 5 — DeepSeek wired · real CLI round end-to-end · tune agent prompts",
    "2026-05-30": "Day 6 — Nansen + Elfa live data feeding Chronos/Web/Mood",
    "2026-06-01": "Day 7 — SEPOLIA DEPLOY all contracts · first end-to-end testnet round (HARD PIN)",
    "2026-06-02": "Day 8 — Merchant Moe V3 wired into AgentExecutor on Sepolia",
    "2026-06-03": "Day 9 — Forta-style public vuln spike (8h)",
    "2026-06-04": "Day 10 — frontend -> live testnet data · settlement modal",
    "2026-06-05": "Day 11 — designer Figma handoff · UI polish round 1",
    "2026-06-06": "Day 12 — backtest harness with REAL Mantle data + real DeepSeek agents",
    "2026-06-07": "Day 13 — backtest report finalized · 2-page writeup",
    "2026-06-08": "Day 14 — MAINNET DEPLOY · $200 USDC seed · first real trade (HARD PIN)",
    "2026-06-09": "Day 15 — glassbox-agent-kit extraction · npm + pip published",
    "2026-06-10": "Day 16 — Reasoning Reputation Token live · agent-architecture spec finalized",
    "2026-06-11": "Day 17 — KOL retweet ($300) · DM crypto-AI researchers · final polish",
    "2026-06-12": "Day 18 — 2 demo videos recorded",
    "2026-06-13": "Day 19 — final READMEs · architecture diagrams · buffer",
    "2026-06-14": "Day 20 — SUBMIT both BUIDLs on DoraHacks · launch tweet thread",
    "2026-06-15": "Day 21 — verify submissions before 10:59 UTC · DONE",
}

HARD_PINS = {
    "2026-06-01": "Sepolia working end-to-end",
    "2026-06-08": "Mainnet live + first real trade",
    "2026-06-14": "Both BUIDLs submitted (1-day buffer)",
}

# The 7 prize buckets + the criteria we must keep satisfying.
CRITERIA_REMINDERS = [
    "Consumer track is PRIMARY (empty lane). Trading is cross-tag bonus, not anchor.",
    "Lead reasoning-transparency, not win-rate (Allora dunks on 14-day PnL stats).",
    "20-Deploy bar: mainnet/testnet deploy + verified contract + >=1 on-chain AI fn + public frontend + >=2min demo + README.",
    "2 BUIDLs: Glass-Box Alpha (Consumer+Trading cross-tag) + glassbox-agent-kit (DevTools).",
    "Build-in-public daily on X for Community Voting buckets ($17K).",
]


def main() -> None:
    now = datetime.now(timezone.utc)
    today_iso = now.date().isoformat()
    delta = DEADLINE - now
    days_left = delta.days
    hours_left = delta.seconds // 3600

    milestone = MILESTONES.get(today_iso, "(no scheduled milestone — check MASTER-PLAN.md)")

    print("=" * 70)
    print(f"  MANTLE TURING TEST — CONTEST STATUS  ({today_iso})")
    print("=" * 70)
    print(f"  Deadline:   2026-06-15 10:59 UTC")
    print(f"  Time left:  {days_left} days, {hours_left} hours")
    print(f"  Today:      {milestone}")

    # Next hard pin
    upcoming_pins = [(d, label) for d, label in HARD_PINS.items() if d >= today_iso]
    if upcoming_pins:
        next_pin_date, next_pin_label = sorted(upcoming_pins)[0]
        pin_dt = datetime.fromisoformat(next_pin_date).replace(tzinfo=timezone.utc)
        pin_days = (pin_dt.date() - now.date()).days
        print(f"  Next pin:   {next_pin_label} (in {pin_days} days, {next_pin_date})")

    print("-" * 70)
    print("  STAY-ON-CRITERIA REMINDERS:")
    for r in CRITERIA_REMINDERS:
        print(f"   • {r}")
    print("=" * 70)


if __name__ == "__main__":
    main()
