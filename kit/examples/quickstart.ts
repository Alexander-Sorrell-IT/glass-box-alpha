// Quickstart: build a transparent agent, produce an auditable reasoning chain, and
// hash it into an on-chain-ready receipt — in well under 30 minutes.
//
//   npm install && npm run example
//
// This runs fully offline (no keys, no network). The commented block at the bottom
// shows the two extra lines that seal the receipt on Mantle Sepolia for real.
import {
  GlassBoxAgent,
  foldEnsemble,
  receiptHash,
  type RawReasoning,
  type Decision,
} from "../src/index.js";

// 1) Define an agent by implementing reason(). Wire any LLM or deterministic logic.
//    Here: a tiny deterministic "smart-money flow" agent, so the demo is reproducible.
class FlowAgent extends GlassBoxAgent {
  constructor(
    agentId: number,
    private netFlowUsd: number,
  ) {
    super(agentId);
  }

  protected async reason(marketId: string): Promise<RawReasoning> {
    const bullish = this.netFlowUsd > 0;
    return {
      model: "deterministic-flow-v1",
      data_sources: ["nansen"],
      steps: [
        { step: 1, thought: `net smart-money flow ${this.netFlowUsd >= 0 ? "+" : ""}$${this.netFlowUsd}` },
        { step: 2, thought: bullish ? "inflows dominate — lean long" : "outflows dominate — lean short" },
      ],
      decision: {
        kind: bullish ? "PERP_LONG" : "PERP_SHORT",
        market_id: marketId,
        directional_signal: Math.max(-1, Math.min(1, this.netFlowUsd / 2_000_000)),
        size_bps: 1500,
        confidence: Math.min(1, Math.abs(this.netFlowUsd) / 2_000_000),
      },
    };
  }
}

const NOW = 1_700_000_000; // fixed timestamp → fully reproducible receipt

const agents = [
  new FlowAgent(1, 1_200_000),
  new FlowAgent(2, -300_000),
  new FlowAgent(3, 800_000),
];

const results = [];
for (const a of agents) {
  results.push(await a.decide("mETH/USDC", NOW));
}

for (const r of results) {
  console.log(`agent ${r.decision.agent_id}: ${r.decision.kind}  receipt ${r.hash}`);
}

const fold = foldEnsemble(results.map((r) => r.decision));
console.log("\nFold ensemble:", fold);

// The receipt hash for agent 1 is deterministic — recompute it anywhere and it matches:
console.log("\nagent 1 receipt recomputes to:", receiptHash(results[0].chain));

// ── Seal it on Mantle Sepolia (uncomment + set PRIVATE_KEY) ──────────────────────
// import { createWalletClient, http } from "viem";
// import { privateKeyToAccount } from "viem/accounts";
// import { commitReasoning, mantleSepolia } from "../src/index.js";
// const walletClient = createWalletClient({
//   account: privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`),
//   chain: mantleSepolia,
//   transport: http(),
// });
// const tx = await commitReasoning({ walletClient, chain: results[0].chain });
// console.log("committed on-chain:", tx);
