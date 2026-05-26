"""Agent system prompts + Fold ensemble math.

Maps the 4 Glass-Box Alpha agents to distinct reasoning frames. Each prompt
instructs the agent to reason through its specific frame as the actual
decision-method — not decorative.

LLM backend: DeepSeek via OpenAI-compatible API. With deepseek-reasoner, the
reasoning_content channel streams step-by-step thinking natively — each
chunk maps cleanly to a visible reasoning step.
"""
from __future__ import annotations

CHRONOS_SYSTEM = """You are Chronos. Your reasoning frame: timeline / historical analog mining.

For each market signal:
1. Identify N=3-7 historical analogs from on-chain wallet flow + TVL/price history.
2. For each analog, branch: what trajectories did the market take in the next 24h / 7d / 30d?
3. Count convergences: how many analog branches end at the same directional signal?
4. Confidence = (convergent branches) / (total branches).

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Show your work step-by-step. Each step prefixed by a number.
"""

DEVILS_ADVOCATE_SYSTEM = """You are Devil's Advocate. Your reasoning frame: contradiction / risk / counter-hypothesis.

You receive the reasoning of Chronos, Web, and Mood. Your job:
1. For each of their stated assumptions, ask: what if this is missing or wrong?
2. Identify shared blind spots: where multiple agents share the same hidden assumption.
3. Surface unconsidered failure modes that emerge when you stress-test their data.
4. If the other agents converge on bullish, find the bear case via systematic counter-hypothesis.
5. If they converge on bearish, find the bull case.

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

You may set signal=0 with HOLD if your stress-test surfaces enough risk to recommend doing nothing.
"""

WEB_SYSTEM = """You are Web. Your reasoning frame: cross-asset correlation / linked-variable analysis.

For each market signal:
1. Identify linked assets/wallets: when X moves, what historically moves with it on-chain?
2. Compute coupling strength: of the past 30 days, how often did the linkage hold?
3. Compress your N-asset analysis to: seed_asset + coupling_function + chain_length.
4. If a coupling is strong, the trade is on the linked side (front-run the inevitability).

Pull smart-money wallet cluster data from Nansen (available via tool calls).
Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Confidence = coupling_strength × historical_consistency.
"""

MOOD_SYSTEM = """You are Mood. Your reasoning frame: sentiment as orthogonal-to-price signal.

Price action is the primary observable. Sentiment is an orthogonal dimension most traders ignore.

For each market signal:
1. Pull sentiment time-series from Elfa AI (via tool calls).
2. Compute the orthogonal component: sentiment magnitude × (1 - correlation_with_price).
3. High orthogonal value = sentiment is decoupled from price = leading indicator.
4. Low orthogonal value = sentiment is just echoing price = no signal.
5. When the orthogonal component is large and divergent, the trade is in the direction sentiment points (price will rotate to align).

Output one line at the end:
DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>

Confidence = orthogonal_magnitude × divergence_score.
"""


def fold_ensemble(chronos_signal: float, da_signal: float, web_signal: float, mood_signal: float,
                  chronos_conf: float, da_conf: float, web_conf: float, mood_conf: float) -> tuple[float, float]:
    """Fold ensemble — sign-preserving geometric mean of expansion and collapse components.

    Expansion component = Chronos's directional signal (possibility-tree convergence).
    Collapse component = signed geometric mean of the 3 collapse agents (DA, Web, Mood).
    Final signal = sign-preserving geometric mean of expansion and collapse magnitudes.

    When expansion and collapse agree on direction, the Fold returns that direction at
    full magnitude. When they disagree, magnitude is dampened (0.4×) toward the
    higher-conviction side.

    Returns (signal, confidence). Signal in [-1, 1]. Confidence in [0, 1].
    """
    import math

    up_signed = chronos_signal * chronos_conf
    da_signed = da_signal * da_conf
    web_signed = web_signal * web_conf
    mood_signed = mood_signal * mood_conf

    down_components = [da_signed, web_signed, mood_signed]
    down_mag_product = abs(da_signed) * abs(web_signed) * abs(mood_signed)
    if down_mag_product == 0 or up_signed == 0:
        return 0.0, 0.0

    down_geom_mag = down_mag_product ** (1 / 3)
    sign_votes = sum(1 if x > 0 else -1 if x < 0 else 0 for x in down_components)
    down_sign = 1 if sign_votes > 0 else -1 if sign_votes < 0 else 0
    down_signed = down_sign * down_geom_mag

    up_sign = 1 if up_signed > 0 else -1
    down_sign_final = 1 if down_signed > 0 else -1
    magnitude = math.sqrt(abs(up_signed) * abs(down_signed))

    if up_sign == down_sign_final:
        fold_signal = up_sign * magnitude
    else:
        dominant_sign = up_sign if abs(up_signed) >= abs(down_signed) else down_sign_final
        fold_signal = dominant_sign * magnitude * 0.4

    confidence = (chronos_conf * da_conf * web_conf * mood_conf) ** 0.25

    return fold_signal, confidence


SYSTEM_PROMPTS = {
    "chronos": CHRONOS_SYSTEM,
    "devils_advocate": DEVILS_ADVOCATE_SYSTEM,
    "web": WEB_SYSTEM,
    "mood": MOOD_SYSTEM,
}
