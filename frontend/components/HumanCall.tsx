"use client";

import { useState } from "react";
import {
  type Direction,
  type ArenaResult,
  resolveDemo,
  ogParams,
  tweetIntent,
  fmtBps,
  DEMO_ROUND,
} from "@/lib/arena";

/// The human side of "AI vs Human" — the thing that makes the hackathon's
/// namesake real. Pick a direction + conviction, get scored under the SAME rule
/// as the agents against the round's realized PnL, then share the result.
///
/// Demo mode runs the full predict → score → share loop with zero keys. When
/// contracts deploy, `submitCall` becomes the one on-chain write; the win/lose
/// read stays a gasless view.
export function HumanCall() {
  const [direction, setDirection] = useState<Direction>(1);
  const [convictionBps, setConvictionBps] = useState(6000);
  const [result, setResult] = useState<ArenaResult | null>(null);

  function lockIn() {
    // Demo: resolve instantly against the simulated round.
    // Live (future): writeContract HumanArena.submitCall, then read beatAgent
    // once the round settles. Same scoring rule either way.
    setResult(resolveDemo(direction, convictionBps));
  }

  function reset() {
    setResult(null);
  }

  return (
    <section className="panel p-5">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-accent">
          You vs the AI — make your call
        </h2>
        {/* The result always resolves against the demo round, so the disclosure is
            ALWAYS shown — never gated on isLive (which would hide it in production). */}
        <span className="badge bg-border text-signal-neutral text-[10px]">SIMULATED ROUND</span>
      </div>
      <p className="text-xs text-signal-neutral mb-3">
        Round #{DEMO_ROUND.roundId} · {DEMO_ROUND.market} · no capital needed — you predict, you&apos;re
        scored by the same rule the agents face. Simulated round (no settled on-chain round yet).
      </p>

      {!result && (
        <div className="rounded-lg border border-border bg-bg/40 p-3 mb-4 text-xs">
          <span className="text-signal-neutral">The AI is split — </span>
          <span className="text-signal-bull font-semibold">Chronos: 🟢 BULL</span>
          <span className="text-signal-neutral"> · </span>
          <span className="text-signal-bear font-semibold">Devil&apos;s Advocate: 🔴 BEAR</span>
          <span className="text-signal-neutral">. Chronos showed its work — </span>
          <span className="text-accent font-semibold">spot what it missed.</span>
        </div>
      )}

      {!result ? (
        <div className="space-y-4">
          {/* Direction toggle */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setDirection(1)}
              aria-label="Predict bullish"
              aria-pressed={direction === 1}
              className={`py-3 rounded-lg border font-semibold transition ${
                direction === 1
                  ? "bg-signal-bull/15 border-signal-bull text-signal-bull"
                  : "border-border text-signal-neutral hover:border-signal-bull/50"
              }`}
            >
              🟢 Bull
            </button>
            <button
              onClick={() => setDirection(-1)}
              aria-label="Predict bearish"
              aria-pressed={direction === -1}
              className={`py-3 rounded-lg border font-semibold transition ${
                direction === -1
                  ? "bg-signal-bear/15 border-signal-bear text-signal-bear"
                  : "border-border text-signal-neutral hover:border-signal-bear/50"
              }`}
            >
              🔴 Bear
            </button>
          </div>

          {/* Conviction slider */}
          <div>
            <div className="flex justify-between text-xs text-signal-neutral mb-1">
              <span>Conviction</span>
              <span className="font-mono">{(convictionBps / 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min={500}
              max={10000}
              step={500}
              value={convictionBps}
              onChange={(e) => setConvictionBps(Number(e.target.value))}
              aria-label="Conviction percent"
              aria-valuetext={`${(convictionBps / 100).toFixed(0)} percent`}
              className="w-full accent-accent"
            />
            <p className="text-[10px] text-signal-neutral/70 mt-1">
              Higher conviction amplifies your score — win bigger, lose bigger. Same skin-in-the-game
              weighting the agents face.
            </p>
          </div>

          <button onClick={lockIn} className="button-primary w-full py-3">
            Lock in call →
          </button>
        </div>
      ) : (
        <ResultView result={result} onReset={reset} />
      )}
    </section>
  );
}

function ResultView({ result, onReset }: { result: ArenaResult; onReset: () => void }) {
  const ogUrl = `/api/og?${ogParams(result).toString()}`;

  function share() {
    const origin = typeof window !== "undefined" ? window.location.origin : "";
    window.open(tweetIntent(result, origin), "_blank", "noopener,noreferrer");
  }

  return (
    <div className="space-y-4">
      <div
        className={`rounded-lg border p-4 text-center ${
          result.beat ? "bg-signal-bull/10 border-signal-bull" : "bg-signal-bear/10 border-signal-bear"
        }`}
      >
        <div className={`text-lg font-bold ${result.beat ? "text-signal-bull" : "text-signal-bear"}`}>
          <span aria-hidden="true">{result.beat ? "🏆 " : "🤖 "}</span>
          {result.beat ? `You beat ${result.agentName}!` : `${result.agentName} beat you`}
        </div>
        <div className="flex items-center justify-center gap-6 mt-3 font-mono">
          <div>
            <div className="text-[10px] uppercase text-signal-neutral">You</div>
            <div className={result.human >= 0 ? "text-signal-bull text-xl" : "text-signal-bear text-xl"}>
              {fmtBps(result.human)} bps
            </div>
          </div>
          <div className="text-signal-neutral">vs</div>
          <div>
            <div className="text-[10px] uppercase text-signal-neutral">{result.agentName}</div>
            <div className={result.agent >= 0 ? "text-signal-bull text-xl" : "text-signal-bear text-xl"}>
              {fmtBps(result.agent)} bps
            </div>
          </div>
        </div>
        <div className="text-[11px] text-signal-neutral mt-3">
          Market realized {fmtBps(result.realizedPnlBps)} bps · both scored by the same rule · simulated round
        </div>
      </div>

      {/* The actual share card — what unfurls on X */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={ogUrl}
        alt={`Round result: you ${fmtBps(result.human)} bps vs ${result.agentName} ${fmtBps(result.agent)} bps`}
        className="w-full rounded-lg border border-border"
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).style.display = "none";
        }}
      />

      <div className="grid grid-cols-2 gap-3">
        <button onClick={share} aria-label="Share result on X" className="button-primary py-3">
          Share on X <span aria-hidden="true">𝕏</span>
        </button>
        <button
          onClick={onReset}
          className="py-3 rounded-lg border border-border text-signal-neutral hover:border-accent/50"
        >
          Play again
        </button>
      </div>
    </div>
  );
}
