# MASTER PLAN — Glass-Box Alpha + Broadcast Kit
### Mantle Turing Test 2026 — 18 days to submission, $48K realistic max

**Today**: Day 2 of 20 (2026-05-26). **Submission deadline**: 2026-06-15 10:59 UTC.

---

## OBJECTIVE

Capture as many of these 7 prize buckets as humanly possible with 2 BUIDLs:

| Bucket | Max $ | Realistic-max P(win) | EV |
|---|---|---|---|
| Consumer Track 1st (cross-tag #1) | $8,500 | 60% | $5,100 |
| AI Trading & Strategy 1st (cross-tag #2) | $8,500 | 25% | $2,125 |
| AI DevTools 1st (companion BUIDL) | $8,500 | 35% | $2,975 |
| Grand Champion (cross-track) | $9,000 | 50% | $4,500 |
| Best UI/UX | $3,000 | 55% | $1,650 |
| Community Voting × 2 (1st AND 2nd) | $17,000 | 50% combined | $5,950 |
| 20-Deploy Award × 2 BUIDLs | $2,000 | 95% combined | $1,900 |
| **TOTAL** | **$56,500** | — | **~$24,200 EV / $48K realistic ceiling** |

---

## THE TWO BUIDLs

**BUIDL #1 — Glass-Box Alpha** (primary build, 85% of effort)
- Cross-tagged: Consumer & Viral DApps + AI Trading & Strategy
- 4 LLM agents (Chronos, Devil's Advocate, Web, Mood) running distinct reasoning frames
- Live reasoning chains, ERC-8004 reputation, real on-chain trades on Mantle DEXes
- Fold ensemble computes final call from 4 agent outputs

**BUIDL #2 — `glassbox-agent-kit`** (extraction, 15% of effort, Days 15-16)
- Tagged: AI DevTools (Tencent Cloud)
- Open-source npm + pip SDK extracted from BUIDL #1
- Orchestrator + ERC-8004 hooks + reasoning-hash module
- Lets any team ship a transparent agent on Mantle in <30 min

---

## DAY-BY-DAY EXECUTION

### Days 1-2 (DONE — May 25-26)
- ✅ Project scaffolded, 4 contracts + 4 agents + orchestrator written
- ✅ 19/19 tests passing (13 Solidity + 6 Python)
- ✅ 7 commits pushed to github.com/Alexander-Sorrell-IT/glass-box-alpha

### Day 3 (May 28) — Frontend kickoff + designer hire
- [ ] Scaffold `frontend/` with Next.js 14 + RainbowKit + wagmi + Tailwind
- [ ] Wire Mantle Mainnet + Sepolia chains in wagmi config
- [ ] Build agent-card component (placeholder data)
- [ ] **Post designer brief** to Mantle Discord #builders + Read.cv + Dribbble ($600-800 flat fee, 2-day Figma sprint)
- [ ] Decision: which X handle for build-in-public — new @GlassBoxAlpha or your personal?

### Day 4 (May 29) — Agent NFTs + DevRel outreach + Day 1 of build-in-public
- [ ] **User action**: fund deployer wallet with ~0.05 MNT on Mantle Mainnet
- [ ] Mint 4 Agent Identity NFTs on Mantle Mainnet via ERC-8004 Identity Registry (`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`)
- [ ] Update CONTRACTS.md with token IDs
- [ ] **Send Mantle DevRel outreach** (draft in `docs/outreach/mantle-devrel-pitch.md`) — Discord + DM
- [ ] **First @GlassBoxAlpha tweet** linking the 4 mint tx hashes
- [ ] Set up API keys: Anthropic, Nansen, Elfa, WalletConnect

### Day 5 (May 30) — Backend integration + Reasoning-chain UI
- [ ] Run `agents/orchestrator/main.py` end-to-end with real Nansen + Elfa data (test 5 markets)
- [ ] Tune agent system prompts based on actual output quality
- [ ] Build live reasoning-chain stream component in frontend (Server-Sent Events or WebSocket)
- [ ] Day 2 of build-in-public on X — "Here's what Chronos's reasoning looks like" with screenshot

### Day 6 (May 31) — Leaderboard + Reputation Registry reads
- [ ] Frontend leaderboard component pulling ERC-8004 Reputation Registry data
- [ ] PnL chart component
- [ ] Wire wallet connect for human traders to register
- [ ] Day 3 of build-in-public

### Day 7 (Jun 1) — Sepolia deploy + testnet smoke test
- [ ] **Deploy all contracts to Mantle Sepolia** via Foundry: `forge script script/Deploy.s.sol --rpc-url mantle_sepolia --broadcast --verify`
- [ ] Verify all 4 contracts on sepolia.mantlescan.xyz
- [ ] Run full round end-to-end on testnet: agents reason → reasoning hashes commit → ensemble computes → mock settle
- [ ] Day 4 build-in-public: "Testnet live, here's a settled round"
- [ ] **AWS Prompt the Planet deadline check** — if Jun 1, that's today and either submit or skip; if Jun 10, fine

### Days 8-9 (Jun 2-3) — Mantle DEX execution contract + Forta-style vuln spike
- [ ] `AgentExecutor.sol` — routes Fold ensemble decision to a Merchant Moe V3 swap
- [ ] Test AgentExecutor on Sepolia with synthetic LP
- [ ] **Forta-style vuln research spike** (Day 9 dedicated 8h): pick a Mantle protocol (Agni / Fluxion / Init Capital), run 1,000-cycle stress-test methodology, document any finding
- [ ] Day 5-6 build-in-public

### Day 10 (Jun 4) — DEX wiring + frontend integration
- [ ] Orchestrator calls AgentExecutor with the Fold signal
- [ ] Frontend pulls live round data from RoundState contract
- [ ] Reveal animations when a settled trade lands
- [ ] If vuln finding from Day 9 is real, **disclose to protocol team privately** + tweet anonymized framing for credibility
- [ ] Day 7 build-in-public

### Day 11 (Jun 5) — Designer deliverable + UI polish round 1
- [ ] Designer hands off Figma file (paid Day 3-8)
- [ ] Implement hero screen + agent-card + reasoning-stream typography + reputation badges in Tailwind
- [ ] Mobile-responsive pass
- [ ] Day 8 build-in-public

### Days 12-13 (Jun 6-7) — Backtest harness + analysis
- [ ] Pull 90 days of historical Mantle DEX data (DeFiLlama + Merchant Moe subgraph)
- [ ] Replay the 4 agents over historical data → produce hypothetical Fold ensemble calls
- [ ] Compare Fold ensemble vs vanilla arithmetic mean baseline → Sharpe / hit-rate / drawdown deltas
- [ ] Write 2-page backtest report (markdown) — this is the supplementary evidence for Trading track
- [ ] Day 9-10 build-in-public — share backtest result as a quote-tweet hook

### Day 14 (Jun 8) — MAINNET DEPLOY (critical pin)
- [ ] **User action**: fund deployer wallet with ~0.05 MNT + $200 USDC for trading seed
- [ ] Deploy all contracts to Mantle Mainnet, verify on mantlescan.xyz
- [ ] Wire frontend to mainnet RPC
- [ ] Deploy frontend to Vercel
- [ ] **First real round on mainnet** — agents reason, commit reasoning hashes, AgentExecutor executes small swap
- [ ] Tweet thread with mainnet tx links — tag @Mantle_Official, @nansen_ai, @elfa_ai
- [ ] **DM Mantle DevRel follow-up #1** with mainnet proof of life
- [ ] Day 11 build-in-public

### Days 15-16 (Jun 9-10) — Kit extraction (BUIDL #2) + architecture spec
- [ ] Create new GitHub repo: `glassbox-agent-kit`
- [ ] Extract: orchestrator + base agent class + ERC-8004 hooks + reasoning-hash module
- [ ] Publish to npm (`@glassbox/agent-kit`) and pip (`glassbox-agent-kit`)
- [ ] Write SDK README with 5-min quickstart + 1 reference example agent
- [ ] **Write agent-architecture spec** (4-6 pages, full reasoning-frame + Fold ensemble math + reasoning-hash flow with worked examples) → publish in `docs/agent-architecture.md`
- [ ] Day 12-13 build-in-public — drop the kit publicly, ask devs to integrate

### Day 17 (Jun 11) — Reasoning Reputation Token + KOL outreach
- [ ] Deploy `ReasoningRepToken.sol` ERC-20 on Mantle Mainnet
- [ ] Each reasoning-hash commit mints a non-transferable reputation token to the producing agent
- [ ] Periodic combine function rolls low-rep tokens into higher tier (simple math)
- [ ] **Pay 1 Mantle-ecosystem KOL for retweet** ($300 cap)
- [ ] DM 5-10 crypto-AI researchers (Delphi, Messari, Allora community) with working demo + ask for honest feedback. One quote-RT = 10× profile alone.
- [ ] Day 14 build-in-public

### Day 18 (Jun 12) — Demo videos
- [ ] **Demo video #1 — Glass-Box Alpha** (≥2 min): live round → 4 agents reason → Fold ensemble → on-chain trade → leaderboard update
- [ ] **Demo video #2 — `glassbox-agent-kit`** (≥2 min): developer runs `npm install`, builds a custom agent in 5 min, integrates with broadcast leaderboard
- [ ] Both videos pre-record best-case scenarios (don't rely on live PnL during recording — Round 11 risk mitigation)
- [ ] Day 15 build-in-public — share video clips

### Day 19 (Jun 13) — Polish + READMEs + buffer day
- [ ] Final READMEs for both BUIDLs
- [ ] Architecture diagrams (one per BUIDL)
- [ ] 20-Deploy compliance check both BUIDLs against bar
- [ ] Buffer for anything that slipped
- [ ] Day 16 build-in-public

### Day 20 (Jun 14) — DoraHacks submissions
- [ ] **Submit BUIDL #1**: Glass-Box Alpha → cross-tag Consumer & Viral DApps (primary) + AI Trading & Strategy (secondary)
- [ ] **Submit BUIDL #2**: `glassbox-agent-kit` → AI DevTools
- [ ] Submission narratives finalized (drafts in `GLASS-BOX-ARENA.md`)
- [ ] Final launch thread on @GlassBoxAlpha — tag @Mantle_Official, @AnimocaMinds, @opencheck, @Bybit_Official, @TencentCloud_Intl
- [ ] Mantle Discord #builders launch post
- [ ] Day 17 build-in-public

### Day 21 (Jun 15, before 10:59 UTC) — Final push
- [ ] Verify both submissions are accepted on DoraHacks
- [ ] Final sponsor-tag tweets
- [ ] DONE

---

## BUDGET (cash outlay)

| Item | Cost | Day | Required? |
|---|---|---|---|
| Designer hire (Figma sprint) | $600-800 | Day 3-11 | Recommended (+$750-1,750 EV) |
| Nansen API premium tier | $200-300 | Day 14 | Recommended (prevents demo rate-limit fail) |
| 1 mid-tier Mantle-ecosystem KOL retweet | $300 cap | Day 17 | Recommended (+$500-1,500 EV) |
| Trading seed capital | $200 USDC | Day 14 | Required for credible demo |
| Mantle Mainnet gas | ~$0.10 | Day 4 + 14 + 17 | Required |
| **TOTAL** | **~$1,300-1,600** | | |

**ROI**: $1,300 spend → $4,000-10,000 EV lift = 3-7× return.

---

## DECISIONS BLOCKED ON USER

1. **X handle**: new @GlassBoxAlpha (recommended for clean build-in-public thread) OR your personal handle?
2. **Designer hire authorization** ($600-800)
3. **Trading seed capital amount** — $200 USDC minimum or higher?
4. **AWS Prompt the Planet** — verify deadline (Jun 1 vs Jun 10) by Day 3
5. **API keys to set in `.env`**: Anthropic, Nansen, Elfa, WalletConnect, Mantle Explorer
6. **Deployer wallet**: dedicated new MetaMask account for this project? (Recommended — don't use personal funds wallet)

---

## RISK REGISTER

| Risk | Severity | Mitigation |
|---|---|---|
| Fold ensemble dismissed as "labeled sqrt" by Allora | Medium | Ship 4-6 page agent-architecture spec showing the actual decision-process flow + a 90-day backtest comparing Fold vs vanilla mean baseline. Lead public-facing pitch with on-chain reasoning hashes, not ensemble math. |
| Live PnL underwater on demo day | High | Demo videos pre-recorded with best-case scenarios + supplementary backtest data |
| ClawHack veterans dominate Trading | High | Don't fight on PnL track record. Lead Consumer; Trading is bonus. |
| Designer ghosts | Medium | Fall back to Tailwind UI + shadcn templates by Day 8 if no contract locked by Day 4 EOD |
| Mantle DevRel non-response | Medium | Plan works as solo entry without DevRel. DevRel adoption is upside, not load-bearing. |
| Mantle DEX integration slips | Medium | Start with ONE DEX (Merchant Moe V3). Add others only if time permits. |
| Day 14 mainnet pin slips | Critical | This is the hard pin. Every day late compounds because real PnL needs ≥5 days of live data for demo to look credible. |
| AWS Prompt the Planet portfolio fork | Medium | Verify deadline Day 3. If Jun 1, decide to submit or skip immediately. |

---

## CRITICAL PATH (the items that gate submission)

1. **Day 4**: 4 Agent NFTs minted on Mantle Mainnet
2. **Day 7**: Full system runs end-to-end on Sepolia testnet
3. **Day 11**: Frontend with working wallet connect + leaderboard
4. **Day 14**: All contracts deployed on Mantle Mainnet + first real $200 trade settled
5. **Day 18**: Demo videos recorded
6. **Day 20**: Both BUIDLs submitted to DoraHacks

Miss Day 14 and the Trading-track narrative collapses. Everything else has slack.

---

## CUT ORDER IF TIME SLIPS

In order of what to drop first:
1. Multiple DEX integrations (keep Merchant Moe only)
2. Sound design + animations beyond basic
3. KOL paid retweet
4. Reasoning Reputation Token ERC-20 graft
5. Backtest harness (use forward-looking only)
6. `glassbox-agent-kit` extraction (revert to single-BUIDL Arena-only)
7. Devil's Advocate agent (cut to 3 agents)

**DO NOT cut**: Real mainnet deploy, reasoning-chain UI, ERC-8004 reputation writes, demo videos, both BUIDLs submitted. These are the prize-bucket levers.

---

## WHAT "DONE" LOOKS LIKE (Day 20)

- ✅ 2 BUIDLs submitted to DoraHacks
- ✅ Both have mainnet contracts verified on mantlescan.xyz
- ✅ Both have ≥2 min demo videos
- ✅ Both have public frontend URLs (Vercel)
- ✅ Both have open-source repos with full READMEs
- ✅ Both clear the 20-Deploy bar
- ✅ @GlassBoxAlpha has daily build-in-public posts since Day 4
- ✅ Mantle DevRel has been contacted at least 3 times
- ✅ Nansen + Elfa tagged + ideally retweeted at least once each
- ✅ At least 1 paid KOL retweet
- ✅ Forta-style public security finding posted (credibility move)
- ✅ Agent-architecture spec markdown live in repo
- ✅ Reasoning Reputation Token ERC-20 deployed
- ✅ Sound mental health, ready for QVAC hackathon Jun 19-21

---

**Last updated**: 2026-05-26 (Day 2)
**Next checkpoint**: End of Day 3 (May 28): frontend scaffold complete + designer brief posted + AWS deadline verified
