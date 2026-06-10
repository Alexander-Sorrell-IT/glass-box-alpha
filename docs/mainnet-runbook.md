# Mainnet runbook — from "Sepolia today" to "live on Mantle"

Every CODE gap between the tested round flow and a real chain is closed
(`agents/settler/live.py`, `mantle_spot_price`, the web3-v7 shim fixes). What
remains is operational: a funded key and one forge command.

**Honesty note before you start:** `--live` has NEVER been executed — every
refusal gate and wiring path is tested offline and ABI-cross-checked, but the
first operator IS the first live run. That is why step 0 rehearses on Sepolia.

## Cost (estimated from receipts + live reads — not a measured mainnet deploy)

Provenance of each number: gasUsed comes from the actual Sepolia deploy receipts
in `contracts/broadcast/Deploy.s.sol/5003/run-latest.json`; gas price (50.0001
gwei), MNT/USD ($0.54), and the DA-fee oracle were read live off mainnet RPCs on
2026-06-10; the commit() figure is an `eth_estimateGas` against the live Sepolia
anchor (mined cost will land somewhat lower). Re-check all of them before relying
on them.

| Step | Gas | MNT | USD |
|---|---|---|---|
| Deploy all 5 contracts | 2,608,439 | ~0.1304 | ~$0.07 |
| One reasoning commit() | ~143,916 (estimate) | ~0.0072 | ~$0.004 |
| Full first round (open + 4 commits + 4 submissions + ensemble) | — | ~0.08 | ~$0.05 |

Fund the deployer with **1 MNT** (~$0.55): deploy (~0.13) + ~10 rounds (~0.8)
fits with margin. DA/L1 data fees on Mantle mainnet are negligible (<0.001%).

## 0. Rehearse on Sepolia first

The `.env.example` live-runner defaults already point at the LIVE Sepolia deploy
(chain 5003). Run the full sequence there — `run --live`, then `settle --live` —
with a Sepolia-funded key before touching mainnet. Same code, free mistakes.

## 1. Deploy (one command)

```bash
cd contracts
# Put DEPLOYER_PRIVATE_KEY (and MANTLE_MAINNET_RPC) in the repo-root .env — see
# .env.example. Never type the key into the shell: it persists in ~/.bash_history.
# forge does not auto-load the repo-root .env from here, so:
set -a; source ../.env; set +a
# optional: SETTLER_ADDRESS if the settler service signs with a different key
forge script script/Deploy.s.sol --rpc-url mantle_mainnet --broadcast --verify
```

Stricter option for a long-lived key: a Foundry keystore (`cast wallet import
deployer --interactive`, then `forge script --account deployer`) — requires
Deploy.s.sol to switch to parameterless `vm.startBroadcast()`, so treat it as a
follow-up, not this runbook.

`Deploy.s.sol` already handles ordering (RoundState before HumanArena) and prints
all 5 addresses. `--verify` needs `MANTLE_EXPLORER_API_KEY`; if verification fails,
deployment still succeeds — retry with `forge verify-contract` later, and per the
claims ledger do NOT claim "verified on Mantle Explorer" until it actually is.

## 2. Point the live runner at mainnet

In `.env` (see `.env.example`, "Live runner" block):

```bash
GLASSBOX_RPC_URL=https://rpc.mantle.xyz
SETTLER_PRIVATE_KEY=0x...                  # the RoundState settler key
ROUND_STATE_ADDRESS=<from deploy output>
REASONING_ANCHOR_ADDRESS=<from deploy output>
# AGENT_EXECUTOR_ADDRESS stays unset until the executor is deployed with the
# Merchant Moe router — the round flow runs without the trade leg.
DEEPSEEK_API_KEY=...                       # the orchestrator refuses to run without it
```

Constraint baked into the contracts: the signing key must be RoundState's
`settler` (constructor arg, defaults to deployer) or recordSubmission /
setEnsemble / settle revert `NotSettler`.

## 3. First live round + settlement

```bash
# dry-run first — same code path, no txs:
python -m agents.settler.live run --market mETH/USDC

# the real thing: seeds decision indices from the anchor, reads a live
# settlement-grade price (refuses to start without one), opens the round,
# commits 4 reasoning hashes, records 4 submissions, sets the ensemble:
python -m agents.settler.live run --market mETH/USDC --live

# after the settlement window, grade the ALREADY-COMMITTED signals against a
# fresh independent price read and write realized bps on-chain:
python -m agents.settler.live settle --record receipts/rounds/round_<id>.json --live
```

The round record (`receipts/rounds/round_<id>.json`; dry-runs write
`dry_round_<id>.json` — separate namespace, and `--live settle` refuses dry-run
records outright) carries both price reads with their provenance tags
(`defillama-price:live@ts=N`) — the same honesty rule as the receipts: it never
grades on an invented price, it waits. Two operational details: the reference
price is read at round START (minutes before the commits land — the record's
`ts=` makes the drift visible), and a live round that crashes mid-flight leaves
`receipts/rounds/inflight_*.json` carrying that price, so the on-chain round
stays gradeable. Records are gitignored; a settled record you want as public
evidence gets committed deliberately with `git add -f`.

## 4. After the first settled round — update the claims

In order, against `docs/claims-ledger.md`:

1. Flip the chain rows: contracts live on **5000** (keep the Sepolia rows too) —
   only after re-verifying yourself (`eth_getCode` for all 5 on rpc.mantle.xyz),
   same as every other row: evidence first, claim second.
2. "no round has been opened on-chain" / `roundsCount()=0` rows — re-verify and rewrite.
3. The DO_NOT_CLAIM rows that exist only because the thing wasn't live yet
   ("deployed on Mantle mainnet", "PnL settlement is live", "more than 2 commits")
   become claimable ONLY after re-running the verification in their Evidence column.
4. README/pitch/video copy: "live on Mantle Sepolia" → "live on Mantle" only after
   steps 1-3. The hedges come out in the same commit that proves them unnecessary.
5. Frontend `lib/contracts.ts`: add the mainnet addresses (today's `*_MAINNET`
   exports hold Sepolia values — the file header says so; make the name honest).

## Out of scope for this runbook (still design / later)

- ERC-8004 identity mints + binding (AGENT_IDS are placeholders 1-4).
- AgentExecutor/MerchantMoeAdapter deploy (needs live LB router + seed capital).
- Auto-scheduling rounds (cron/daemon) — `run`/`settle` are deliberate manual
  steps until at least one settled round is verified end-to-end.
