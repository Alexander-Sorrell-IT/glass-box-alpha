# Mantle DevRel Outreach

**Send-ready now — the pitch references LIVE on-chain artifacts: the `ReasoningHashAnchor` + in-browser tamper test on Mantle Sepolia (chain 5003). DO NOT reference mainnet mints, agent-identity NFTs, or live PnL→reputation settlement — none of those exist yet (see docs/claims-ledger.md).**

**Channels (in order):**
1. Mantle Discord — #builders channel (public-facing version)
2. Mantle DevRel team DMs on X — look for the active hackathon-program runner
3. Mantle DevHub Telegram if accessible

---

## Public Discord post (Day 2 — drop in #builders)

> Hey Mantle builders 👋
>
> Shipping Glass-Box Alpha for the Turing Test Hackathon — 4 AI trading agents, each running a different reasoning frame, with full chain-of-thought visible (DeepSeek's reasoner streams its thinking natively). The hook: each agent commits the keccak256 of its reasoning to Mantle **before** the outcome — recompute it in the browser, tamper one byte, watch it turn red. Live on Mantle Sepolia today. (ERC-8004 reputation graded by realized PnL is the design; settlement lands post-hackathon.)
>
> Agent frames:
> - Chronos → timeline / historical analog mining (possibility trees through time)
> - Devil's Advocate → contradiction / counter-hypothesis on peer agents
> - Web → cross-asset correlation (linked-variable compression)
> - Mood → sentiment as orthogonal-to-price signal
> - Ensemble → Fold — confidence-weighted consensus of all 4 frames (beats the avg single agent in backtest; no claim to beat a plain mean)
>
> Hot take: the AI Awakening livestream on July 2-3 deserves an open scoreboard that any competing agent can plug into. So I'm building one. OBS-streaming-ready, 16:9 layout, plug-and-play schema. If anyone wants to integrate their agent into the leaderboard, the spec drops in 48hrs.
>
> What's live on Mantle Sepolia (chain 5003) right now:
> - On-chain reasoning commit + in-browser tamper test — recompute the hash yourself
> - TS = Python = Solidity hash parity, proven on-chain
> - New: the receipt commits each input's *provenance* (live vs mock) — it can't claim mock data was real
> - Open SDK (glassbox-agent-kit): a foreign agent built on only the kit produces a receipt anyone can recompute **and** beat under the same on-chain rule
>
> Repo: github.com/Alexander-Sorrell-IT/glass-box-alpha
>
> CC @[DevRel handle] — would love to chat about whether this could be useful for the livestream production.

---

## DM to Mantle DevRel (Day 2 — personalized)

> Hey [name], building Glass-Box Alpha for the Turing Test hackathon — 4 AI agents, each a different reasoning frame, with visible chain-of-thought (DeepSeek's reasoner streams its thinking natively). The hook: each agent commits the keccak256 of its reasoning to Mantle **before** the outcome, so anyone recomputes it in the browser and a single tampered byte turns it red — live on Mantle Sepolia today. Ensemble decision via the Fold (confidence-weighted consensus). ERC-8004 reputation graded by realized PnL is designed; settlement lands post-hackathon.
>
> Concrete ask: I'm scoping a broadcast view explicitly designed for the July 2-3 AI Awakening livestream — OBS-streaming layout, plug-and-play integration schema any hackathon team's agent can implement to appear on the leaderboard alongside ours.
>
> Two questions:
>
> 1. Is the broadcast production already locked with Tencent Cloud, or is there room for an open community scoreboard layer? Happy to build to whatever spec the production team needs.
>
> 2. Could you intro me to whoever's running the livestream production? I want to scope this to what's actually useful.
>
> Either way, the standalone Alpha Arena product ships regardless — but if there's an opportunity to make it the open scoreboard the community sees during AI Awakening, that's where I want to aim.
>
> Background: AI Systems Engineer, NVIDIA HGX A100/H100 hardware background, built a 20-class multi-agent orchestration framework managing 6,400+ concurrent program states, 451-test AI governance methodology across Claude/Copilot/Gemini, identified vulnerabilities in Forta Network.
>
> Repo is live (github.com/Alexander-Sorrell-IT/glass-box-alpha); all 5 contracts deployed on Mantle Sepolia. Happy to share the integration spec now if useful.

---

## Follow-up cadence

- **Day 5:** If no response, follow up with a "shipped X" update in Discord
- **Day 10:** Post the integration schema publicly; ping again with "spec is live, here's how integration works"
- **Day 14:** Send mainnet broadcast view link; ask for production-side feedback
- **Day 18:** Final ask before submission — "is there an opportunity to put this in front of the broadcast team for July 2-3?"

---

## What NOT to do

- ❌ Cold-DM judges (Hashed, Caladan, Animoca Minds partners, Nansen leadership in judge capacity)
- ❌ Call yourself "the official scoreboard" without Mantle's explicit blessing
- ❌ Mass-tag judges in tweets
- ❌ Pitch Animoca Minds about Consumer track (judge-adjacent, looks like lobbying)
- ❌ Email pitch decks unsolicited to judging-panel members

---

## Success indicators

- Mantle DevRel responds with "interested, send the spec"
- Anyone from Mantle Foundation retweets the public Discord post
- Tencent Cloud rep shows up in the thread
- 2+ other hackathon teams ask about integrating
- Allora / Z.ai / Virtuals engineers ask about the agent architecture

Even 1 of these signals is meaningful. All 5 = Grand Champion becomes plausible.
