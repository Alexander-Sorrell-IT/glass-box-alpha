// The transparent-agent interface. Subclass GlassBoxAgent, implement reason(),
// and you get a reproducible reasoning chain + its on-chain-ready receipt hash for
// free. The kit is LLM-agnostic: wire DeepSeek, Claude, a local model, or pure
// deterministic math inside reason() — the receipt primitive doesn't care.
import { type ReasoningChain, type ReasoningStep, receiptHash } from "./receipt.js";

export type DecisionKind =
  | "SPOT_SWAP"
  | "LP_DEPOSIT"
  | "LP_WITHDRAW"
  | "PERP_LONG"
  | "PERP_SHORT"
  | "HOLD"
  | "HEDGE";

/** A directional call, scored later by the same on-chain rule for agents and humans. */
export interface Decision {
  agent_id: number;
  decision_index: number;
  timestamp: number;
  kind: DecisionKind;
  market_id: string;
  directional_signal: number; // -1..1
  size_bps: number; // 0..10000
  confidence: number; // 0..1
}

/** What an agent implementation returns from reason(): the visible thinking, the
 *  call, and the provenance (model + data sources) that go into the audited chain. */
export interface RawReasoning {
  steps: ReasoningStep[];
  decision: Omit<Decision, "agent_id" | "decision_index" | "timestamp">;
  model: string;
  data_sources: string[];
  prompt_tokens?: number;
  completion_tokens?: number;
}

export interface ReasoningResult {
  decision: Decision;
  chain: ReasoningChain;
  /** keccak256 of the canonical chain — commit this on-chain BEFORE the market moves. */
  hash: `0x${string}`;
}

export abstract class GlassBoxAgent {
  readonly agentId: number;
  protected decisionIndex = 0;

  /** @param agentId the agent's ERC-8004 identity token id. */
  constructor(agentId: number) {
    this.agentId = agentId;
  }

  /** Implement your reasoning frame here: produce visible steps and a decision. */
  protected abstract reason(marketId: string): Promise<RawReasoning>;

  /**
   * Run one decision cycle and assemble the auditable chain + receipt hash.
   * `now` (unix seconds) is passed in, not read from the clock, so a receipt is
   * fully reproducible — anyone can recompute the exact same hash later.
   */
  async decide(marketId: string, now: number): Promise<ReasoningResult> {
    const raw = await this.reason(marketId);
    const decision_index = this.decisionIndex++;

    const chain: ReasoningChain = {
      agent_id: this.agentId,
      decision_index,
      model: raw.model,
      prompt_tokens: raw.prompt_tokens ?? 0,
      completion_tokens: raw.completion_tokens ?? 0,
      steps: raw.steps,
      data_sources: raw.data_sources,
      timestamp: now,
    };

    const decision: Decision = {
      agent_id: this.agentId,
      decision_index,
      timestamp: now,
      ...raw.decision,
    };

    return { decision, chain, hash: receiptHash(chain) };
  }
}

/**
 * The Fold: a confidence-weighted consensus of several agents' decisions.
 * Returns the weighted directional signal and mean size/confidence. Deliberately
 * simple and transparent — it makes no claim to beat a plain mean; it's the
 * combining rule, published so anyone can reproduce the ensemble call.
 */
export function foldEnsemble(decisions: Decision[]): {
  directional_signal: number;
  size_bps: number;
  confidence: number;
} {
  if (decisions.length === 0) {
    return { directional_signal: 0, size_bps: 0, confidence: 0 };
  }
  const totalConf = decisions.reduce((s, d) => s + d.confidence, 0);
  const weight = totalConf > 0 ? totalConf : decisions.length;
  const signal =
    decisions.reduce(
      (s, d) => s + d.directional_signal * (totalConf > 0 ? d.confidence : 1),
      0,
    ) / weight;
  const size = Math.round(
    decisions.reduce((s, d) => s + d.size_bps, 0) / decisions.length,
  );
  const confidence = totalConf / decisions.length;
  return { directional_signal: signal, size_bps: size, confidence };
}
