// A FOREIGN agent — built on nothing but `glassbox-agent-kit`. It demonstrates the
// inevitability half of the pitch: a third-party team needs only the published package
// to produce a receipt that anyone can CHECK (recompute + provenance) and BEAT (the same
// rule the on-chain arena enforces). The kit is a sufficient integration surface.
//
//   npm run example:foreign      # runs fully offline (no keys, no network)
//
// The only on-chain step is the commit, gated on PRIVATE_KEY. Everything else runs locally.
import {
  GlassBoxAgent,
  arenaScore,
  scoreDecision,
  beats,
  parseProvenance,
  isFullyLive,
  canonicalReceipt,
  hashCanonical,
  receiptHash,
  type RawReasoning,
} from "../src/index.js";

// A reasoning frame that is NOT one of Glass-Box's four (Chronos / Devil's Advocate /
// Web / Mood): perp funding-rate skew. Deterministic, so the receipt is reproducible.
// agentId 8242 sits well outside the built-in 1..4 ids (and the live anchor's (1,0) commit).
class FundingSkewAgent extends GlassBoxAgent {
  constructor(private fundingBps8h: number, private oracleBlock: number) {
    super(8242);
  }

  protected async reason(marketId: string): Promise<RawReasoning> {
    // Positive funding ⇒ longs pay shorts ⇒ crowded long ⇒ fade it (lean bear).
    const bearish = this.fundingBps8h > 0;
    return {
      model: "funding-skew-v1",
      // Provenance in the kit's tag convention: a live first-party oracle read + a mocked
      // dex mid. isFullyLive() will therefore report false — the receipt says so, honestly.
      data_sources: [`funding-oracle:live@block=${this.oracleBlock}`, "dex-mid:mock"],
      steps: [
        { step: 1, thought: `8h funding ${this.fundingBps8h >= 0 ? "+" : ""}${this.fundingBps8h}bps` },
        { step: 2, thought: bearish ? "longs crowded — fade, lean bear" : "shorts crowded — lean bull" },
      ],
      decision: {
        kind: bearish ? "PERP_SHORT" : "PERP_LONG",
        market_id: marketId,
        directional_signal: Math.max(-1, Math.min(1, -this.fundingBps8h / 50)),
        size_bps: 2200,
        confidence: Math.min(1, Math.abs(this.fundingBps8h) / 50),
      },
    };
  }
}

const NOW = 1_700_000_000; // fixed timestamp ⇒ fully reproducible receipt

const agent = new FundingSkewAgent(/* fundingBps8h */ 18, /* oracleBlock */ 19_000_123);
const { decision, chain, hash } = await agent.decide("mETH/USDC", NOW);

console.log("=== Foreign agent receipt (built with only glassbox-agent-kit) ===");
console.log(`agentId ${decision.agent_id}  ${decision.kind}  signal ${decision.directional_signal.toFixed(3)}`);
console.log(`receipt hash: ${hash}`);

// 1) PROVENANCE — anyone can read each input's source and whether it was live.
console.log("\n-- provenance (committed inside the receipt) --");
for (const p of parseProvenance(chain)) {
  console.log(`  ${p.source}: ${p.mode}${p.ref ? ` (${p.ref})` : ""}`);
}
console.log(`  fully live? ${isFullyLive(chain)}  — false, because dex-mid was mock; the receipt can't hide it`);

// 2) A STRANGER CHECKS — recompute locally, then tamper one token and watch it diverge.
console.log("\n-- tamper check (local recompute, no chain needed) --");
const pristine = canonicalReceipt(chain);
const tampered = pristine.replace("funding-skew-v1", "funding-skew-v2");
console.log(`  pristine recompute matches on-chain-ready hash? ${hashCanonical(pristine) === receiptHash(chain)}`);
console.log(`  after editing one byte:  ${hashCanonical(tampered) === receiptHash(chain) ? "MATCHES (bug!)" : "DOES NOT MATCH — tamper caught"}`);

// 3) A STRANGER BEATS IT — the exact rule HumanArena.score() enforces, computed off-chain.
console.log("\n-- head to head, same rule as HumanArena.score() --");
const realizedPnlBps = -120; // suppose the market fell 120bps after the call
const agentScore = scoreDecision(decision, realizedPnlBps);
const myScore = arenaScore(/* direction */ -1, /* convictionBps */ 9000, realizedPnlBps);
console.log(`  realized PnL: ${realizedPnlBps}bps`);
console.log(`  agent score: ${agentScore}   your score: ${myScore}`);
console.log(`  you beat the agent? ${beats(myScore, agentScore)}`);

// 4) COMMIT — the one on-chain step. Real if PRIVATE_KEY is set; otherwise print the exact
//    (agentId, decisionIndex, hash) a wallet would seal. No silent fakery.
console.log("\n-- commit (the only on-chain step) --");
if (process.env.PRIVATE_KEY) {
  const { createWalletClient, http } = await import("viem");
  const { privateKeyToAccount } = await import("viem/accounts");
  const { commitReasoning, mantleSepolia } = await import("../src/index.js");
  const walletClient = createWalletClient({
    account: privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`),
    chain: mantleSepolia,
    transport: http(),
  });
  const tx = await commitReasoning({ walletClient, chain });
  console.log(`  committed on-chain: ${tx}`);
} else {
  console.log(`  PRIVATE_KEY unset — would commit (agentId=${chain.agent_id}, decisionIndex=${chain.decision_index}, hash=${hash})`);
  console.log("  set PRIVATE_KEY to seal it on Mantle Sepolia.");
}
