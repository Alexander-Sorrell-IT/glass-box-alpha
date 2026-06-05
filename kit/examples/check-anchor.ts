// Read-only sanity check: does the kit's ABI decode the LIVE contract, and which
// (agentId, decisionIndex) slots are already committed? No key, no writes.
import { createPublicClient, http } from "viem";
import {
  REASONING_HASH_ANCHOR_SEPOLIA,
  reasoningHashAnchorAbi,
  mantleSepolia,
} from "../src/index.js";

const client = createPublicClient({ chain: mantleSepolia, transport: http() });

const count = await client.readContract({
  address: REASONING_HASH_ANCHOR_SEPOLIA,
  abi: reasoningHashAnchorAbi,
  functionName: "commitsCount",
});
console.log("commitsCount =", count.toString());

// Probe a few (agentId, decisionIndex) slots via verify() with empty bytes:
// it reverts "no commit" if the slot is free, else returns (false, stored, recomputed).
for (const agentId of [0n, 1n, 2n, 3n, 4n]) {
  for (const idx of [0n, 1n]) {
    try {
      const [ok, stored] = await client.readContract({
        address: REASONING_HASH_ANCHOR_SEPOLIA,
        abi: reasoningHashAnchorAbi,
        functionName: "verify",
        args: [agentId, idx, "0x"],
      });
      console.log(`agent ${agentId} idx ${idx}: COMMITTED (stored ${stored})`);
    } catch {
      // "no commit" → slot is free
    }
  }
}
