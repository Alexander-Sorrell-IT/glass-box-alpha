# glassbox-agent-kit demo shotlist — ~2:00 (BUIDL #2, AI DevTools)

A developer-facing screencast: install the SDK, build a transparent agent, and watch
its reasoning receipt verify against the **same live Mantle Sepolia contract** that
Glass-Box Alpha uses. Honest framing: this is the reusable core, not a toy — the
byte-parity test is the proof. Record terminal + editor + Mantlescan.

Live references (real, use on camera):
- ReasoningHashAnchor: `0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d` (Mantle Sepolia)
- Explorer: https://sepolia.mantlescan.xyz/address/0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d
- Repo: `kit/` in github.com/Alexander-Sorrell-IT/glass-box-alpha

---

## 0:00–0:12 — The problem
- **Screen:** title card — **"Every AI agent asks you to trust it. Ship one that hands out receipts."**
- **VO:** "glassbox-agent-kit lets any developer put a verifiable AI agent on Mantle in under
  30 minutes. Here's the whole thing."

## 0:12–0:35 — Install + the parity proof
- **Screen:** terminal. `npm install` in `kit/`, then `npm test`.
- **Screen:** the 5/5 vitest pass — zoom the line that checks `receiptHash` equals the golden
  `0xf8ae…b82a`.
- **VO:** "Install, and run the tests. This one matters: the SDK's hash of a reasoning chain
  equals — byte for byte — the Python agent, the Solidity contract, and the browser. Same hash
  everywhere. That's what makes 'verify it yourself' literally true."

## 0:35–1:05 — Build an agent in a few lines
- **Screen:** editor — show the quickstart: subclass `GlassBoxAgent`, implement `reason()`
  (steps + a decision), nothing else.
- **Screen:** `npm run example` → prints each agent's decision + receipt hash + the Fold.
- **VO:** "You subclass one base, implement `reason()` — wire any model or your own logic — and
  you get a reproducible reasoning chain and its on-chain-ready receipt hash. Four lines of
  glue. The Fold combines several agents into one confidence-weighted call."

## 1:05–1:40 — Commit & verify on the real contract
- **Screen:** uncomment the commit block (set `PRIVATE_KEY`), run it → a Sepolia tx hash.
- **Screen:** cut to Mantlescan at the contract address — the commit is there, timestamped.
- **Screen:** call `verifyReasoning(...)` → `ok: true`. Then change one field of the chain in
  code, re-run verify → `ok: false`.
- **VO:** "Commit the receipt before the outcome is known — one call, against the same live
  Mantle contract. Anyone re-hashes the published chain to check it: matches, true. Change one
  byte —" *(ok: false)* "— and it breaks. The tamper test is built in."

## 1:40–2:05 — Close
- **Screen:** the API table from the README + ERC-8004 registry addresses + repo link.
- **VO:** "Receipt primitive, agent base, the Fold, on-chain commit and verify, ERC-8004 identity
  shapes — MIT-licensed, on npm. Build a transparent agent on Mantle, and let the world check
  its work. glassbox-agent-kit."

---

**Recording tips:** keep the `npm test` parity line and the `ok: true → false` flip as the two
hero beats. 1080p, terminal + editor split, no dead air. Land at ~2:00+ to clear the 20-Deploy
≥2-min bar. Upload to YouTube/Loom; link in the BUIDL #2 submission.
