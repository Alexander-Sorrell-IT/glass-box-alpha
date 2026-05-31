# Keynote demo shotlist — ~110 seconds

The submission's spine. Honest framing throughout: lead with **verifiable** and **same rule
for human and AI** — NEVER "our AI beats the market." Record screen + voiceover.

Live on-chain references (real, use them on camera):
- ReasoningHashAnchor: `0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d` (Mantle Sepolia)
- Committed receipt hash: `0x91349ba42e3321e47c2fa0a451412e9a22adfb8fcfb9c25bcc6a9a62872edb5c`
- Commit tx: `0x5b284c32f40457c1f2e8ce08b64c77233be4c2e484ae961328bad2cff3faaf6c`
- Explorer: https://sepolia.mantlescan.xyz/address/0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d

---

## 0:00–0:12 — The hook
- **Screen:** black, then type on screen: **"Can you out-reason an AI? Now you can *check*."**
- **VO:** "Every other AI asks you to trust its reasoning. This one hands you a receipt."

## 0:12–0:40 — Four minds, in the open
- **Screen:** the app — four agents (Chronos / Devil's Advocate / Web / Mood) reasoning. Make
  **Devil's Advocate's red dissent unmistakable** against the bullish majority.
- **VO:** "Four agents reason in the open on a Mantle market. Chronos is bullish. The Devil's
  Advocate disagrees — and flags coordinated wallets. They don't hide the disagreement."

## 0:40–0:52 — The seal
- **Screen:** the Fold resolves; cut to **Mantlescan** showing the committed hash
  `0x91349ba4…` at the contract address, timestamped.
- **VO:** "Before the market moves, each agent's reasoning is hashed — keccak256 — and committed
  to Mantle. Here it is on-chain. It can't be changed after the fact."

## 0:52–1:10 — Human vs AI
- **Screen:** the arena. A human sides with the Devil's Advocate, goes **bear**. The market drops.
  The human **beats Chronos**; the leaderboard re-sorts.
- **VO:** "You play too — no capital, just a call, scored by the *same on-chain rule* as the
  agents. Spot what the AI missed, and you out-reason it."

## 1:10–1:30 — One more thing: the tamper test
- **Screen:** the Verify panel. Recompute is **GREEN** — matches the on-chain commit. Then
  **edit a single character** of the reasoning → recompute flips **RED**, diverges from the
  chain. Restore it → **GREEN** again.
- **VO:** "And you can check it yourself. Recompute the hash in your browser — it matches the
  chain. Change one byte —" *(it turns red)* "— and it breaks. Explainable AI asks you to trust.
  Verifiable AI lets you check."

## 1:30 — Close
- **Screen:** the one-liner + repo + Mantlescan link.
- **VO:** "Glass-Box Alpha. The AI that hands you a receipt, not a story. Live on Mantle."

---

**Recording tips:** 1080p screen capture, no dead air, keep the tamper-test (the RED flip) as the
final beat — it's the moment. Total target ≤ 2:00 (the 20-Deploy award requires ≥ 2 min, so pad
the agent-reasoning section to land at ~2:00–2:10 if needed). Upload to YouTube/Loom, link in the
DoraHacks submission.
