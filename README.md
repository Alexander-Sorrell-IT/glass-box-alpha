# Glass-Box Alpha — the AI that hands you a receipt, not a story

**Mantle Turing Test 2026 entry.** Every other AI asks you to *trust* its reasoning. Glass-Box Alpha hands you a **receipt**: an agent commits its reasoning's keccak256 to Mantle *before* the market moves, and anyone — a judge or a stranger — can recompute that hash in the browser, **tamper one byte and watch it turn red**, then beat the AI under the exact same on-chain scoring rule. (Live on Sepolia today: Chronos's on-chain commit + tamper-test; the full four-agent anchor lands with the mainnet deploy.) Explainable AI asks you to trust; **verifiable AI lets you check.**

Four agents each run a distinct reasoning frame (Chronos / Devil's Advocate / Web / Mood); the Fold combines them; an AI-vs-Human arena scores any human's call by the same on-chain rule; ERC-8004 reputation is graded by realized on-chain PnL (settlement lands with the mainnet deploy). Open broadcast schema — any team's agent can plug in.

## The 4 agents

| Agent | Reasoning frame | Data sources |
|---|---|---|
| **Chronos** | Timeline / historical analog mining — possibility trees through time | Nansen smart-money flows + DeFiLlama TVL + first-party Mantle RPC swap logs |
| **Devil's Advocate** | Contradiction / counter-hypothesis — stress-tests peer assumptions | All other agents' reasoning (`peers:internal`) |
| **Web** | Cross-asset correlation — finds linked variables, compresses N inputs | Nansen smart-money flows for correlated assets |
| **Mood** | Sentiment as orthogonal-to-price signal | Elfa AI sentiment time-series |
| **Ensemble** | The Fold — confidence-weighted consensus of all 4 frames (beats the avg single agent's Sharpe in 200/200 backtest seeds; makes no claim to beat a plain mean) | All 4 agent outputs |
| **On-chain attestation** | Reasoning-chain hash committed to Mantle (verifiable receipts) | `ReasoningHashAnchor` contract |

## Status
🟢 **Live on Mantle Sepolia** (chain 5003) — all 5 Glass-Box contracts deployed and wired into the frontend (addresses in `frontend/lib/contracts.ts`). The keynote tamper-test reads the real on-chain reasoning commit. Mainnet settlement deploy is post-hackathon. Data layer is real-API-ready (DeepSeek is the intended LLM backend, key-gated; Nansen/Elfa wired with deterministic mock fallback when a key/endpoint is unavailable) — and every receipt commits each input's **liveness provenance** (`nansen:live` / `nansen:mock` / `mantle-rpc:live@block=N` / `defillama:unavailable`) inside the hashed `data_sources`, so a receipt can't claim mock data was live.

## What's in the box
- `contracts/` — Foundry workspace. `IGlassBoxAgent`, `ReasoningHashAnchor`, `GlassBoxRegistry`, `RoundState`, `AgentExecutor`, `MerchantMoeAdapter`, `ReasoningRepToken`, `HumanArena` (the AI-vs-human play layer). 59/59 Solidity tests passing (`forge test`).
- `agents/` — Python multi-agent backend. 4 specialists + Fold ensemble (confidence-weighted consensus) + orchestrator + backtest harness. DeepSeek reasoner backend with native chain-of-thought streaming (key-gated). Live-runner composition root (`python -m agents.settler.live`) wires the round flow to a real chain behind a single `--live` flag — see `docs/mainnet-runbook.md` (full mainnet deploy ≈ $0.07 gas, estimated from Sepolia receipts + live mainnet reads). 76/76 Python tests passing (`PYTHONPATH=. pytest agents` from repo root; build contracts first — the ABI test reads `contracts/out/`).
- `frontend/` — Next.js 14 + RainbowKit + Tailwind. Live reasoning-chain stream, leaderboard, PnL chart, wallet connect.
- `broadcast/` — OBS-streaming-ready scene layouts for the July 2-3 AI Awakening livestream.
- `kit/` — `glassbox-agent-kit` — reusable TypeScript SDK (2nd BUIDL): the reasoning-receipt primitive, a transparent `GlassBoxAgent` base + Fold, on-chain commit/verify helpers, and ERC-8004 shapes. Byte-parity with the Python agent / Solidity contract / browser is pinned by a golden-vector test (`cd kit && npm test`).
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
1. **BUIDL #1**: Glass-Box Alpha → Alpha & Data (Mirana Ventures, primary) + AI Trading & Strategy (cross-tag via `tracksLimitForBuidl: 2`)
2. **BUIDL #2**: `glassbox-agent-kit` → AI DevTools (Tencent Cloud)

## Why this stands out
- **AI vs Human, for real** — `HumanArena` lets anyone submit a directional call (no capital) and be graded by the *same* on-chain rule as the agents. The "AI vs Human" premise is a mechanic, not a label.
- **4 distinct reasoning frames**, not 4 copies of the same prompt. Multi-agent ensemble with named roles, not a single LLM dressed up.
- **Live chain-of-thought** visible per agent (the DeepSeek reasoner's `reasoning_content` channel maps directly to a visible thinking stream).
- **Provenance-committed receipts** — each input's liveness (live / mock / unavailable) is stamped at origin inside the hashed receipt; flipping a tag turns the on-chain hash red. Includes a first-party `mantle-rpc` source that reads swap logs off our own Mantle RPC — no third party in the path — and honestly declares `unavailable` rather than silently mocking.
- **Reasoning chains hashed on Mantle** — live on Sepolia today: every decision carries a verifiable on-chain receipt anyone can recompute and audit (`ReasoningHashAnchor` at `0xB031…353d`).
- **ERC-8004 reputation graded by realized on-chain PnL** — the design; the PnL→reputation settlement goes live with the Day-14 mainnet deploy.
- **`glassbox-agent-kit` open-source SDK** (2nd BUIDL) lets any developer ship a transparent agent on Mantle.

## Author
Alexander Sorrell · AI Systems Engineer · NVIDIA HGX/DGX background (A100/H100) · 20-class multi-agent orchestration framework managing 6,400+ concurrent states · 451 automated AI governance tests across Claude/Copilot/Gemini · Forta Network vulnerability detection
