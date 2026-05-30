# Glass-Box Alpha — Alpha & Data Track pitch

**One line:** Every other AI asks you to *trust* its reasoning. Glass-Box Alpha hands you a **receipt** you can recompute yourself.

## The enemy: post-hoc "explainable AI"
Today's explainable AI shows you a reasoning *story* — written, and editable, *after* the outcome is known. There's no way to prove the model actually reasoned that way, or that the explanation wasn't massaged to fit what happened. It asks for trust and gives you no way to check.

## The reframe: commit before the outcome, verify after
Glass-Box Alpha inverts it. Each of four agents commits the **keccak256 of its full reasoning** to Mantle **before the market moves**. The reasoning JSON is published off-chain. Anyone can later recompute the hash from that JSON and compare it to the on-chain commit:

- **Match (green):** this is provably the exact reasoning the agent committed, timestamped before settlement.
- **One byte different (red):** tampered. The seal breaks instantly.

This is the difference between *explainable* (trust the story) and **verifiable** (check the receipt).

## The proof (what a judge can do in 10 seconds, with their own hands)
1. Two timestamps: reasoning **committed at T0**, market **settled at T0 + 24h**. The AI could not have known the outcome when it wrote the reason down.
2. The browser recomputes `keccak256(canonical reasoning)` live — it equals the on-chain commit, byte-for-byte. *(Proven: the Python committer, the Solidity `verify()`, and the in-browser viem recompute all produce the identical digest — golden-vector test `agents/tests/test_receipt.py`.)*
3. The judge edits a single character of the published reasoning → the recompute turns red and diverges from Mantlescan. Restore it → green again.

`ReasoningHashAnchor.verify(agentId, decisionIndex, canonicalJson)` returns `(ok, stored, recomputed)` — the tamper test runs on-chain.

## Honesty clause (what this proves and what it does NOT)
This proves **provenance**, not correctness. It guarantees the reasoning is authentic and pre-commitment — *not* that the trade was right. We make **no claim to beat the market**: the Fold is a confidence-weighted consensus that ties a plain mean on direction; its measured value is variance reduction (beats the average single agent's Sharpe in 200/200 backtest seeds), and the backtest is supplementary evidence, not the headline. The headline is the **audit trail**: an AI whose reasoning is verifiable and pre-committed is a new primitive for on-chain finance — the missing trust layer between an agent's decision and the capital it moves.

## Why it fits Alpha & Data
- **Core data source:** Nansen on-chain smart-money flows (Chronos, Web) + sentiment (Mood) — real Mantle on-chain data, as required.
- **The role of AI:** four distinct reasoning frames produce a directional signal; the Fold aggregates.
- **Verifiable value on Mantle:** every reasoning receipt is keccak256-committed and on-chain-verifiable — the track's verifiability axis, made literal.
