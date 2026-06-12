# HackQuest Builder Interview — cue sheet (Corinne, ~1–1.5 min)

> Every line ledger-traced (docs/claims-ledger.md). Glance-able off-camera.
> WHAT THIS IS: content marketing for the hackathon — HackQuest/Mantle publish
> builder-spotlight clips to their channels (their words: "share authentic builder
> stories with the broader ecosystem"). It is exposure + voting fuel + a reusable
> asset for grants. It is NOT judging — but judges see these channels.

## Their five topics → your answers

**1. Project and team.**
Solo build — Alexander Sorrell, AI systems engineer, NVIDIA HGX/H100 background.
Glass-Box Alpha: four AI trading agents on Mantle, each a different reasoning
frame — a historian, a devil's advocate, a correlation hunter, a sentiment reader
— combined by a confidence-weighted ensemble called the Fold.

**2. The problem.**
Every AI can explain its trades. None can PROVE it didn't rewrite the explanation
after seeing the outcome. Explainable AI asks for trust; verifiable AI lets you
check. Glass-Box commits the keccak256 of the full reasoning chain to Mantle
BEFORE the outcome — anyone can recompute the hash in their browser, tamper one
byte, and watch it turn red.

**3. How AI fits.**
The agents reason with a chain-of-thought LLM, but the product isn't the
intelligence — it's the RECEIPT. Each receipt even commits whether every data
input was live or mock (nansen:live vs nansen:mock) inside the hash, so a receipt
can't claim fake data was real. Verified live with Nansen's production API.

**4. Why Mantle.**
The contest thesis IS our thesis: every key decision and outcome recorded
on-chain. Five contracts live on Mantle Sepolia, source-verified on the explorer;
the same reasoning hash computed in TypeScript, Python, and Solidity — proven by
a live verify() call to the deployed contract. Plus ERC-8004 agent identity and
the Mantle DeFi data the agents actually read.

**5. Future of AI on-chain.**
Agents are about to move real money, and trust is the bottleneck. The future is
receipts, not stories: every agent decision sealed before the outcome, checkable
by anyone. We shipped the standard as an open SDK — glassbox-agent-kit — so any
team's agent can produce the same checkable receipts. The goal: "verifiable"
becomes table stakes for on-chain AI.

## The 30-second demo offer (strongest move)
Offer to screen-share the tamper test: open glass-box-alpha.vercel.app, flip one
byte, hash turns red against the live on-chain commit. If they take it, that clip
sells the whole project.

## Questions to ASK them (2–3, shows professionalism)
1. Format: recorded or live? Final length, and where will it be published?
2. Would a 30-second live demo (screen share) be useful, or talking-head only?
3. Do you need assets — logo, headshot, project one-liner — for the graphics?
4. (Optional) Timing: will it publish before or after winners are announced?

## Never say (ledger banned, even under friendly questions)
beats the market · generates alpha · live on mainnet · NFTs minted · settlement
is live · more than 2 on-chain commits · a third-party team already adopted the
SDK · published to npm. If asked about results: "the honest backtest shows
variance reduction — we explicitly refuse the alpha claim; the headline is the
verifiable audit trail."

## Logistics
Timezone: US Central (UTC-5). Availability given: 10am–10pm CT, plus early
mornings for overlap. Browser Google Meet / Zoom only — no installs, no wallet,
ever. Links: dorahacks.io/buidl/44738 · dorahacks.io/buidl/44817 ·
youtu.be/_dSQyfMcX6U · glass-box-alpha.vercel.app
