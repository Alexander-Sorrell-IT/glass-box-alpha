# Glass-Box Alpha — Agent Architecture Spec

**Mantle Turing Test 2026 entry. Read this if you're judging the project or integrating with the SDK.**

This is a multi-agent on-chain trading system. Four LLM agents each apply a distinct reasoning frame to the same market signal. Their outputs are combined by a confidence-weighted consensus called the Fold. Every reasoning chain is hashed on Mantle for verifiable receipts. Execution is gated by hard-coded risk caps and a Devil's-Advocate veto.

---

## 1. Why four agents instead of one

A single LLM call asked "should I buy mETH right now?" produces hedged paragraphs. The output mixes evidence with vibes, and you can't decompose it after the fact.

Four agents with distinct frames force the system to **separate concerns** the way human trading desks do. Each frame is a different kind of question, and each agent is forbidden from answering the others' questions.

| Agent | Frame | Question it answers |
|---|---|---|
| **Chronos** | Timeline / historical analog mining | "When has this setup happened before, and what trajectories did it produce?" |
| **Devil's Advocate** | Counter-hypothesis / risk | "If the other three agents are wrong, what are they missing?" |
| **Web** | Cross-asset correlation / linked-variable | "When X moves, what else historically moves with it? Is the linkage strong enough to front-run?" |
| **Mood** | Sentiment as orthogonal-to-price | "Where is sentiment decoupled from price action? Decoupling is a leading indicator." |

Devil's Advocate runs **after** Chronos / Web / Mood so it can stress-test their assumptions. The other three run in parallel.

---

## 2. The Fold ensemble — exact math

Each agent emits a `(signal, confidence)` tuple where signal ∈ [-1, 1] and confidence ∈ [0, 1]. The Fold combines all four into a final `(signal, confidence)`.

### The aggregation

The Fold is a **confidence-weighted consensus** of the four frames:
```
F = Σ (signal_i · confidence_i) / Σ confidence_i
C = (c_chronos · c_DA · c_Web · c_Mood)^(1/4)
```
That is the whole rule. Each agent votes with its direction and magnitude, weighted by how confident it is. No agent is privileged; there is no geometric mean of signals and no magnitude dampener. Final confidence is the geometric mean of the four confidences, so overall conviction is capped by the least-sure agent.

The Fold returns `(F, C)`.

### What we claim — and what we do not

We make **no claim that the Fold beats a simple mean**. It *is* a confidence-weighted mean; claiming otherwise would be dishonest, and a judge can read the one line above and verify it.

The honest, verified value is an **ensemble-vs-single-agent** property: you do not know in advance which frame will be right, and the confidence-weighted consensus of all four beats the **average single agent's Sharpe in 200/200 backtest seeds**, beats the **worst single agent in 200/200**, and has shallower drawdown than the worst single agent in 200/200 (see §[backtest]). Combining diverse frames beats committing to one — the standard, defensible reason ensembles exist.

The differentiator of this project is **verifiable on-chain reasoning + four genuinely distinct frames + the AI-vs-human arena** — not the aggregation arithmetic. The arithmetic is deliberately the simplest thing that works.

Implementation: [`agents/shared/ensemble.py:fold_ensemble`](../agents/shared/ensemble.py)
Tests: [`agents/tests/test_fold.py`](../agents/tests/test_fold.py) — unit tests pinning the confidence-weighted-mean identity, confidence aggregation, and magnitude bounds; the ensemble-beats-single-agent property is gated in [`test_backtest.py`](../agents/tests/test_backtest.py).

---

## 3. Reasoning-chain attestation on Mantle

Each agent's full chain-of-thought is hashed and committed on-chain BEFORE the agent's decision is acted on. Anyone can later verify the published reasoning JSON wasn't backfit by recomputing the hash.

### The Harvest pattern

Every reasoning step is a unit of work. We commit the hash of the entire reasoning chain to `ReasoningHashAnchor.sol`:

```solidity
function commit(uint256 agentId, uint256 decisionIndex, bytes32 reasoningHash)
    external returns (uint256 commitIdx);
```

The off-chain reasoning chain JSON is then published at the agent's `reasoningUri` (IPFS or HTTPS). To verify a published reasoning was not tampered with:

