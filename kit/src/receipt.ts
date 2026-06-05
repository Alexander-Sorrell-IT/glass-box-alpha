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
