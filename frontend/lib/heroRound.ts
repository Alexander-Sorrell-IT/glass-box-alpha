import type { ReasoningChain } from "./receipt";
// AUTO-GENERATED from a REAL DeepSeek-reasoner round — do not hand-edit signals/hashes.
// Source: agents/orchestrator/main.py on market mETH/USDC, captured 2026-06-05.
// Every signal, confidence, and reasoningHash below is the actual model output + the
// keccak256 of its canonical reasoning receipt (byte-identical to the on-chain commit
// and the in-browser recompute). This is the "nothing is fake" spine of the demo.

export type HeroAgentKey = "chronos" | "web" | "mood" | "devils_advocate";

export interface HeroAgent {
  agentKey: HeroAgentKey;
  action: string;
  signal: number;       // -1..1
  confidence: number;   // 0..1
  sizeBps: number;      // 0..10000
  reasoningPreview: string;
  reasoningHash: `0x${string}`;
}

export interface HeroRound {
  marketId: string;
  capturedAt: string;
  ensemble: { signal: number; confidence: number };
  agents: HeroAgent[];
}

export const HERO_ROUND: HeroRound = {
  marketId: "mETH/USDC",
  capturedAt: "2026-06-05",
  ensemble: {
  "signal": -0.332,
  "confidence": 0.252
},
  agents: [
  {
    "agentKey": "chronos",
    "action": "PERP_SHORT",
    "signal": -0.5,
    "confidence": 0.6,
    "sizeBps": 2000,
    "reasoningPreview": "Net 24h flow is negative \u2014 lean bearish short-term. But 7d inflow suggests some accumulation, so this reads as consolidation more than a breakdown.",
    "reasoningHash": "0xfedc499efb7e22a4050c72b80e5cf84a04e64afab3bf8d605dacad3b5dedbd33"
  },
  {
    "agentKey": "web",
    "action": "PERP_SHORT",
    "signal": -0.5,
    "confidence": 0.45,
    "sizeBps": 1500,
    "reasoningPreview": "Related-asset flows: ETH +$1.48M, USDC +$406k, wstETH +$509k while mETH shows net \u2212$856k. mETH is being rotated into ETH/wstETH \u2014 sell pressure.",
    "reasoningHash": "0x4c22e2acc1fdd22ac8489438f362b504e643c845c00e46b6b6df7e34a3461fb0"
  },
  {
    "agentKey": "mood",
    "action": "HOLD",
    "signal": 0.0,
    "confidence": 0.05,
    "sizeBps": 0,
    "reasoningPreview": "24h volume is thin (~2,762), so sentiment is a small sample; the orthogonal component is weakly negative. Confidence stays low \u2014 not a high-signal read.",
    "reasoningHash": "0x9aed794fd7a211a0050f663d9c69fe42f3f47460ec8d1db9ebe3a0dd142271c5"
  },
  {
    "agentKey": "devils_advocate",
    "action": "PERP_LONG",
    "signal": 0.2,
    "confidence": 0.3,
    "sizeBps": 500,
    "reasoningPreview": "Counter-hypothesis: the outflow is a one-off whale adjustment, and the 7d inflow trend is still positive. The bearish analogs may be cherry-picked \u2014 I take the other side, lightly.",
    "reasoningHash": "0xdbcd8c6495aea954fe17fc9d2df4cca9029ec17ae625b01f93166f658f63e9be"
  }
],
};

export const HERO_AGENTS = HERO_ROUND.agents;
export const HERO_ENSEMBLE = HERO_ROUND.ensemble;

