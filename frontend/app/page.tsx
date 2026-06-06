"use client";

import { useState } from "react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Ring } from "@/components/Ring";
import { AgentCard } from "@/components/AgentCard";
import { ReasoningStream, type ReasoningStep } from "@/components/ReasoningStream";
import { Leaderboard } from "@/components/Leaderboard";
import { LiveStatus } from "@/components/LiveStatus";
import { HumanCall } from "@/components/HumanCall";
import { VerifyPanel } from "@/components/VerifyPanel";
import { useIsLive } from "@/lib/useGlassBox";
import { ROUND_STATE_MAINNET } from "@/lib/contracts";
import { HERO_AGENTS, type HeroAgentKey } from "@/lib/heroRound";

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

export default function Home() {
  const { isLive } = useIsLive();
  const [selectedAgent, setSelectedAgent] = useState<HeroAgentKey | null>(null);
  const selected = selectedAgent ? HERO_AGENTS.find((a) => a.agentKey === selectedAgent) : undefined;
  const mantlescanLive = ROUND_STATE_MAINNET.length === 42;

  return (
    <main className="min-h-screen px-6 py-8 max-w-7xl mx-auto">
      <header className="flex flex-wrap items-center justify-between gap-4 mb-8">
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

      {/* HERO — a REAL captured DeepSeek round, fully offline & deterministic.
          Four reasoning frames fold into one call; the lone dissent loses on
          conviction WEIGHT, not a vote count. This is NOT simulated. */}
      <section className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-signal-neutral flex flex-wrap items-center gap-2">
            mETH/USDC — the Fold
            <span className="badge bg-accent/15 text-accent text-[10px]">
              CAPTURED 2026-06-05 · real model output
            </span>
          </h2>
          {mantlescanLive && (
            <a
              className="text-xs text-accent underline"
              href={`https://sepolia.mantlescan.xyz/address/${ROUND_STATE_MAINNET}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on Mantlescan →
            </a>
          )}
        </div>
        <p className="text-base text-signal-neutral mb-3">
          Four reasoning frames. One Fold call. One dissent.
        </p>

        <div className="panel p-4 sm:p-6">
          <Ring onSelectAgent={setSelectedAgent} selectedAgent={selectedAgent} />
        </div>

        {/* Drill-down: click a ribbon → that agent's reasoning, with a hash to verify. */}
        {selected && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 items-start animate-reasoning-fade">
            <AgentCard
              agentKey={selected.agentKey}
              signal={selected.signal}
              confidence={selected.confidence}
              reasoningPreview={selected.reasoningPreview}
            />
            <div className="panel p-4 space-y-2">
              <div className="text-[10px] uppercase tracking-wider text-signal-neutral/60">
                Reasoning hash (keccak256, committed on-chain)
              </div>
              <div className="font-mono text-[11px] text-signal-neutral break-all">
                {selected.reasoningHash}
              </div>
              {selected.agentKey === "chronos" ? (
                <a
                  href="#verify"
                  className="inline-block text-xs text-accent underline mt-1"
                  onClick={(e) => {
                    e.preventDefault();
                    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
                    document.getElementById("verify")?.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
                  }}
                >
                  Verify this — recompute the hash yourself ↓
                </a>
              ) : (
                <p className="text-[11px] text-signal-neutral/70 mt-1">
                  The live tamper-test below verifies Chronos&apos;s on-chain commit; this is this
                  agent&apos;s reasoning hash from the same round.
                </p>
              )}
            </div>
          </div>
        )}
      </section>

      {/* The keynote: an AI that hands you a receipt, not a story — verify it yourself. */}
      <section id="verify" className="mb-8 scroll-mt-6">
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

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Leaderboard rows={isLive ? [] : DEMO_LEADERBOARD} />
        </div>
        <div>
          <ReasoningStream steps={isLive ? [] : DEMO_STEPS} />
        </div>
      </section>

      <footer className="mt-12 pt-6 border-t border-border text-xs text-signal-neutral text-center">
        <p>Built for Mantle Turing Test 2026 · github.com/Alexander-Sorrell-IT/glass-box-alpha</p>
      </footer>
    </main>
  );
}
