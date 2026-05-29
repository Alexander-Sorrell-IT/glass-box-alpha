"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { AgentCard } from "@/components/AgentCard";
import { ReasoningStream, type ReasoningStep } from "@/components/ReasoningStream";
import { Leaderboard } from "@/components/Leaderboard";
import { LiveStatus } from "@/components/LiveStatus";
import { HumanCall } from "@/components/HumanCall";

const DEMO_STEPS: ReasoningStep[] = [
  { agent: "chronos", step: 1, thought: "Pulling 30d Nansen smart-money flows on mETH/USDC…", ts: 0 },
  { agent: "chronos", step: 2, thought: "Net inflow +$1.2M from 7 wallets with 30d win-rate >0.65", ts: 0 },
  { agent: "web", step: 1, thought: "Linkage check: when mETH inflows >$500k, USDC pool depth contracts within 4h (73% historical)", ts: 0 },
  { agent: "mood", step: 1, thought: "Elfa sentiment 24h: +0.42 (avg), delta_24h +0.15. Orthogonal component large.", ts: 0 },
  { agent: "devils_advocate", step: 1, thought: "Counter-hypothesis: what if the 7 wallets are coordinated wash trade? Cross-check funding-graph proximity…", ts: 0 },
];

const DEMO_LEADERBOARD = [
  { rank: 1, name: "Chronos", isAgent: true, agentId: 1, trades: 14, winRatePct: 71.4, pnlPct: 8.32 },
  { rank: 2, name: "Web", isAgent: true, agentId: 3, trades: 12, winRatePct: 66.7, pnlPct: 5.18 },
  { rank: 3, name: "@cryptotrader42", isAgent: false, trades: 9, winRatePct: 55.6, pnlPct: 3.41 },
  { rank: 4, name: "Mood", isAgent: true, agentId: 4, trades: 11, winRatePct: 54.5, pnlPct: 1.92 },
  { rank: 5, name: "@onchaindegen", isAgent: false, trades: 8, winRatePct: 50.0, pnlPct: 0.67 },
  { rank: 6, name: "Devil's Advocate", isAgent: true, agentId: 2, trades: 14, winRatePct: 50.0, pnlPct: -0.43 },
];

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-8 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Glass-Box Alpha</h1>
          <p className="text-sm text-signal-neutral mt-1">
            AI trading agents on Mantle · reasoning attested on-chain
          </p>
          <div className="mt-2">
            <LiveStatus />
          </div>
        </div>
        <ConnectButton />
      </header>

      {/* The thesis made real: a human can actually play against the agents. */}
      <section className="mb-8 max-w-2xl">
        <HumanCall />
      </section>

      <section className="mb-8">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-signal-neutral mb-3 flex items-center gap-2">
          Current Round — mETH/USDC
          <span className="badge bg-border text-signal-neutral text-[10px]">SIMULATED — illustrative</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <AgentCard
            agentKey="chronos"
            signal={0.62}
            confidence={0.74}
            reasoningPreview="30d smart-money net inflow positive; 5 of 7 top wallets accumulating. 24h analog suggests +3-5% within 48h."
          />
          <AgentCard
            agentKey="devils_advocate"
            signal={-0.15}
            confidence={0.55}
            reasoningPreview="Three of the 7 wallets share funding-graph proximity. Could be coordinated. Reducing conviction."
          />
          <AgentCard
            agentKey="web"
            signal={0.48}
            confidence={0.71}
            reasoningPreview="When mETH inflows >$500k, USDC pool depth contracts within 4h in 73% of past 30d cases. Front-run probable."
          />
          <AgentCard
            agentKey="mood"
            signal={0.38}
            confidence={0.66}
            reasoningPreview="Sentiment net +0.42 (24h avg), orthogonal component large vs price action. Decoupled = leading."
          />
        </div>

        <div className="panel p-4 mt-4 flex items-center justify-between">
          <div>
            <span className="text-sm text-signal-neutral uppercase tracking-wider">
              Fold Ensemble
            </span>
            <div className="flex items-baseline gap-3 mt-1">
              <span className="text-3xl font-mono text-signal-bull">+0.41</span>
              <span className="text-sm text-signal-neutral">conf 66%</span>
            </div>
          </div>
          <button
            className="button-primary opacity-50 cursor-not-allowed"
            disabled
            title="Available once contracts deploy to Mantle"
          >
            View on Mantlescan (post-deploy) →
          </button>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Leaderboard rows={DEMO_LEADERBOARD} />
        </div>
        <div>
          <ReasoningStream steps={DEMO_STEPS} />
        </div>
      </section>

      <footer className="mt-12 pt-6 border-t border-border text-xs text-signal-neutral/60 text-center">
        <p>Built for Mantle Turing Test 2026 · github.com/Alexander-Sorrell-IT/glass-box-alpha</p>
      </footer>
    </main>
  );
}