// Full Chronos reasoning chain from the SAME captured round, committed on-chain at
// ReasoningHashAnchor getCommit(agentId=1, decisionIndex=0) = keccak256 of this object
// (= 0xfedc499e...; tx 0xaa64a6c6). Powers the VerifyPanel tamper test on the REAL round.
export const HERO_CHRONOS_CHAIN: ReasoningChain = {
  "agent_id": 1,
  "decision_index": 0,
  "model": "deepseek-reasoner",
  "prompt_tokens": 2822,
  "completion_tokens": 2653,
  "steps": [
    {
      "step": 1,
      "thought": "We are given market data for mETH/USDC. We need to analyze using historical analog mining and timeline reasoning. We have net flows: -856k (24h), +1.19M (7d), -129k (30d). Top wallets: one positive net +350k (win rate 64%), one negative -394k (win rate 55%). Their histories show trades across MNT, USDY, fBTC, mETH, USDC, with various realized PnLs. Also TVL is $156M."
    },
    {
      "step": 2,
      "thought": "We need to identify 3-7 historical analogs from on-chain wallet flow + TVL/price history. But we are not given historical price data directly. We have only current snapshot. However, we can infer from wallet flows and TVL context. Since this is mETH/USDC, likely a liquid staking token pair. The net flows suggest recent selling pressure (24h negative) but 7d positive, indicating mixed signals. Top wallet 1 has high win rate and net positive, but his recent trades show switching between assets, including buying mETH with USDY and later selling mETH for fBTC. Wallet 2 has lower win rate but net negative, yet his last trade was buying mETH with fBTC (positive realized PnL)."
    },
    {
      "step": 3,
      "thought": "We need to construct analogs. Since we don't have historical prices, we must use wallet behavior patterns as proxies. Alternatively, we can think of historical patterns from similar DeFi pairs (like stETH/ETH or rETH/ETH) in terms of flow reversals, whale actions, and TVL changes. But the instruction says \"timeline / historical analog mining\" and \"on-chain wallet flow + TVL/price history\". We have to be creative."
    },
    {
      "step": 4,
      "thought": "Let's assume we have knowledge of past similar situations: \n- Analog 1: When a large net outflow in 24h but positive 7d, often indicates short-term selling by one whale but accumulation by others. Example: In stETH/ETH, after a whale sold heavily, price dipped then recovered within a week.\n- Analog 2: High win rate wallet buying mETH with USDY and later selling for fBTC suggests rotation into BTC, which might indicate bearishness on ETH relative to BTC. But wallet 2's last trade was fBTC to mETH (positive), so conflicting.\n- Analog 3: TVL is high ($156M) but flows not extremely large relative to TVL? 856k outflow vs 156M is ~0.55%, minor."
    },
    {
      "step": 5,
      "thought": "We'll list 5 analogs:"
    },
    {
      "step": 6,
      "thought": "1. Whale dumping followed by recovery (e.g., stETH/ETH April 2023)\n2. Whale accumulation from stablecoins (USDY) into mETH (wallet 1 did that) but then sold \u2013 pattern of a trader taking profits.\n3. Rotation between ETH and BTC (wallet 1 swapped mETH to fBTC, wallet 2 swapped fBTC to mETH) \u2013 divergence.\n4. Medium-term positive 7d flow but negative 30d \u2013 could be a short-term bounce in a downtrend.\n5. High win rate (64%) wallet net positive but also incurred losses; mixed."
    },
    {
      "step": 7,
      "thought": "For each, we branch trajectories:"
    },
    {
      "step": 8,
      "thought": "Analog 1 (Whale sell-off): \n- Next 24h: continued selling, price drops 2-3%\n- Next 7d: recovery, price back to even\n- Next 30d: moderate uptrend, +5%"
    },
    {
      "step": 9,
      "thought": "Analog 2 (Stablecoin rotation into mETH):\n- 24h: slight price increase as buying pressure\n- 7d: profit-taking leads to decline\n- 30d: mixed, possibly down"
    },
    {
      "step": 10,
      "thought": "Analog 3 (Rotation BTC/ETH):\n- 24h: neutral\n- 7d: if BTC outperforms, mETH might lag\n- 30d: possible underperformance"
    },
    {
      "step": 11,
      "thought": "Analog 4 (Short-term bounce in downtrend):\n- 24h: bounce continues, +1-2%\n- 7d: fades, back to downtrend\n- 30d: lower lows"
    },
    {
      "step": 12,
      "thought": "Analog 5 (Mixed signals from smart money):\n- 24h: sideways\n- 7d: slight upward drift\n- 30d: uncertain"
    },
    {
      "step": 13,
      "thought": "Convergence: Count branches ending with same directional signal. Need to decide direction. Let's assign signals: For each analog and time horizon, we can define if the net direction for mETH price is up, down, or neutral. Then see how many converge to up/down."
    },
    {
      "step": 14,
      "thought": "We should also consider the confidence formula: Confidence = convergent branches / total branches. But we need to pick a specific action. Likely a neutral or bearish stance given recent outflow and mixed signals."
    },
    {
      "step": 15,
      "thought": "From wallet histories: Wallet 1's recent trades: On June 5, he swapped USDY to fBTC with positive PnL (0.19). That's after earlier mETH trades. So he is moving to BTC. Wallet 2's last trade on June 3: fBTC to mETH with positive PnL (0.067). So they are on opposite sides."
    },
    {
      "step": 16,
      "thought": "Given net 24h flow negative, we might lean bearish short-term. But 7d positive suggests some accumulation. I'd say a period of consolidation."
    },
    {
      "step": 17,
      "thought": "We need to output a decision. Options: SPOT_SWAP, LP_DEPOSIT, LP_WITHDRAW, PERP_LONG, PERP_SHORT, HOLD, HEDGE. With signal (-1..1), size_bps, confidence."
    },
    {
      "step": 18,
      "thought": "Given the mixed signals, I think HOLD or HEDGE is appropriate. But the instruction says \"for HOLD/HEDGE use size_bps=0\". We can choose HOLD with confidence based on convergence."
    },
    {
      "step": 19,
      "thought": "Let me quantify analog branches more concretely."
    },
    {
      "step": 20,
      "thought": "I'll define 5 analogs:"
    },
    {
      "step": 21,
      "thought": "A1: Pattern of large 24h outflow after a week of inflow (like stETH/ETH Feb 2023). Outcome: 24h down, 7d recovery, 30d up.\nA2: Smart whale buying mETH from USDY (accumulation) then selling for BTC (profit). Outcome: 24h up, 7d down, 30d down.\nA3: Divergent whales: one going to BTC, one coming from BTC. Outcome: 24h neutral, 7d neutral, 30d slight down.\nA4: 7d positive but 30d negative: bounce in downtrend. Outcome: 24h up, 7d down, 30d down.\nA5: High win rate wallet net positive but inconsistent: Outcome: 24h neutral, 7d up, 30d mixed."
    },
    {
      "step": 22,
      "thought": "Now for each time horizon, we count convergences. For 24h: down: A1, neutral: A3, A5; up: A2, A4. That's 2 down, 2 up, 1 neutral? Actually A1 down, A2 up, A3 neutral, A4 up, A5 neutral => up: 2, down: 1, neutral: 2. So no strong convergence. For 7d: A1 up, A2 down, A3 neutral, A4 down, A5 up => up: 2 (A1, A5), down: 2 (A2, A4), neutral: 1 (A3). For 30d: A1 up, A2 down, A3 down, A4 down, A5 mixed -> down: 3 (A2, A3, A4), up: 1 (A1), mixed: 1. So 30d convergence to down: 3 out of 5 (60%). Highest convergence."
    },
    {
      "step": 23,
      "thought": "Therefore, over 30 days, bearish signal is more convergent. But short-term mixed."
    },
    {
      "step": 24,
      "thought": "Given the instruction \"for each market signal: identify N=3-7 historical analogs\", we have 5. Confidence = convergent/total = 3/5 = 0.6 for down. So we could take a bearish position. But we need to choose an action. PERP_SHORT would be appropriate, with signal magnitude maybe -0.5 to -0.6. size_bps: we need to determine position size; not specified, could use moderate size. Let's say size_bps=2000 (20% of capital). Confidence=0.6."
    },
    {
      "step": 25,
      "thought": "Alternatively, if we think short-term uncertain, we might HOLD. But the historical analog mining suggests a 30d bearish bias. So I'll go with PERP_SHORT."
    },
    {
      "step": 26,
      "thought": "But let's also consider that the top wallets have 64% and 55% win rates, not extremely high. And net flows 24h negative but 7d positive. Might be a tug-of-war. My 30d convergence is 3/5, which is not overwhelming. So confidence 0.6 is reasonable."
    },
    {
      "step": 27,
      "thought": "Signal should be negative for short, say -0.5 (since not super strong). Size: maybe 2000 bps (20%)."
    },
    {
      "step": 28,
      "thought": "Thus decision: PERP_SHORT signal=-0.5 size_bps=2000 confidence=0.6."
    },
    {
      "step": 29,
      "thought": "But wait, the instruction says \"for each market signal: identify N=3-7 historical analogs... Output one line at the end: DECISION: <action> signal=<-1..1> size_bps=<0..10000> confidence=<0..1>\". We must show work step-by-step."
    },
    {
      "step": 30,
      "thought": "Let me write the reasoning step by step."
    }
  ],
  "data_sources": [
    "market_id",
    "flows_24h_net_usd",
    "flows_7d_net_usd",
    "flows_30d_net_usd",
    "top_wallets",
    "top_wallet_histories",
    "mantle_tvl_context"
  ],
  "timestamp": 1780712749
};
