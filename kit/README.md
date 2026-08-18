# glassbox-agent-kit

**Ship a verifiable, transparent AI agent on Mantle in under 30 minutes.**

Most AI agents ask you to *trust* their reasoning. A glass-box agent hands you a **receipt**: it commits the `keccak256` of its canonical reasoning chain to Mantle *before* the outcome is known, and anyone can recompute that hash from the published reasoning — tamper one byte and it stops matching. This kit is the reusable core of [Glass-Box Alpha](../README.md), extracted as a standalone SDK.

The receipt primitive here is **byte-for-byte identical** to the Python agent, the Solidity `ReasoningHashAnchor` contract, and the in-browser verifier — pinned by a golden-vector test (`npm test`). That cross-language match is the whole point: a hash you compute in Node equals the one the contract stored equals the one a stranger recomputes in their browser.

## Install

```bash
npm install glassbox-agent-kit viem
```

## 30-second quickstart

```ts
import { GlassBoxAgent, receiptHash, type RawReasoning } from "glassbox-agent-kit";

class MyAgent extends GlassBoxAgent {
  protected async reason(marketId: string): Promise<RawReasoning> {
    // wire any LLM (DeepSeek, Claude, local) or deterministic logic here
    return {
      model: "my-model-v1",
      // Tag each source's liveness: "<source>:<live|mock|unavailable>[@<ref>]".
      // It rides inside the hashed receipt, so the receipt can't claim mock data was live.
      data_sources: ["nansen:live"],
      steps: [
        { step: 1, thought: "net smart-money inflow is positive" },
        { step: 2, thought: "lean long" },
      ],
      decision: {
        kind: "PERP_LONG",
        market_id: marketId,
        directional_signal: 0.6,
        size_bps: 1500,
        confidence: 0.7,
      },
    };
  }
}

const agent = new MyAgent(/* ERC-8004 token id */ 1);
const { chain, hash } = await agent.decide("mETH/USDC", 1_700_000_000);
console.log(hash); // commit THIS on-chain before the market moves
```

Run the full offline demo:

```bash
npm run example
```

## Commit & verify on-chain

```ts
import {
  commitReasoning,
  verifyReasoning,
  mantleSepolia,
} from "glassbox-agent-kit";
import { createWalletClient, createPublicClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";

const walletClient = createWalletClient({
  account: privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`),
  chain: mantleSepolia,
  transport: http(),
});

// Seal the receipt BEFORE the outcome is known:
const tx = await commitReasoning({ walletClient, chain });

// Later, anyone re-hashes the published chain against the on-chain commit:
const publicClient = createPublicClient({ chain: mantleSepolia, transport: http() });
const { ok } = await verifyReasoning({
  publicClient,
  agentId: chain.agent_id,
  decisionIndex: chain.decision_index,
  chain,
});
// ok === true. Change any field of `chain` and ok flips to false.
```

`commitReasoning` / `verifyReasoning` default to the live `ReasoningHashAnchor` on
Mantle Sepolia (`0xB031…353d`); pass `anchor` to point at your own deployment.

## Check *and* beat — the kit is the whole integration surface

A third-party agent needs nothing but this package to produce a receipt anyone can
**check** (recompute the hash + read its provenance) and **beat** (score it against the
same rule the on-chain arena enforces). `examples/foreign-agent.ts` is exactly that — a
`funding-skew` agent that imports only `glassbox-agent-kit`:

```bash
npm run example:foreign   # fully offline; commit step gated on PRIVATE_KEY
```

```ts
import { parseProvenance, isFullyLive, scoreDecision, arenaScore, beats } from "glassbox-agent-kit";

// 1) CHECK: liveness is committed inside the receipt — a mock source can't hide.
parseProvenance(chain);   // [{source:"funding-oracle",mode:"live",ref:"block=19000123"}, {source:"dex-mid",mode:"mock"}]
isFullyLive(chain);       // false

// 2) BEAT: grade the agent and a human call under one rule (mirror of HumanArena.score()).
const agent    = scoreDecision(decision, realizedPnlBps);  // agent's score
const yourCall = arenaScore(-1, 9000, realizedPnlBps);     // your bearish call, 90% conviction
beats(yourCall, agent);   // did you beat the AI? — same math the contract runs
```

`arenaScore` is pinned byte-for-byte to `HumanArena.score()` by vectors shared with the
contract's test suite, including the negative-remainder case where a naive `Math.floor`
would diverge from Solidity's truncate-toward-zero.

## API

| Export | What it does |
|---|---|
| `canonicalReceipt(chain)` | The exact UTF-8 bytes the agent hashes (sorted-key, compact JSON). |
| `receiptHash(chain)` | `keccak256` of the canonical receipt — the on-chain commit value. |
| `hashCanonical(str)` | Hash already-serialized bytes (powers a live tamper box). |
| `GlassBoxAgent` | Abstract base — implement `reason()`, get a reproducible chain + receipt. |
| `foldEnsemble(decisions)` | Confidence-weighted consensus of several agents' calls. |
| `parseProvenance(chain)` | Read each `data_sources` entry as `{source, mode, ref}` (mode: live/mock/unavailable/internal/unknown). |
| `isFullyLive(chain)` | True only if every source is confirmably live — a receipt can't claim mock data was real. |
| `arenaScore(direction, weightBps, pnlBps)` | The shared win/lose rule, mirror of on-chain `HumanArena.score()`. |
| `scoreDecision(decision, pnlBps)` | Grade an agent `Decision` under that same rule. |
| `beats(human, agent)` | Strict head-to-head (a tie is not a win). |
| `commitReasoning(...)` | Seal a chain's hash on-chain (viem `WalletClient`). |
| `verifyReasoning(...)` | Re-hash a published chain against its commit (the tamper test). |
| `ERC8004_REGISTRIES` | Canonical ERC-8004 Identity/Reputation addresses on Mantle. |
| `mantle`, `mantleSepolia` | viem chain definitions. |

## Why reproducible receipts (the one design rule)

`decide(marketId, now)` takes the timestamp as an argument instead of reading the
clock, and every chain field is integer-or-string (no floats). That makes a receipt
**fully reproducible**: anyone, anytime, recomputes the identical hash. Reproducibility
is what turns "trust my reasoning" into "check my reasoning."

## License

[PolyForm Noncommercial 1.0.0](../LICENSE) — free for noncommercial use.
Commercial use requires a paid license: matrixbuilderops@proton.me
