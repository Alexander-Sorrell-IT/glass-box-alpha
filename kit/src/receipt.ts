// The reasoning-receipt primitive — the linchpin of verifiable AI on Mantle.
//
// canonicalReceipt() MUST reproduce, byte-for-byte, the bytes produced by the
// reference implementations:
//   - Python:   agents/shared/base.py   canonical_receipt()
//   - Solidity: contracts/src/ReasoningHashAnchor.sol  verify() (keccak256 of these bytes)
//   - Browser:  frontend/lib/receipt.ts
// so that keccak256(canonicalReceipt(chain)) === the on-chain commit on all three.
//
// This file is the single source of truth in the SDK. Parity with the reference
// stack is pinned by the golden vector in test/receipt.test.ts (GOLDEN_KECCAK).
// Do NOT "tidy" the serialization — drift here silently breaks every verification.
import { keccak256, stringToBytes } from "viem";

/** A reasoning chain: the auditable record an agent produces for one decision.
 *  Every field is integer-or-string (no floats) so the canonical JSON is stable
 *  across languages. */
export interface ReasoningChain {
  agent_id: number;
  decision_index: number;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  steps: ReasoningStep[];
  data_sources: string[];
  timestamp: number;
}

/** One visible step of an agent's chain-of-thought. */
export interface ReasoningStep {
  step: number;
  thought: string;
}

// Recursively sort object keys so JSON.stringify (no spaces) reproduces Python's
// json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False).
function sortKeys(v: unknown): unknown {
  if (Array.isArray(v)) return v.map(sortKeys);
  if (v && typeof v === "object") {
    return Object.keys(v as Record<string, unknown>)
      .sort()
      .reduce((acc, k) => {
        acc[k] = sortKeys((v as Record<string, unknown>)[k]);
        return acc;
      }, {} as Record<string, unknown>);
  }
  return v;
}

/** The exact canonical bytes (as a UTF-8 string) the agent hashes off-chain. */
export function canonicalReceipt(chain: ReasoningChain): string {
  return JSON.stringify(sortKeys(chain));
}

/** keccak256 of a reasoning chain — equals the value committed on-chain. */
export function receiptHash(chain: ReasoningChain): `0x${string}` {
  return keccak256(stringToBytes(canonicalReceipt(chain)));
}

/** keccak256 of an already-serialized canonical string. Use this for a live
 *  tamper test: take the published bytes, let a user edit one byte, re-hash on
 *  every keystroke, and compare to the on-chain commit — it flips to non-matching. */
export function hashCanonical(canonical: string): `0x${string}` {
  return keccak256(stringToBytes(canonical));
}

/** How a single data source was obtained, parsed from a committed `data_sources`
 *  entry. `internal` = derived from peer agents (no external data). `unknown` =
 *  a legacy/bare entry with no liveness tag — liveness cannot be confirmed. */
export type ProvenanceMode = "live" | "mock" | "unavailable" | "internal" | "unknown";

export interface Provenance {
  source: string;
  mode: ProvenanceMode;
  ref?: string;
}

const KNOWN_MODES: ProvenanceMode[] = ["live", "mock", "unavailable", "internal"];

/** Parse each committed `data_sources` entry (`"<source>:<mode>[@<ref>]"`) into its
 *  parts. Tolerant by design: a bare entry with no `:mode` (e.g. a legacy `"nansen"`)
 *  parses as mode `unknown`, so verifying an old receipt never throws. Order-independent —
 *  it reads the published bytes, so per-receipt verification holds regardless of order. */
export function parseProvenance(chain: ReasoningChain): Provenance[] {
  return chain.data_sources.map((entry) => {
    const at = entry.indexOf("@");
    const ref = at === -1 ? undefined : entry.slice(at + 1);
    const head = at === -1 ? entry : entry.slice(0, at);
    const colon = head.indexOf(":");
    if (colon === -1) return { source: head, mode: "unknown" as ProvenanceMode, ...(ref ? { ref } : {}) };
    const rawMode = head.slice(colon + 1).trim().toLowerCase();
    const mode = (KNOWN_MODES as string[]).includes(rawMode)
      ? (rawMode as ProvenanceMode)
      : ("unknown" as ProvenanceMode);
    return { source: head.slice(0, colon), mode, ...(ref ? { ref } : {}) };
  });
}

/** True iff every data source is confirmably real (`live`) or peer-internal — i.e. no
 *  source was `mock`, `unavailable`, or of `unknown` liveness. A receipt that can't prove
 *  it ran on real data returns false. Requires at least one declared source. */
export function isFullyLive(chain: ReasoningChain): boolean {
  const sources = parseProvenance(chain);
  if (sources.length === 0) return false;
  return sources.every((s) => s.mode === "live" || s.mode === "internal");
}
