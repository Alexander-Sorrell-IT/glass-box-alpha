// Human-side arena helpers. The scoring rule here MIRRORS HumanArena.sol's
// `score()` exactly — it is the single conceptual source of truth for "did the
// human beat the agent?", applied identically to humans and agents both here
// (instant demo/preview) and on-chain (verifiable). Keep the two in lockstep.

export type Direction = 1 | -1;

const BPS = 10_000;

/// score = sign(direction) · realizedPnlBps · weightBps / 10000
/// Integer math, truncated toward zero — matches Solidity int256 division.
export function score(direction: number, weightBps: number, realizedPnlBps: number): number {
  if (direction === 0 || weightBps === 0) return 0;
  const dir = direction > 0 ? 1 : -1;
  return Math.trunc((dir * realizedPnlBps * weightBps) / BPS);
}

export function fmtBps(v: number): string {
  return v >= 0 ? `+${v}` : `${v}`;
}

// The demo round — lets the predict → score → share loop run with ZERO keys,
// before any contract is deployed. Clearly labeled SIMULATED in the UI.
export const DEMO_ROUND = {
  roundId: 17,
  market: "mETH/USDC",
  // Card signals (normalized -1..1) for the OG image.
  signals: { signal: 0.41, confidence: 66, chronos: 0.62, da: -0.15, web: 0.48, mood: 0.38 },
  // Chronos's on-chain-style submission, scored under the same rule.
  chronos: { name: "Chronos", direction: 1 as Direction, convictionBps: 2500 },
  // The honest twist: the AI consensus was BULLISH (Fold +0.41, Chronos +0.62) but
  // Devil's Advocate dissented (-0.15) — and the market DROPPED 120bps. So a human who
  // sided with the skeptic out-reasons the AI. (Not rigged: going bull here LOSES,
  // exactly as it should.) Scoring stays in lockstep with HumanArena.sol.
  realizedPnlBps: -120,
};

export interface ArenaResult {
  direction: Direction;
  convictionBps: number;
  realizedPnlBps: number;
  human: number;
  agent: number;
  agentName: string;
  beat: boolean;
}

/// Resolve a human call against the demo round under the shared rule.
export function resolveDemo(direction: Direction, convictionBps: number): ArenaResult {
  const human = score(direction, convictionBps, DEMO_ROUND.realizedPnlBps);
  const agent = score(DEMO_ROUND.chronos.direction, DEMO_ROUND.chronos.convictionBps, DEMO_ROUND.realizedPnlBps);
  return {
    direction,
    convictionBps,
    realizedPnlBps: DEMO_ROUND.realizedPnlBps,
    human,
    agent,
    agentName: DEMO_ROUND.chronos.name,
    beat: human > agent,
  };
}

/// Build the /api/og query for a human-result share card.
export function ogParams(r: ArenaResult): URLSearchParams {
  const s = DEMO_ROUND.signals;
  return new URLSearchParams({
    market: DEMO_ROUND.market,
    round: String(DEMO_ROUND.roundId),
    signal: String(s.signal),
    confidence: String(s.confidence),
    pnl: (DEMO_ROUND.realizedPnlBps / 100).toFixed(2),
    chronos: String(s.chronos),
    da: String(s.da),
    web: String(s.web),
    mood: String(s.mood),
    human: String(r.human),
    agent: String(r.agent),
    vs: r.agentName,
    beat: r.beat ? "1" : "0",
    dir: r.direction > 0 ? "bull" : "bear",
  });
}

/// The tweet text — the viral payload.
export function tweetText(r: ArenaResult): string {
  const dir = r.direction > 0 ? "🟢 bull" : "🔴 bear";
  if (r.beat) {
    return `I went ${dir} on ${DEMO_ROUND.market} and BEAT ${r.agentName} on @GlassBoxAlpha 🧠⚔️🤖\n` +
      `Me ${fmtBps(r.human)}bps vs ${r.agentName} ${fmtBps(r.agent)}bps — every call graded on-chain by real PnL.\n` +
      `Think you can out-reason the AI? #MantleAIHackathon`;
  }
  return `I went ${dir} on ${DEMO_ROUND.market} and ${r.agentName} beat me on @GlassBoxAlpha 🤖⚔️🧠\n` +
    `${r.agentName} ${fmtBps(r.agent)}bps vs me ${fmtBps(r.human)}bps. Rematch incoming.\n` +
    `Can you out-reason the AI? #MantleAIHackathon`;
}

/// Twitter intent URL: text + a link to /share (which carries OG meta so the
/// card unfurls). `origin` comes from the browser at click time.
export function tweetIntent(r: ArenaResult, origin: string): string {
  const url = `${origin}/share?${ogParams(r).toString()}`;
  const intent = new URLSearchParams({ text: tweetText(r), url });
  return `https://twitter.com/intent/tweet?${intent.toString()}`;
}