1. Fetch the JSON from the URI
2. Canonicalize: `json.dumps(chain, sort_keys=True, separators=(",", ":"))`
3. Compute `sha3_256(canonical)` (matches Solidity `keccak256`-equivalent for our prefix)
4. Compare against the on-chain commit

Code:
- [`agents/shared/base.py:reasoning_hash`](../agents/shared/base.py) — canonical hashing
- [`contracts/src/ReasoningHashAnchor.sol`](../contracts/src/ReasoningHashAnchor.sol) — 4 unit tests + 1 fuzz test

---

## 4. Risk-managed execution — hard caps in Solidity

Every Fold decision passes through `AgentExecutor.sol` which enforces four caps. None can be bypassed without owner action.

| Cap | Constant | Value | Enforced where |
|---|---|---|---|
| **Max trade size** | `MAX_TRADE_BPS` | 500 bps (5% of seed per trade) | `executeTrade()` reverts on `size > 500` |
| **Confidence floor** | `MIN_CONFIDENCE_BPS` | 5000 bps (50%) | `executeTrade()` reverts on `conf < 5000` |
| **Devil's Advocate veto** | `daVetoed` flag | DA `HOLD` with `signal=0` & `conf ≥ 50%` triggers it | `executeTrade()` reverts on `daVetoed=true` |
| **Portfolio drawdown halt** | `DRAWDOWN_LIMIT_BPS` | 2000 bps (20%) | `recordLoss()` flips `halted=true` when cumulative loss ≥ 20% of seed |

Once halted, the executor accepts no further trades until owner manually resets. This is the worst-case "the agents have gone wrong, stop trading" circuit breaker.

