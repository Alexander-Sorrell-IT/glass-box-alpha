// On-chain commit/verify helpers for the ReasoningHashAnchor contract — the part
// that makes a reasoning receipt verifiable by anyone, not just auditable in theory.
//
// commit(): seal a chain's keccak256 on Mantle BEFORE the market settles.
// verify(): hand the contract the raw canonical bytes; it re-hashes and compares.
//           Flip one byte of the bytes and `ok` flips to false — the tamper test.
import {
  type Address,
  type PublicClient,
  type WalletClient,
  stringToHex,
} from "viem";
import { type ReasoningChain, canonicalReceipt, receiptHash } from "./receipt.js";

/** ReasoningHashAnchor, live on Mantle Sepolia (chain 5003), deployed 2026-05-30. */
export const REASONING_HASH_ANCHOR_SEPOLIA: Address =
  "0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d";

/** Minimal ABI for the anchor — commit, verify, and reads. */
export const reasoningHashAnchorAbi = [
  {
    type: "function",
    name: "commit",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agentId", type: "uint256" },
      { name: "decisionIndex", type: "uint256" },
      { name: "reasoningHash", type: "bytes32" },
    ],
    outputs: [{ name: "commitIdx", type: "uint256" }],
  },
  {
    type: "function",
    name: "verify",
    stateMutability: "view",
    inputs: [
      { name: "agentId", type: "uint256" },
      { name: "decisionIndex", type: "uint256" },
      { name: "canonicalJson", type: "bytes" },
    ],
    outputs: [
      { name: "ok", type: "bool" },
      { name: "stored", type: "bytes32" },
      { name: "recomputed", type: "bytes32" },
    ],
  },
  {
    type: "function",
    name: "commitsCount",
    stateMutability: "view",
    inputs: [],
    outputs: [{ name: "", type: "uint256" }],
  },
] as const;

/**
 * Commit a reasoning chain's receipt hash on-chain. Returns the transaction hash.
 * Reverts (AlreadyCommitted) if this (agentId, decisionIndex) was already sealed.
 */
export async function commitReasoning(args: {
  walletClient: WalletClient;
  anchor?: Address;
  chain: ReasoningChain;
}): Promise<`0x${string}`> {
  const anchor = args.anchor ?? REASONING_HASH_ANCHOR_SEPOLIA;
  const account = args.walletClient.account;
  if (!account) throw new Error("walletClient has no account");
  return args.walletClient.writeContract({
    address: anchor,
    abi: reasoningHashAnchorAbi,
    functionName: "commit",
    args: [
      BigInt(args.chain.agent_id),
      BigInt(args.chain.decision_index),
      receiptHash(args.chain),
    ],
    account,
    chain: args.walletClient.chain,
  });
}

/**
 * Verify a published reasoning chain against its on-chain commit. The contract
 * re-hashes the exact canonical bytes and reports whether they match. Tamper with
 * the chain (any field) and `ok` comes back false.
 */
export async function verifyReasoning(args: {
  publicClient: PublicClient;
  anchor?: Address;
  agentId: number;
  decisionIndex: number;
  chain: ReasoningChain;
}): Promise<{ ok: boolean; stored: `0x${string}`; recomputed: `0x${string}` }> {
  const anchor = args.anchor ?? REASONING_HASH_ANCHOR_SEPOLIA;
  const [ok, stored, recomputed] = await args.publicClient.readContract({
    address: anchor,
    abi: reasoningHashAnchorAbi,
    functionName: "verify",
    args: [
      BigInt(args.agentId),
      BigInt(args.decisionIndex),
      stringToHex(canonicalReceipt(args.chain)),
    ],
  });
  return { ok, stored, recomputed };
}
