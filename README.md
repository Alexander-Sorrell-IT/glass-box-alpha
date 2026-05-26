# Glass-Box Alpha — The Official Broadcast Kit

**Mantle Turing Test 2026 entry.** 4 specialized LLM agents make real Mantle DeFi calls with full reasoning chains visible. ERC-8004 reputation graded by actual on-chain PnL. Built as an open broadcast scoreboard for Mantle's AI Awakening July 2-3 livestream — any team's agent can plug in.

## Status
🚧 Day 1 of 20 (deadline 2026-06-15 10:59 UTC)

## What's in the box
- `contracts/` — Foundry workspace. Round-state contract, reasoning-hash commit, ERC-8004 integrations (Mantle native addresses).
- `agents/` — Python multi-agent backend. 4 specialists (Chronos, Devil's Advocate, Web, Mood) + orchestrator. Reuses Type 1/KS60 stack from ECHO.
- `frontend/` — Next.js app. Live reasoning-chain stream, leaderboard, PnL chart, wallet connect (RainbowKit + wagmi).
- `broadcast/` — OBS-streaming-ready 16:9 scene layouts for Mantle's July 2-3 livestream.
- `kit/` — `glassbox-agent-kit` — extracted reusable SDK (orchestrator + ERC-8004 hooks + reasoning-hash module) for DevTools track.
- `docs/` — Integration schema spec (the plug-and-play standard other teams adopt) + Mantle DevRel outreach drafts.

## Build plan
See `../GLASS-BOX-ARENA.md` for the 20-day burndown and prize-bucket strategy.

## Quickstart (in progress)
```bash
cp .env.example .env  # fill in keys
cd contracts && forge install && forge build
cd ../agents && pip install -r requirements.txt
cd ../frontend && pnpm install && pnpm dev
```

## Submissions (Day 20)
1. **BUIDL #1**: Glass-Box Alpha Arena → Consumer & Viral DApps (primary) + AI Trading & Strategy (cross-tag via `tracksLimitForBuidl: 2`)
2. **BUIDL #2**: `glassbox-agent-kit` → AI DevTools (Tencent Cloud)

## Why this might break the contest
We built it so Mantle Foundation can adopt it as the official broadcast scoreboard for their July 2-3 AI Awakening livestream. Every agent in the hackathon can plug in via our open integration schema. If they adopt → contest-defining. If they don't → still a strong standalone Consumer + Trading entry.
