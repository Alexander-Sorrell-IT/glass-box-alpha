> **BUIDL #2 — paste-ready submission card.** Tracks: **AI DevTools (Tencent Cloud)**.
> Every claim traces to docs/claims-ledger.md (BUILT_TESTED unless marked). No banned phrasings.

---

# glassbox-agent-kit

**Tagline:** Ship a verifiable AI agent on Mantle in one `npm install` — every decision becomes a receipt anyone can recompute, check the data-liveness of, and beat under the same on-chain rule.

## What it is
`glassbox-agent-kit` is the reusable TypeScript SDK extracted from Glass-Box Alpha — the **reasoning-receipt primitive** as a standalone, publish-ready package (v0.1.0, ESM, viem ^2.21). Most agent frameworks ask you to *trust* the model. This one hands the user a receipt: the keccak256 of a canonical reasoning chain, committed on-chain **before** the outcome, that anyone can recompute — tamper one byte and it turns red.

## What a developer gets (the API)
- `GlassBoxAgent` / `decide()` — subclass it, return your reasoning + decision, get a reproducible chain + on-chain-ready receipt hash. LLM-agnostic (DeepSeek, Claude, local, or deterministic).
- `canonicalReceipt` / `receiptHash` — the hash, **byte-identical across TypeScript, Python, and the Solidity contract** — proven live, not just asserted: calling `verify()` on the deployed Sepolia anchor recomputes the exact golden hash that the TS and Python implementations produce independently. Reproduce it yourself in two commands: `npm ci && npm test` (15 tests: golden vectors, one-byte tamper, Solidity truncate-toward-zero parity), then `npm run example:foreign` offline.
- `parseProvenance` / `isFullyLive` — each data source's liveness (`nansen:live` / `:mock` / `mantle-rpc:live@block=N`) is committed *inside* the receipt, so it **can't claim mock data was live**.
- `arenaScore` / `scoreDecision` / `beats` — a byte-for-byte mirror of the on-chain `HumanArena.score()` rule, so a human or a foreign agent can be graded by the **same** rule off-chain (pinned to the contract incl. the truncate-toward-zero edge case).
- `commitReasoning` / `verifyReasoning` — commit/recompute against the live `ReasoningHashAnchor` (source-verified on Mantle Explorer, Exact Match).

**Zero-friction by design:** one runtime dependency (viem), Node ≥18, ESM, fully typed. The 30-second quickstart runs offline with no keys and no network. The golden-vector and arena-parity suites are plain vitest — wire `npm test` into CI and any drift between your receipts and the on-chain rule fails the build.

## The proof it's a *sufficient* standard, not a demo
`examples/foreign-agent.ts` is a **foreign agent** (a funding-skew frame — not one of Glass-Box's four) built on **nothing but the published package**. Run `npm run example:foreign` (offline) and it produces a receipt a stranger can:
- **recompute** (and watch a one-byte tamper break it),
- **read the provenance of** (`isFullyLive` → false, because one source was mock — the receipt says so),
- **beat** (score it vs a human call under `arenaScore`, the same rule the contract enforces).

A third-party team needs only this package to ship a verifiable, check-and-beatable agent on Mantle.

## Built + tested
- **15 passing TypeScript/vitest tests** (receipt golden + tamper + Fold + provenance parser + arena-score parity). `npm run build` emits a `dist/` that exposes the full API; `tsc --noEmit` clean.
- Targets the **live** `ReasoningHashAnchor` on Mantle Sepolia (`0xB0319b2e…93353d`) — commit/verify run against a real deployed contract.

## What provenance proves (and what it doesn't)
The receipt proves the **integrity of the record**, not the correctness of the decision: it cannot be rewritten after the fact, and it cannot claim mock data was live — each input's liveness is hashed inside it. Where generic LLM commentary is unfalsifiable, every receipt here is recomputable to the byte. Compliance posture follows from the same property: the receipt trail is the pre-trade decision record auditors actually ask for — sealed before the outcome, recomputable by any third party, with data-liveness disclosed inside the hash. The companion HumanArena takes no user capital, and the kit makes no market-beating or alpha claims by design — that refusal is enforced in the code's own docstrings.

## Honest status (don't overclaim)
- **Not yet published to npm** — the package is publish-ready and lives in-repo (`kit/`); `npm view glassbox-agent-kit` → 404. Install today via the repo.
- `commitReasoning` / `verifyReasoning` run end-to-end offline and were validated manually on-chain, but are **not** yet in the automated test suite.

## Links / fields for the form
- **Repo:** github.com/Alexander-Sorrell-IT/glass-box-alpha  (SDK in `kit/`)
- **Demo:** `npm run example:foreign` (offline) · product video: https://youtu.be/_dSQyfMcX6U
- **On-chain target:** ReasoningHashAnchor `0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d` (Mantle Sepolia, chain 5003)
- **Track:** AI DevTools (Tencent Cloud)
