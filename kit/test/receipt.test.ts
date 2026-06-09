// Parity test: the SDK's receipt hashing MUST match the reference stack byte-for-byte.
// These golden values are copied verbatim from agents/tests/test_receipt.py — if the
// SDK ever drifts from the Python agent / Solidity contract / browser, this fails loudly.
import { describe, expect, it } from "vitest";
import {
  type ReasoningChain,
  canonicalReceipt,
  receiptHash,
  parseProvenance,
  isFullyLive,
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

// Second golden vector — PRODUCTION provenance format ("source:mode[@ref]") in data_sources.
// Copied verbatim from agents/tests/test_receipt.py; pins cross-language byte-parity for the
// shape real agents emit, not just the legacy bare entry.
const GOLDEN_CHAIN_V2: ReasoningChain = {
  ...GOLDEN_CHAIN,
  data_sources: ["mantle-rpc:live@block=12345", "nansen:mock"],
};
const GOLDEN_CANONICAL_V2 =
  '{"agent_id":1,"completion_tokens":200,' +
  '"data_sources":["mantle-rpc:live@block=12345","nansen:mock"],"decision_index":0,' +
  '"model":"deepseek-reasoner","prompt_tokens":100,' +
  '"steps":[{"step":1,"thought":"net inflow +$1.2M"},{"step":2,"thought":"bullish"}],' +
  '"timestamp":1700000000}';
const GOLDEN_KECCAK_V2 =
  "0xdad4f919a0eb10033dde1cc748cc45f72cd1f7b77e8062d599108aeef6cee33e";

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

  it("production provenance format matches the reference byte-for-byte (V2 vector)", () => {
    expect(canonicalReceipt(GOLDEN_CHAIN_V2)).toBe(GOLDEN_CANONICAL_V2);
    expect(receiptHash(GOLDEN_CHAIN_V2)).toBe(GOLDEN_KECCAK_V2);
  });
});

describe("provenance", () => {
  const withSources = (data_sources: string[]): ReasoningChain => ({
    ...GOLDEN_CHAIN,
    data_sources,
  });

  it("parses source/mode/ref and tolerates legacy bare names", () => {
    const p = parseProvenance(
      withSources(["nansen:mock", "mantle-rpc:live@block=12345", "nansen"]),
    );
    expect(p[0]).toEqual({ source: "nansen", mode: "mock" });
    expect(p[1]).toEqual({ source: "mantle-rpc", mode: "live", ref: "block=12345" });
    expect(p[2]).toEqual({ source: "nansen", mode: "unknown" }); // bare → unconfirmable
  });

  it("a mock source is committed into the hash (flip mock→live turns it red)", () => {
    expect(receiptHash(withSources(["nansen:mock"]))).not.toBe(
      receiptHash(withSources(["nansen:live"])),
    );
  });

  it("normalizes mode casing/whitespace and keeps ref on bare names", () => {
    const p = parseProvenance(withSources(["src:LIVE", "x: mock ", "nansen@2025"]));
    expect(p[0].mode).toBe("live"); // case-insensitive
    expect(p[1].mode).toBe("mock"); // whitespace-trimmed
    expect(p[2]).toEqual({ source: "nansen", mode: "unknown", ref: "2025" }); // ref preserved
  });

  it("isFullyLive is true only when every source is confirmably real", () => {
    expect(isFullyLive(withSources(["nansen:live", "mantle-rpc:live@block=9"]))).toBe(true);
    expect(isFullyLive(withSources(["nansen:live", "elfa:mock"]))).toBe(false);
    expect(isFullyLive(withSources(["nansen"]))).toBe(false); // unknown liveness → not live
    expect(isFullyLive(withSources([]))).toBe(false);
    expect(isFullyLive(withSources(["peers:internal"]))).toBe(true); // DA: honest, not mock
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
