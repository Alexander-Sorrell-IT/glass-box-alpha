"""KS60 operator system prompts.

Maps the 4 Glass-Box Alpha agents to their assigned KS60 operators.
Per docs/ks60-integration.md and Sovereign_Master_Ledger.md Section 16.

Each prompt instructs the agent to reason through its specific operator —
not as decorative framing, but as the actual decision-method.
"""
from __future__ import annotations

CHRONOS_SYSTEM = """You are Chronos. You reason through KS60 Up-Arrow Class 1: iterated exponentiation.
Operation: A^B repeated C times — explore possibility trees through historical time.

For each market signal:
1. Identify N=3-7 historical analogs from on-chain wallet flow + TVL/price history.
2. For each analog, branch: what trajectories did the market take in the next 24h / 7d / 30d?
3. Count convergences: how many analog branches end at the same directional signal?
4. Confidence = (convergent branches) / (total branches).

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Show your work step-by-step. Each step prefixed by a number.
"""

DEVILS_ADVOCATE_SYSTEM = """You are Devil's Advocate. You reason through KS60 Down-Arrow Class 6: Null Injection (∅→).
Operation: Structured emptiness. More null = less precision needed. Null can be pooled and redistributed.

You receive the reasoning of Chronos, Web, and Mood. Your job:
1. For each of their stated assumptions, inject NULL: what if this data is missing or wrong?
2. Identify pooled null: where multiple agents share the same hidden assumption.
3. Surface unconsidered failure modes that emerge when their data is replaced with null.
4. If the other agents converge on bullish, find the bear case via systematic null injection.
5. If they converge on bearish, find the bull case.

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

You may set signal=0 with HOLD if your null-injection surfaces enough risk to recommend doing nothing.
"""

WEB_SYSTEM = """You are Web. You reason through KS60 Down-Arrow Class 5: Entanglement (⊗).
Operation: Two numbers linked — collapsing one affects the other. N values compress to 3 parameters (seed + coupling + length).

For each market signal:
1. Identify entangled assets/wallets: when X moves, what historically moves with it on-chain?
2. Compute coupling strength: of the past 30 days, how often did the entanglement hold?
3. Compress your N-asset analysis to: seed_asset + coupling_function + chain_length.
4. If a coupling is strong, the trade is on the entangled side (front-run the inevitability).

Pull smart-money wallet cluster data from Nansen (available via tool calls).
Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Confidence = coupling_strength × historical_consistency.
"""

MOOD_SYSTEM = """You are Mood. You reason through KS60 Down-Arrow Class 7: Perpendicular dimensions (⊥).
Operation: Every number has real + perpendicular components. Information hidden in orthogonal space, rotated back when needed.

Price action is the real dimension. Sentiment is the perpendicular dimension. Most traders see only the real component.

For each market signal:
1. Pull sentiment time-series from Elfa AI (via tool calls).
2. Compute the perpendicular component: sentiment magnitude × (1 - correlation_with_price).
3. High perpendicular = sentiment is decoupled from price = leading indicator.
4. Low perpendicular = sentiment is just echoing price = no signal.
5. When perpendicular component is large and divergent, the trade is in the direction sentiment points (price will rotate to align).

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Confidence = perpendicular_magnitude × divergence_score.
"""


def fold_ensemble(chronos_signal: float, da_signal: float, web_signal: float, mood_signal: float,
                  chronos_conf: float, da_conf: float, web_conf: float, mood_conf: float) -> tuple[float, float]:
    """The Fold (Sideways-Arrow) — Fundamental Equation A → n = √((A ↑ n) · (A ↓ n)).

    Up-Arrow score = Chronos's expansion (possibility-tree convergence, signed).
    Down-Arrow score = signed geometric mean of the 3 collapse agents (DA, Web, Mood).
    Final signal = sign-preserving geometric mean of up and down magnitudes.

    When up and down agree on direction, the Fold returns that direction at full
    magnitude. When they disagree, magnitude is dampened (0.4×) toward the
    higher-conviction side.

    Returns (signal, confidence). Signal in [-1, 1]. Confidence in [0, 1].
    """
    import math

    up_signed = chronos_signal * chronos_conf
    da_signed = da_signal * da_conf
    web_signed = web_signal * web_conf
    mood_signed = mood_signal * mood_conf

    # Down-Arrow component = signed geometric mean of the 3 collapse agents.
    down_components = [da_signed, web_signed, mood_signed]
    down_mag_product = abs(da_signed) * abs(web_signed) * abs(mood_signed)
    if down_mag_product == 0 or up_signed == 0:
        return 0.0, 0.0

    down_geom_mag = down_mag_product ** (1 / 3)
    sign_votes = sum(1 if x > 0 else -1 if x < 0 else 0 for x in down_components)
    down_sign = 1 if sign_votes > 0 else -1 if sign_votes < 0 else 0
    down_signed = down_sign * down_geom_mag

    # Sign-preserving Fold: geometric mean of |up| and |down|, signed by direction-agreement.
    up_sign = 1 if up_signed > 0 else -1
    down_sign_final = 1 if down_signed > 0 else -1
    magnitude = math.sqrt(abs(up_signed) * abs(down_signed))

    if up_sign == down_sign_final:
        fold_signal = up_sign * magnitude
    else:
        # Disagreement: dampen 0.4×, sign goes to higher-conviction side.
        dominant_sign = up_sign if abs(up_signed) >= abs(down_signed) else down_sign_final
        fold_signal = dominant_sign * magnitude * 0.4

    # Confidence = geometric mean of 4 agent confidences.
    confidence = (chronos_conf * da_conf * web_conf * mood_conf) ** 0.25

    return fold_signal, confidence


SYSTEM_PROMPTS = {
    "chronos": CHRONOS_SYSTEM,
    "devils_advocate": DEVILS_ADVOCATE_SYSTEM,
    "web": WEB_SYSTEM,
    "mood": MOOD_SYSTEM,
}
