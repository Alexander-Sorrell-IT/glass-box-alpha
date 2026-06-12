# Interview Q&A — study + edit draft
**How to use:** read MY DRAFT out loud, then rewrite it your way under YOUR VERSION.
Keep each answer 20–30 seconds spoken (~60–80 words). Hand the file back and we
drill on YOUR versions until they're reflex. Every draft line is ledger-safe —
if your edits add claims, we re-check them against docs/claims-ledger.md.

---

## Q1. "Tell us about your project and the team behind it."

**MY DRAFT:**
I'm Alexander Sorrell, AI systems engineer — NVIDIA data-center background.
I built Glass-Box Alpha solo: four AI trading agents on Mantle, each with a
different reasoning style — a historian, a devil's advocate, a correlation
hunter, and a sentiment reader — combined into one decision by a
confidence-weighted ensemble I call the Fold.

**YOUR VERSION:**
(write yours here)

---

## Q2. "What problem are you solving?"

**MY DRAFT:**
Every AI can explain its trades. None of them can prove they didn't rewrite
the explanation after seeing the outcome. So I made the reasoning commit
itself to Mantle before the outcome — anyone can recompute the hash in their
browser, change one character, and watch it turn red. Explainable AI asks you
to trust it. Verifiable AI lets you check.

**YOUR VERSION:**
(write yours here)

---

## Q3. "How does AI fit into your product vision?"

**MY DRAFT:**
The agents think with a chain-of-thought model, but the product isn't the
intelligence — it's the receipt. The receipt even seals in whether every data
input was live or simulated, so an agent can't claim fake data was real. We
verified that with Nansen's production API — their live data, stamped inside
the hash.

**YOUR VERSION:**
(write yours here)

---

## Q4. "Why did you choose Mantle?"

**MY DRAFT:**
The hackathon's own thesis is my thesis — every decision recorded on-chain.
I have five contracts live on Mantle Sepolia, source-verified on the explorer,
and the same reasoning hash comes out byte-identical in TypeScript, Python,
and Solidity — proven by a live call to the deployed contract, not just a test.

**YOUR VERSION:**
(write yours here)

---

## Q5. "What's your view on the future of AI and on-chain innovation?"

**MY DRAFT:**
Agents are about to move real money, and trust is the bottleneck. The future
is receipts, not stories. That's why I shipped the standard as an open SDK —
any team's agent can produce the same checkable receipts. The endgame is that
"verifiable" becomes table stakes for on-chain AI.

**YOUR VERSION:**
(write yours here)

---

## Q6 (bonus — they usually close with something like this).
## "Where can people find the project?"

**MY DRAFT:**
Everything's public: the live app is glass-box-alpha.vercel.app — go tamper
with the hash yourself. The repo is github.com/Alexander-Sorrell-IT/glass-box-alpha,
both BUIDLs are on DoraHacks, and I'm @AlexSorrellIT on X.

**YOUR VERSION:**
(write yours here)

---

## The three power lines (land at least one)
- "It hands you a receipt, not a story."
- "Tamper one byte, watch it turn red."
- "Explainable AI asks for trust. Verifiable AI lets you check."

## Never say (even casually)
beats the market · alpha · live on mainnet · NFTs minted · settlement is live ·
more than 2 on-chain commits · teams already using the SDK · published to npm.
If asked about performance: "the honest backtest shows variance reduction — I
refuse the alpha claim on purpose. The headline is the verifiable audit trail."

## After the recording stops
"Is the Mantle Global Accelerator's next cohort open? I'd want Glass-Box in it."