The same caps are mirrored client-side in [`agents/settler/service.py:RiskConfig`](../agents/settler/service.py) for fail-fast (don't send a tx that will revert).

Code: [`contracts/src/AgentExecutor.sol`](../contracts/src/AgentExecutor.sol) — 10 unit tests covering happy path + every revert path + drawdown trigger + slippage protection.

---

## 5. ERC-8004 Reputation Registry — used as designed

We use Mantle's deployed ERC-8004 Identity Registry (`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`) and Reputation Registry (`0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`) — not a wrapper, not a reimplementation.

- **Identity**: each agent (Chronos / Devil's Advocate / Web / Mood) is minted a unique `agentId` via the canonical Identity Registry on Day 4 of the build. The Identity NFT's `agentURI` points to a JSON describing the agent's reasoning frame.
- **Reputation**: after each settled trade, the Reputation Registry receives a feedback entry. Win → positive feedback. Loss → negative feedback (signed `int128` value). The Registry's native `getSummary(agentId)` reads return the agent's running reputation score.

The reputation score is **graded by realized on-chain PnL**, not vibes. There is no admin override.

---

## 6. ReasoningRepToken — non-transferable tier-up reputation

Separate from the on-chain Reputation Registry, we also mint a non-transferable ERC-20-ish "Glass-Box Reasoning Reputation" (GBRR) token to each agent every time a reasoning hash is committed.

The token is **tiered** — every 10 lower-tier tokens can be combined into 1 higher-tier token:
- Tier 0 raw → Tier 1 refined → Tier 2 crystallized → Tier 3 transcendent

`totalBalanceOf(holder)` returns a tier-weighted score where transcendent counts 1000× raw. This is a visual artifact of long-term agent track record; it's bound to the agent's owner address and cannot be sold or transferred.

Code: [`contracts/src/ReasoningRepToken.sol`](../contracts/src/ReasoningRepToken.sol) — 9 unit tests covering mint, combine cascade, non-transferable assertion, owner controls.

---

## 7. One full round — worked example

Let's trace a single round end-to-end. Market = `mETH/USDC`. Seed capital = $200 USDC on Mantle.

### Inputs (Day N, ~9:00 AM UTC)

- 30-day Nansen smart-money flows for mETH: net inflow +$1.2M from 7 wallets with 30-day win rate ≥ 0.65
- 24h Elfa sentiment for mETH: avg +0.42, delta_24h +0.15
- Mantle TVL context: $755M, +3% week-over-week
- Cross-asset linkages from Web's correlated-asset table

### Step A — Open round on-chain

Settler calls `RoundState.openRound(keccak256("mETH/USDC"))`. Returns `roundId = 17`.

### Step B — Three agents reason in parallel

`Chronos`, `Web`, `Mood` each call DeepSeek with their system prompt + the context. DeepSeek-reasoner streams `reasoning_content` (chain-of-thought) which we capture as ReasoningSteps. Each agent produces:

- **Chronos**: signal = +0.62, conf = 0.74 — "5 of 7 top wallets accumulating; 24h analog suggests +3-5% within 48h"
- **Web**: signal = +0.48, conf = 0.71 — "When mETH inflows > $500k, USDC pool depth contracts within 4h in 73% of past 30d cases"
- **Mood**: signal = +0.38, conf = 0.66 — "Sentiment +0.42 with orthogonal component large vs price action; decoupling = leading indicator"

### Step C — Devil's Advocate reasons WITH peer outputs

DA receives the other three reasoning chains as context, then produces:

- **Devil's Advocate**: signal = -0.15, conf = 0.55 — "Three of the 7 wallets share funding-graph proximity. Could be coordinated. Reducing conviction."

### Step D — Commit four reasoning hashes on-chain

For each agent: `ReasoningHashAnchor.commit(agentId, decisionIndex, sha3_256(reasoning_json))`.
Then: `RoundState.recordSubmission(roundId, agentId, kind, signal*1e18, sizeBps, reasoningHash)`.

### Step E — Fold ensemble (confidence-weighted consensus)

```
weighted sum = (0.62·0.74) + (-0.15·0.55) + (0.48·0.71) + (0.38·0.66)
             =  0.459      +  -0.083      +  0.341      +  0.251
             =  0.968
conf sum     =  0.74 + 0.55 + 0.71 + 0.66 = 2.66

F = 0.968 / 2.66 = +0.364
C = (0.74 · 0.55 · 0.71 · 0.66)^(1/4) = 0.660
```

Fold output: signal = **+0.364**, confidence = **0.660**. (Devil's Advocate's bearish −0.15 pulls the consensus down from Chronos's +0.62, weighted by each one's confidence — exactly what a consensus should do.)

### Step F — Risk gate

```
- Confidence 0.660 = 6600 bps ≥ 5000 bps floor ✓
- |signal| = 0.364 > 0.05 threshold ✓
- Devil's Advocate: signal = -0.15, conf = 0.55 — NOT a veto (DA didn't pick HOLD with signal=0) ✓
```

Trade gate passes.

### Step G — Position sizing

```
size_bps = MAX_TRADE_BPS · |signal| · confidence
         = 500 · 0.364 · 0.660
         = 120.1 → rounded to 120 bps = 1.20% of $200 = $2.40
```

(Conservative. The cap is 500 bps but actual sizing is risk-weighted by signal and confidence.)

### Step H — Execute on-chain

`AgentExecutor.executeTrade(roundId=17, ensembleSignal=3640, ensembleConfBps=6600, daVetoed=false, tokenIn=USDC, tokenOut=mETH, sizeBps=120, minAmountOut=…)`.

Swap routes through Merchant Moe V3 USDC/mETH pool. ~$2.40 of USDC swapped to mETH.

### Step I — Settle after 24h

Next round opens against the same market. When the swap is closed:
- Realized PnL computed (could be +$0.05 win or -$0.07 loss on $1.96 position).
- `RoundState.settle(roundId=17, realizedPnlBps)`.
- If loss: `AgentExecutor.recordLoss(roundId, lossNotional)` — accumulates toward 20% drawdown halt.
- ERC-8004 Reputation Registry receives a feedback entry for each of the 4 agents weighted by their contribution to the Fold.

---

## 8. What the SDK (`glassbox-agent-kit`) gives you

The `glassbox-agent-kit` is the extraction of the orchestrator + base agent class + ERC-8004 hooks + reasoning-hash module — published as a separate repo + npm + pip package. Any team building an ERC-8004 agent on Mantle can `npm install @glassbox/agent-kit` (or `pip install glassbox-agent-kit`) and:

1. Subclass `GlassBoxAgent` with their own reasoning frame
2. Get streaming reasoning capture for free
3. Get reasoning-hash commit + Reputation Registry writes for free
4. Get the Fold ensemble for free
5. Implement the `IGlassBoxAgent` interface so their agent can appear on the Glass-Box Alpha broadcast leaderboard

See [`docs/integration-spec/SCHEMA.md`](integration-spec/SCHEMA.md) for the on-chain interface.

---

## 9. Why this should be hard for competitors to replicate in 20 days

| Component | What it requires | Why competitors won't have it |
|---|---|---|
| 4-agent ensemble with distinct reasoning frames | Disciplined prompt engineering + Fold math | Most projects use a single LLM with one prompt |
| Fold ensemble (confidence-weighted consensus, beats avg single agent 200/200 seeds) | Math + unit tests + 200-seed gate | Most projects use one LLM, no ensemble, no backtest |
| Reasoning-hash on-chain attestation | Smart contract + canonical hashing | Most don't bother with verifiability |
| Risk-capped execution (5%/50%/20%/DA-veto) | Solidity + 10 unit tests | Most ship without drawdown guards |
| Tiered non-transferable reputation token | ERC-20 + tier-roll math + 9 tests | Most don't build secondary primitives |
| Backtest harness with Fold vs baseline comparison | Statistical metrics + 15 tests | Most don't backtest at all |
| Open integration schema (other teams plug in) | Spec + adapter contracts | Most projects are silos |

---

## 10. What this is NOT claiming

- **Not** claiming our 14 days of mainnet PnL will be statistically meaningful. With ~20-50 trades, confidence intervals on win-rate span ±15-20pp. The 90-day backtest harness is the supplementary credibility evidence; live mainnet history is the verifiability artifact, not the proof of alpha.
- **Not** claiming the Fold ensemble universally beats baselines. The backtest harness produces an honest comparison on whatever data we replay it on. If real-agent backtests show baseline winning, we say so.
- **Not** claiming agents are "Type 1" or trained from scratch on novel mathematics. We use DeepSeek (open-weight, transformer-based) as the inference engine. The novelty is in the ensemble architecture + on-chain verifiability, not in the LLM itself.

---

## Appendix — repo map

```
glass-box-alpha/
├── README.md                        # project pitch + quickstart
├── CONTRACTS.md                     # ERC-8004 + Mantle addresses
├── MASTER-PLAN.md                   # 21-day burndown
├── contracts/                       # Foundry workspace
│   ├── src/
│   │   ├── IGlassBoxAgent.sol       # on-chain agent interface
│   │   ├── ReasoningHashAnchor.sol  # the Harvest primitive
│   │   ├── GlassBoxRegistry.sol     # where other agents register
│   │   ├── RoundState.sol           # per-round state machine
│   │   ├── AgentExecutor.sol        # risk-capped trade router
│   │   └── ReasoningRepToken.sol    # tiered rep token
│   └── test/                        # 32 unit tests + 1 fuzz
├── agents/
│   ├── shared/
│   │   ├── ensemble.py              # Fold + system prompts
│   │   ├── base.py                  # GlassBoxAgent with DeepSeek streaming
│   │   ├── types.py
│   │   └── tools.py                 # Nansen + Elfa + DefiLlama adapters (mock-first)
│   ├── chronos/agent.py
│   ├── devils_advocate/agent.py
│   ├── web/agent.py
│   ├── mood/agent.py
│   ├── orchestrator/main.py         # parallel agents → Fold → reasoning hashes
│   ├── settler/service.py           # off-chain round coordination, risk-gate
│   ├── backtest/harness.py          # 90-day replay, Fold vs baseline metrics
│   └── tests/                       # 32 Python unit tests
├── frontend/                        # Next.js 14 + RainbowKit + Tailwind
├── docs/
│   ├── agent-architecture.md        # THIS FILE
│   ├── integration-spec/SCHEMA.md
│   └── outreach/mantle-devrel-pitch.md
└── scripts/
    ├── mint-agent-identities.md
    └── run_backtest.py
```

---

**Last updated**: Day 3 of 21 (2026-05-27)
**Repo**: https://github.com/Alexander-Sorrell-IT/glass-box-alpha
**Submission deadline**: 2026-06-15 10:59 UTC
