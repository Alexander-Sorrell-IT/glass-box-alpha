// Parity test: the SDK's arenaScore() MUST match HumanArena.sol score() — the rule that
// grades agents and humans on-chain. Vectors are shared VERBATIM with
// contracts/test/HumanArena.t.sol; if TS and Solidity ever diverge, one side flips here.
// The negative-remainder vectors are load-bearing: they distinguish truncate-toward-zero
// (Solidity `/`, Math.trunc) from Math.floor — every clean-division vector hides that bug.
import { describe, expect, it } from "vitest";
import { arenaScore, scoreDecision, beats, GlassBoxAgent, type Decision, type RawReasoning } from "../src/index.js";
import { parseProvenance, isFullyLive, canonicalReceipt, hashCanonical, receiptHash } from "../src/index.js";

describe("arenaScore — parity with HumanArena.sol score()", () => {
  it("matches the contract's sign / weight / clamp vectors", () => {
    expect(arenaScore(1, 10_000, 100)).toBe(100);
    expect(arenaScore(-1, 10_000, 100)).toBe(-100);
    expect(arenaScore(1, 5_000, 100)).toBe(50);
    expect(arenaScore(0, 10_000, 100)).toBe(0); // HOLD ⇒ 0, guard runs before the sign
    expect(arenaScore(1, 0, 100)).toBe(0);
    expect(arenaScore(0.62, 10_000, 100)).toBe(100); // any positive signal normalizes to +1
    expect(arenaScore(1, 20_000, 100)).toBe(100); // weight clamped to 10_000
    expect(arenaScore(1, 50_000, 100)).toBe(100);
  });

  it("truncates toward zero on a negative remainder (floor would diverge)", () => {
    expect(arenaScore(-1, 3333, 100)).toBe(-33); // -33.33 → -33, NOT -34
    expect(arenaScore(1, 3333, 100)).toBe(33);
    expect(arenaScore(1, 3333, -100)).toBe(-33);
  });

  it("reproduces the money-path vectors from HumanArena.t.sol", () => {
    expect(arenaScore(1, 8000, 120)).toBe(96); // human, high conviction, right way
    expect(arenaScore(0.62, 2500, 120)).toBe(30); // agent, size 2500
    expect(arenaScore(-1, 10_000, 80)).toBe(-80); // full conviction, wrong way
    expect(arenaScore(-0.5, 4000, -150)).toBe(60); // bearish call, market down ⇒ wins
  });
});

describe("scoreDecision + beats", () => {
  const decision = (signal: number, size_bps: number): Decision => ({
    agent_id: 8242, decision_index: 0, timestamp: 0, kind: "PERP_LONG",
    market_id: "mETH/USDC", directional_signal: signal, size_bps, confidence: 0.6,
  });

  it("grades an agent decision; a more-convinced stranger beats it under the same rule", () => {
    const pnl = 120;
    const agent = scoreDecision(decision(0.62, 2500), pnl); // 30
    const stranger = arenaScore(1, 8000, pnl); // 96
    expect(agent).toBe(30);
    expect(stranger).toBe(96);
    expect(beats(stranger, agent)).toBe(true);
    expect(beats(agent, agent)).toBe(false); // a tie is not a win (strict >)
  });
});

// The whole point of the task: a FOREIGN agent built on nothing but the kit produces a
// receipt that is checkable (recompute + provenance) and beatable (shared score).
describe("foreign agent is checkable and beatable with only the kit", () => {
  class FundingSkewAgent extends GlassBoxAgent {
    constructor(private fundingBps8h: number) { super(8242); } // id outside the built-in 1..4
    protected async reason(marketId: string): Promise<RawReasoning> {
      const bearish = this.fundingBps8h > 0;
      return {
        model: "funding-skew-v1",
        data_sources: ["funding-oracle:live@block=19000123", "dex-mid:mock"],
        steps: [{ step: 1, thought: `funding ${this.fundingBps8h}bps` }],
        decision: {
          kind: bearish ? "PERP_SHORT" : "PERP_LONG", market_id: marketId,
          directional_signal: Math.max(-1, Math.min(1, -this.fundingBps8h / 50)),
          size_bps: 2200, confidence: 0.7,
        },
      };
    }
  }

  it("recomputes, catches a tamper, reports honest liveness, and loses to a better call", async () => {
    const { decision, chain, hash } = await new FundingSkewAgent(18).decide("mETH/USDC", 1_700_000_000);

    // check: local recompute matches; a one-token tamper breaks it
    const pristine = canonicalReceipt(chain);
    expect(hashCanonical(pristine)).toBe(receiptHash(chain));
    expect(hashCanonical(pristine.replace("funding-skew-v1", "funding-skew-v2"))).not.toBe(hash);

    // provenance: a mock source means the receipt is honestly NOT fully live
    const modes = parseProvenance(chain).map((p) => p.mode).sort();
    expect(modes).toEqual(["live", "mock"]);
    expect(isFullyLive(chain)).toBe(false);

    // beat: market fell 120bps; both called bear, the stranger had higher conviction
    const pnl = -120;
    const agent = scoreDecision(decision, pnl);
    const stranger = arenaScore(-1, 9000, pnl);
    expect(beats(stranger, agent)).toBe(true);
  });
});
