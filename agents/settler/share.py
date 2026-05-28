"""Build shareable card URLs + tweet copy from a round outcome.

Connects the settler service to the build-in-public X campaign. The OG card is
rendered by the frontend's /api/og edge route; this module constructs the URL
+ the tweet text. Actual posting happens via the X API once keys are wired
(Day 14+), or manually by copy-pasting the generated copy.
"""
from __future__ import annotations

from urllib.parse import urlencode

from agents.settler.service import RoundOutcome

DEFAULT_BASE = "https://glass-box-alpha.vercel.app"


def share_card_url(outcome: RoundOutcome, pnl_pct: float | None = None,
                   base_url: str = DEFAULT_BASE) -> str:
    """Construct the OG share-card image URL for a round outcome."""
    signals = {a["name"]: a["decision"]["directional_signal"] for a in outcome.agent_records}
    params = {
        "market": outcome.market_id,
        "signal": f"{outcome.ensemble_signal:.2f}",
        "confidence": f"{outcome.ensemble_confidence * 100:.0f}",
        "round": str(outcome.round_id),
        "chronos": f"{signals.get('chronos', 0):.2f}",
        "da": f"{signals.get('devils_advocate', 0):.2f}",
        "web": f"{signals.get('web', 0):.2f}",
        "mood": f"{signals.get('mood', 0):.2f}",
    }
    if pnl_pct is not None:
        params["pnl"] = f"{pnl_pct:.2f}"
    return f"{base_url}/api/og?{urlencode(params)}"


def tweet_copy(outcome: RoundOutcome, pnl_pct: float | None = None) -> str:
    """Generate the tweet text for a round result. Stays under 280 chars."""
    direction = "bullish" if outcome.ensemble_signal > 0 else "bearish" if outcome.ensemble_signal < 0 else "neutral"
    arrow = "📈" if outcome.ensemble_signal > 0 else "📉" if outcome.ensemble_signal < 0 else "➡️"

    if not outcome.trade_executed:
        # Risk gate blocked the trade — that's a feature, show it
        return (
            f"{arrow} Round #{outcome.round_id} · {outcome.market_id}\n\n"
            f"4 agents reasoned. Fold ensemble: {outcome.ensemble_signal:+.2f} "
            f"({outcome.ensemble_confidence*100:.0f}% conf)\n\n"
            f"Trade SKIPPED — {outcome.rejection_reason}.\n"
            f"Risk gate working as designed. Reasoning hashed on-chain. 🔗\n\n"
            f"#MantleAIHackathon"
        )

    pnl_line = f"PnL {pnl_pct:+.2f}% · " if pnl_pct is not None else ""
    return (
        f"{arrow} Round #{outcome.round_id} · {outcome.market_id}\n\n"
        f"4 AI agents → Fold ensemble: {outcome.ensemble_signal:+.2f} {direction} "
        f"({outcome.ensemble_confidence*100:.0f}% conf)\n"
        f"{pnl_line}every reasoning chain hashed on Mantle 🔗\n\n"
        f"Watch them think → glass-box-alpha.vercel.app\n"
        f"#MantleAIHackathon"
    )
