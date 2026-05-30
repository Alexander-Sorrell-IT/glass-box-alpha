"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { AgentCard } from "@/components/AgentCard";
import { ReasoningStream, type ReasoningStep } from "@/components/ReasoningStream";
import { Leaderboard } from "@/components/Leaderboard";
import { LiveStatus } from "@/components/LiveStatus";
import { HumanCall } from "@/components/HumanCall";
import { VerifyPanel } from "@/components/VerifyPanel";
import { useIsLive, useRoundsCount, useRound } from "@/lib/useGlassBox";
import { ROUND_STATE_MAINNET, type AgentKey } from "@/lib/contracts";

// Demo fixtures — shown ONLY before contracts deploy (clearly labelled SIMULATED).
// Once live, every panel reads on-chain or shows an honest "awaiting" state, so the
// LIVE badge never sits over fabricated numbers.
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

const DEMO_AGENTS: { agentKey: AgentKey; signal: number; confidence: number; reasoningPreview: string }[] = [
  { agentKey: "chronos", signal: 0.62, confidence: 0.74, reasoningPreview: "30d smart-money net inflow positive; 5 of 7 top wallets accumulating. 24h analog suggests +3-5% within 48h." },
  { agentKey: "devils_advocate", signal: -0.15, confidence: 0.55, reasoningPreview: "Three of the 7 wallets share funding-graph proximity. Could be coordinated. Reducing conviction." },
  { agentKey: "web", signal: 0.48, confidence: 0.71, reasoningPreview: "When mETH inflows >$500k, USDC pool depth contracts within 4h in 73% of past 30d cases. Front-run probable." },
  { agentKey: "mood", signal: 0.38, confidence: 0.66, reasoningPreview: "Sentiment net +0.42 (24h avg), orthogonal component large vs price action. Decoupled = leading." },
];

const STATUS_LABEL = ["Open", "Pending", "Settled", "Cancelled"];

function fmtSignal(v: number): string {
  return v >= 0 ? `+${v.toFixed(2)}` : v.toFixed(2);
}

export default function Home() {
  const { isLive } = useIsLive();
  const { roundsCount } = useRoundsCount();
  const currentRoundId = roundsCount && roundsCount > 0 ? roundsCount - 1 : undefined;
  const { round } = useRound(currentRoundId);

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

      {/* The keynote: an AI that hands you a receipt, not a story — verify it yourself. */}
      <section className="mb-4">
        <p className="text-base text-signal-neutral mb-3">
          Every other AI asks you to <em>trust</em> its reasoning. This one hands you a{" "}
          <span className="text-accent font-semibold">receipt</span> — recompute the hash yourself.
        </p>
        <VerifyPanel />
      </section>

      {/* The thesis made real: a human can actually play against the agents. */}
      <section className="mb-8 max-w-2xl">
        <HumanCall />
      </section>

      <section className="mb-8">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-signal-neutral mb-3 flex items-center gap-2">
          Current Round — mETH/USDC
          {!isLive ? (
            <span className="badge bg-border text-signal-neutral text-[10px]">SIMULATED — illustrative</span>
          ) : (
            currentRoundId !== undefined && (
              <span className="badge bg-signal-bull/15 text-signal-bull text-[10px]">
                Round #{currentRoundId}{round ? ` · ${STATUS_LABEL[round.status] ?? "?"}` : ""}
              </span>
            )
          )}
        </h2>

        {!isLive ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {DEMO_AGENTS.map((a) => (
              <AgentCard key={a.agentKey} {...a} />
            ))}
          </div>
        ) : (
          <div className="panel p-6 text-sm text-signal-neutral">
            Live on Mantle. Per-agent signals + reasoning stream as each round opens and settles —
            on-chain submission reads wire in with the settler/indexer.
          </div>
        )}

        <div className="panel p-4 mt-4 flex items-center justify-between">
          <div>
            <span className="text-sm text-signal-neutral uppercase tracking-wider">Fold Ensemble</span>
            <div className="flex items-baseline gap-3 mt-1">
              {!isLive ? (
                <>
                  <span className="text-3xl font-mono text-signal-bull">+0.41</span>
                  <span className="text-sm text-signal-neutral">conf 66%</span>
                </>
              ) : round ? (
                <>
                  <span
                    className={`text-3xl font-mono ${round.ensembleSignal >= 0 ? "text-signal-bull" : "text-signal-bear"}`}
                  >
                    {fmtSignal(round.ensembleSignal)}
                  </span>
                  {round.status === 2 && (
                    <span className={`text-sm ${round.realizedPnlBps >= 0 ? "text-signal-bull" : "text-signal-bear"}`}>
                      PnL {round.realizedPnlBps >= 0 ? "+" : ""}{(round.realizedPnlBps / 100).toFixed(2)}%
                    </span>
                  )}
                </>
              ) : (
                <span className="text-3xl font-mono text-signal-neutral">—</span>
              )}
            </div>
          </div>
          {isLive && ROUND_STATE_MAINNET ? (
            <a
              className="button-primary"
              href={`https://mantlescan.xyz/address/${ROUND_STATE_MAINNET}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on Mantlescan →
            </a>
          ) : (
            <button
              className="button-primary opacity-50 cursor-not-allowed"
              disabled
              title="Available once contracts deploy to Mantle"
            >
              View on Mantlescan (post-deploy) →
            </button>
          )}
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Leaderboard rows={isLive ? [] : DEMO_LEADERBOARD} />
        </div>
        <div>
          <ReasoningStream steps={isLive ? [] : DEMO_STEPS} />
        </div>
      </section>

      <footer className="mt-12 pt-6 border-t border-border text-xs text-signal-neutral/60 text-center">
        <p>Built for Mantle Turing Test 2026 · github.com/Alexander-Sorrell-IT/glass-box-alpha</p>
      </footer>
    </main>
  );
}
