// Parity test: the SDK's receipt hashing MUST match the reference stack byte-for-byte.
// These golden values are copied verbatim from agents/tests/test_receipt.py — if the
// SDK ever drifts from the Python agent / Solidity contract / browser, this fails loudly.
import { describe, expect, it } from "vitest";
import {
  type ReasoningChain,
  canonicalReceipt,
  receiptHash,
  foldEnsemble,
  type Decision,
} from "../src/index.js";

const GOLDEN_CHAIN: ReasoningChain = {
  agent_id: 1,
  decision_index: 0,
  model: "deepseek-reasoner",
  prompt_tokens: 100,
  completion_tokens: 200,
  steps: [
    { step: 1, thought: "net inflow +$1.2M" },
    { step: 2, thought: "bullish" },
  ],
  data_sources: ["nansen"],
  timestamp: 1700000000,
};

const GOLDEN_CANONICAL =
  '{"agent_id":1,"completion_tokens":200,"data_sources":["nansen"],"decision_index":0,' +
  '"model":"deepseek-reasoner","prompt_tokens":100,' +
  '"steps":[{"step":1,"thought":"net inflow +$1.2M"},{"step":2,"thought":"bullish"}],' +
  '"timestamp":1700000000}';

const GOLDEN_KECCAK =
  "0xf8aed1ad2a6bcdf567b73fb7fe2814f93d83f7ee1ffdea7d6e70eb663f55b82a";

describe("reasoning receipt parity", () => {
  it("canonical bytes match the frozen reference (Python json.dumps sort_keys)", () => {
    expect(canonicalReceipt(GOLDEN_CHAIN)).toBe(GOLDEN_CANONICAL);
  });

  it("keccak256 matches the on-chain commit value", () => {
    expect(receiptHash(GOLDEN_CHAIN)).toBe(GOLDEN_KECCAK);
  });

  it("a single-byte tamper changes the hash", () => {
    const tampered = structuredClone(GOLDEN_CHAIN);
    tampered.steps[1].thought = "bearish"; // was "bullish"
    expect(receiptHash(tampered)).not.toBe(GOLDEN_KECCAK);
  });
});

describe("fold ensemble", () => {
  it("confidence-weights the directional signal", () => {
    const d = (signal: number, confidence: number): Decision => ({
      agent_id: 0,
      decision_index: 0,
      timestamp: 0,
      kind: "SPOT_SWAP",
      market_id: "mETH/USDC",
      directional_signal: signal,
      size_bps: 1000,
      confidence,
    });
    // high-confidence +1 should dominate a low-confidence -1
    const fold = foldEnsemble([d(1, 0.9), d(-1, 0.1)]);
    expect(fold.directional_signal).toBeGreaterThan(0.5);
    expect(fold.size_bps).toBe(1000);
  });

  it("empty input is a flat HOLD-equivalent", () => {
    expect(foldEnsemble([])).toEqual({
      directional_signal: 0,
      size_bps: 0,
      confidence: 0,
    });
  });
});
