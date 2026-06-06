# Keynote demo shotlist — target 2:20–2:40 (HARD floor 2:00)

The submission's spine. Honest framing throughout: lead with **verifiable** and **same rule
for human and AI** — NEVER "our AI beats the market." Record screen + voiceover.

> ⚠️ **The 20-Deploy award requires a demo video ≥ 2:00.** Do NOT ship a 1:50 cut. The beats below
> are timed to land at ~2:20–2:40 with the expanded agent-reasoning + tamper sections — comfortably
> over the floor. Time a silent run first.

> **Record on the FINAL app:** the public Vercel URL, with `heroRound.ts` (a real DeepSeek round, not
> the SIMULATED fixtures) and the `<Ring>` hero in place. Shot 18–40 below is the Ring; the tamper
> panel and Mantlescan links must show the verified contract.

Live on-chain references (real, use them on camera) — the SAME captured round the Ring renders:
- ReasoningHashAnchor: `0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d` (Mantle Sepolia)
- Chronos captured-round receipt hash: `0xfedc499efb7e22a4050c72b80e5cf84a04e64afab3bf8d605dacad3b5dedbd33`
  (committed at `getCommit(agentId=1, decisionIndex=0)`)
- Commit tx: `0xaa64a6c6459a15e865c1c8d72fe3ff5df7e7c59ece74e49c9c692775d40f77d5`
- Explorer: https://sepolia.mantlescan.xyz/address/0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d

---

## 0:00–0:12 — The hook
- **Screen:** black, then type on screen: **"Can you out-reason an AI? Now you can *check*."**
- **VO:** "Every other AI asks you to trust its reasoning. This one hands you a receipt."

## 0:12–0:40 — Four minds, in the open
- **Screen:** the Ring hero — four reasoning frames fold into one call. **Chronos and Web are
  bearish (PERP_SHORT, the fat red ribbons); Mood holds (neutral, grey); the Devil's Advocate
  breaks ranks BULLISH (PERP_LONG, the lone green ribbon riding up, tagged "DISSENT ↑").** The
  ribbons merge down to the Fold node, PERP_SHORT −0.33.
- **VO:** "Four agents reason in the open on a Mantle market. Chronos and Web read the net outflow
  as selling, and go short. But the Devil's Advocate takes the other side — it argues the outflow
  is a one-off whale, the seven-day trend is still positive, and the bearish analogs are
  cherry-picked. They don't hide the disagreement — the Fold weighs it into a cautious short."

## 0:40–0:52 — The seal
- **Screen:** the Fold resolves to PERP_SHORT −0.33; cut to **Mantlescan** showing Chronos's
  committed hash `0xfedc499e…` at the contract, timestamped before settlement.
- **VO:** "Before the market moves, each agent's reasoning is hashed — keccak256 — and committed
  to Mantle. Here it is on-chain. It can't be changed after the fact."

## 0:52–1:10 — Human vs AI
- **Screen:** the arena. A human sides with the lone dissenter — the Devil's Advocate — and goes
  **bull** against the bearish Fold. Scored by the *same on-chain rule* as the agents; the
  leaderboard re-sorts.
- **VO:** "You play too — no capital, just a call, scored by the same on-chain rule as the agents.
  Back the dissenter or back the Fold — and let reality settle it."

## 1:10–1:30 — One more thing: the tamper test
- **Screen:** the Verify panel directly below the Ring — **the same Chronos reasoning** shown in
  the hero. Recompute is **GREEN** — "MATCHES ON-CHAIN · read from Mantle". Then **edit a single
  character** of the reasoning → recompute flips **RED**, diverges from the on-chain commit.
  Restore it → **GREEN** again.
- **VO:** "And you can check it yourself. Recompute the hash in your browser — it matches the
  chain. Change one byte —" *(it turns red)* "— and it breaks. Explainable AI asks you to trust.
  Verifiable AI lets you check."

## 1:30 — Close
- **Screen:** the one-liner + repo + Mantlescan link.
- **VO:** "Glass-Box Alpha. The AI that hands you a receipt, not a story. Live on Mantle."

---

**Recording tips:** 1080p screen capture, no dead air, keep the tamper-test (the RED flip) as the
final beat — it's the moment. **Land at 2:20–2:40** (hard floor 2:00 for the 20-Deploy award) by
expanding the four-minds section (Shot 0:12–0:40 → ~0:35) and the tamper test (let the recompute
hash visibly stream as you type). Upload to YouTube/Loom, link in the DoraHacks submission + README.

---

## Spoken submission answers (Alpha & Data "Tell Us") — say in VO or paste in the description
- **Data sources:** Mantle on-chain data via **Nansen** smart-money flows + **Elfa** sentiment.
- **Role of AI:** four DeepSeek-reasoner agents produce distinct reasoning chains (timeline analogs,
  counter-hypothesis, cross-asset linkage, sentiment-orthogonal-to-price); the **Fold** is a
  transparent confidence-weighted consensus.
- **Verifiable value on Mantle:** every chain's keccak256 is committed on-chain *before* settlement,
  so the alpha claim is auditable in-browser, not asserted — the tamper test proves it.

## Pre-record checklist (gates the recording)
- [ ] Public Vercel URL live; `NEXT_PUBLIC_SITE_URL` set (clean page, working OG)
- [ ] `heroRound.ts` = a real captured DeepSeek round (NOT the SIMULATED fixtures)
- [ ] `<Ring>` hero in place as the page centerpiece
- [ ] Contracts verified on Mantlescan (so Shot 0:40 + close show the green ✓)
- [ ] HumanCall works (wallet connected, or keyless demo path)
- [ ] Silent timing run ≥ 2:00 before recording with VO
