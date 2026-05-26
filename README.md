# Glass-Box Alpha — AI Trading Agents on Mantle

**Mantle Turing Test 2026 entry.** 4 specialized AI trading agents on Mantle. Each runs a different reasoning frame, with full chain-of-thought visible. ERC-8004 reputation graded by actual on-chain PnL. Built as an open broadcast scoreboard for Mantle's AI Awakening livestream — any team's agent can plug in via the open integration schema.

## The 4 agents

| Agent | Reasoning frame | Data sources |
|---|---|---|
| **Chronos** | Timeline / historical analog mining — possibility trees through time | Nansen smart-money flows + on-chain TVL history |
| **Devil's Advocate** | Contradiction / counter-hypothesis — stress-tests peer assumptions | All other agents' reasoning + oracle risk feeds |
| **Web** | Cross-asset correlation — finds linked variables, compresses N inputs | Nansen smart-money flows for correlated assets |
| **Mood** | Sentiment as orthogonal-to-price signal | Elfa AI sentiment time-series |
| **Ensemble** | The Fold — sign-preserving geometric mean of expansion (Chronos) and collapse (DA + Web + Mood) | All 4 agent outputs |
| **On-chain attestation** | Reasoning-chain hash committed to Mantle (verifiable receipts) | `ReasoningHashAnchor` contract |

## Status
🚧 Day 3 of 20 (deadline 2026-06-15 10:59 UTC)

## What's in the box
- `contracts/` — Foundry workspace. `IGlassBoxAgent`, `ReasoningHashAnchor`, `GlassBoxRegistry`, `RoundState`. 13/13 tests passing.
- `agents/` — Python multi-agent backend. 4 specialists + Fold ensemble + orchestrator. DeepSeek (deepseek-reasoner) backend with native chain-of-thought streaming.
- `frontend/` — Next.js 14 + RainbowKit + Tailwind. Live reasoning-chain stream, leaderboard, PnL chart, wallet connect.
- `broadcast/` — OBS-streaming-ready scene layouts for the July 2-3 AI Awakening livestream.
- `kit/` — `glassbox-agent-kit` — reusable SDK extracted Day 15-16 (DevTools 2nd BUIDL).
- `docs/` — Integration schema spec + Mantle DevRel outreach drafts.

## Build plan
See `../GLASS-BOX-ARENA.md` for the 20-day burndown and prize-bucket strategy.

## Quickstart
```bash
cp .env.example .env       # fill in keys
cd contracts && forge install foundry-rs/forge-std && forge build && forge test
cd ../agents && pip install -r requirements.txt
cd ../frontend && pnpm install && pnpm dev
```

## Submissions (Day 20)
1. **BUIDL #1**: Glass-Box Alpha → Consumer & Viral DApps (primary) + AI Trading & Strategy (cross-tag via `tracksLimitForBuidl: 2`)
2. **BUIDL #2**: `glassbox-agent-kit` → AI DevTools (Tencent Cloud)

## Why this stands out
- **4 distinct reasoning frames**, not 4 copies of the same prompt. Multi-agent ensemble with named roles, not a single LLM dressed up.
- **Live chain-of-thought** visible per agent (deepseek-reasoner's `reasoning_content` channel maps directly to a visible thinking stream).
- **Reasoning chains hashed on Mantle** — every decision has a verifiable on-chain receipt. Anyone can audit.
- **ERC-8004 reputation graded by actual PnL** — not vibes. Used as the spec is designed.
- **Open Broadcast Kit** built for Mantle's AI Awakening livestream — any team's agent can plug in.
- **`glassbox-agent-kit` open-source SDK** lets any developer ship a transparent agent on Mantle in <30 min.

## Author
Alexander Sorrell · AI Systems Engineer · NVIDIA HGX/DGX background (A100/H100) · 20-class multi-agent orchestration framework managing 6,400+ concurrent states · 451 automated AI governance tests across Claude/Copilot/Gemini · Forta Network vulnerability detection
