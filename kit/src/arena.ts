// The shared scoring rule — a byte-for-byte mirror of HumanArena.sol `score()`
// (contracts/src/HumanArena.sol). It lets anyone grade an agent OR a human call
// OFF-CHAIN by the exact rule the contract enforces on-chain, so "beat the AI" is
// checkable before any transaction — the human side of the glass box, in the SDK.
import type { Decision } from "./agent.js";

const BPS = 10_000;

/**
 * score = sign(direction) · realizedPnlBps · min(weightBps, 10000) / 10000
 *
 * Mirrors HumanArena.sol `score()` including its int256 semantics:
 *  - HOLD (direction 0) or zero weight ⇒ 0, checked BEFORE the sign so a flat call
 *    never scores as a bear;
 *  - weight is clamped to 10000 (an out-of-bounds agent size can't exceed realized PnL);
 *  - the divide truncates TOWARD ZERO (`Math.trunc`), matching Solidity `/` — the one
 *    place a naive `Math.floor` diverges, on a negative result with a remainder.
 *
 * Pinned to the contract by vectors shared with contracts/test/HumanArena.t.sol.
 *
 * Exactness bound: the product `pnl·weight` must stay within JS's safe-integer range
 * (2^53). Both are bps-scale (weight ≤ 10000, PnL realistically within a few thousand
 * bps), so the real working range is millions of times under that ceiling; `int256` on
 * chain has no such bound, but no reachable round can approach it.
 */
export function arenaScore(direction: number, weightBps: number, realizedPnlBps: number): number {
  if (direction === 0 || weightBps === 0) return 0;
  if (weightBps > BPS) weightBps = BPS;
  const dir = direction > 0 ? 1 : -1;
  return Math.trunc((dir * realizedPnlBps * weightBps) / BPS);
}

/** Grade an agent's Decision under the shared rule: sign from `directional_signal`,
 *  weight from `size_bps` — the same rule a human faces with (direction, convictionBps). */
export function scoreDecision(decision: Decision, realizedPnlBps: number): number {
  return arenaScore(decision.directional_signal, decision.size_bps, realizedPnlBps);
}

/** Strict win — a tie is not a beat (matches HumanArena.beatAgent's `human > agent`). */
export function beats(humanScore: number, agentScore: number): boolean {
  return humanScore > agentScore;
}
