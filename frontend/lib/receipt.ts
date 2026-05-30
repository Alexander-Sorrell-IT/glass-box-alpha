// In-browser reasoning-receipt hashing — the client half of the verifiability claim.
// canonicalReceipt() MUST reproduce, byte-for-byte, the bytes that
// agents/shared/base.py canonical_receipt() produces, so that
// keccak256(canonicalReceipt(chain)) === the on-chain commit === the Python reasoning_hash.
// Pinned by the golden vector in agents/tests/test_receipt.py.
import { keccak256, stringToBytes } from "viem";

export interface ReasoningChain {
  agent_id: number;
  decision_index: number;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  steps: { step: number; thought: string }[];
  data_sources: string[];
  timestamp: number;
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

/** The exact canonical bytes (as a UTF-8 string) — matches base.py canonical_receipt(). */
export function canonicalReceipt(chain: ReasoningChain): string {
  return JSON.stringify(sortKeys(chain));
}

/** keccak256 of a reasoning chain — equals the on-chain commit. */
export function receiptHash(chain: ReasoningChain): `0x${string}` {
  return keccak256(stringToBytes(canonicalReceipt(chain)));
}

/** keccak256 of an already-serialized canonical string — used by the live tamper box,
 *  where the user edits the raw bytes directly and we re-hash on every keystroke. */
export function hashCanonical(canonical: string): `0x${string}` {
  return keccak256(stringToBytes(canonical));
}
