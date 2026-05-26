# Glass-Box Alpha — KS60 AI Trading Agents on Mantle

**Mantle Turing Test 2026 entry.** 4 specialized AI trading agents on Mantle, each reasoning through a named **KS60 mathematical operator** (Knuth-Sorrellian System — a 60-class original mathematical framework). Full reasoning chains visible. ERC-8004 reputation graded by actual on-chain PnL. Built as the open broadcast scoreboard for Mantle's AI Awakening July 2-3 livestream — any team's agent can plug in via the open integration schema.

## Why this isn't another GPT-wrapper

The 4 agents don't share a system prompt — they reason through **different KS60 operators**:

| Agent | KS60 Operator | What it does for the agent |
|---|---|---|
| **Chronos** | Up-Arrow Class 1 — iterated exponentiation | Explores possibility trees through historical time, expanding scenarios |
| **Devil's Advocate** | Down-Arrow Class 6 — Null Injection (∅→) | Structured emptiness — finds what data ISN'T present, contrarian frame |
| **Web** | Down-Arrow Class 5 — Entanglement (⊗) | Finds linked variables across markets, compresses N inputs → seed+coupling |
| **Mood** | Down-Arrow Class 7 — Perpendicular (⊥) | Sentiment as orthogonal dimension to price action |
| **Ensemble** | Sideways-Arrow — The Fold | Fundamental Equation `A → n = √((A ↑ n) · (A ↓ n))` selects the call |
| **On-chain attestation** | Down-Arrow Class 8 — Harvest (⟨⟩) | Every reasoning chain does WORK; work captured as hash on Mantle, banked, spent on future decisions |

KS60 is the user's original work — 60 classes across three interlocking 20-class hierarchies, novel operators with no precedent in standard notation. Already applied to Sovereign cryptocurrency (mining problems are KS60 recursion). Glass-Box Alpha extends it to AI trading decisions. No competitor can replicate the math — it's unfakeable IP.

## Status
🚧 Day 1 of 20 (deadline 2026-06-15 10:59 UTC)

## What's in the box
- `contracts/` — Foundry workspace. ReasoningHashAnchor (the Harvest operator on-chain), GlassBoxRegistry (where any team's agent registers), IGlassBoxAgent interface.
- `agents/` — Python multi-agent backend. 4 KS60-specialized agents + Fold ensemble + orchestrator. Reuses Type 1 / 20-class hierarchical orchestration framework.
- `frontend/` — Next.js app. Live reasoning-chain stream (KS60 operators visible per step), leaderboard, PnL chart, wallet connect.
- `broadcast/` — OBS-streaming-ready 16:9 scene layouts for Mantle's July 2-3 AI Awakening livestream.
- `kit/` — `glassbox-agent-kit` — extracted reusable SDK for DevTools track. Lets any team plug their ERC-8004 agent into the leaderboard.
- `docs/` — Integration schema spec + Mantle DevRel outreach drafts.

## Build plan
See `../GLASS-BOX-ARENA.md` for the 20-day burndown, prize-bucket strategy, KS60 integration plan.

## Quickstart (in progress)
```bash
cp .env.example .env  # fill in keys
cd contracts && forge install && forge build
cd ../agents && pip install -r requirements.txt
cd ../frontend && pnpm install && pnpm dev
```

## Submissions (Day 20)
1. **BUIDL #1 — Glass-Box Alpha**: cross-tagged Consumer & Viral DApps + AI Trading & Strategy (via `tracksLimitForBuidl: 2`)
2. **BUIDL #2 — `glassbox-agent-kit`**: AI DevTools track (Tencent Cloud)

## Why this might break the contest
- **KS60 paradigm** — no other team has this; Grand Champion judges (Z.ai, Allora, Virtuals, Animoca, Hashed, UHK academic) will see a genuine paradigm shift, not another LLM-wrapper. Innovation score should be top of field.
- **Open broadcast kit** — built so Mantle Foundation can adopt it as the official scoreboard for July 2-3 AI Awakening livestream. If adopted, contest-defining. If not, still strong standalone Consumer + Trading entry.
- **Verifiable on Mantle** — every agent decision's reasoning chain hashed on-chain via the Harvest operator. Anyone can audit. ERC-8004 reputation graded by actual on-chain PnL.
- **Real existing IP** — KS60 applied to crypto already (Sovereign cryptocurrency mining). This is extension of proven work, not invented for the hackathon.

## Author
Alexander Sorrell · AI Systems Engineer · NVIDIA HGX/DGX background (A100/H100) · 20-class multi-agent orchestration framework managing 6,400+ states · 451 automated AI governance tests across Claude/Copilot/Gemini · Forta Network vulnerability detection · KS60 creator
