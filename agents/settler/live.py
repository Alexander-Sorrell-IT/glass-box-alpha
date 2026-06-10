"""Live-runner composition root — the one file that binds the tested pieces to a real chain.

Everything underneath was already built and tested in isolation (the SettlerService
round flow, resolve_outcome/score_prediction, the orchestrator payload contract);
what was missing was the wiring:

  * a signing web3 client (web3 v7 SignAndSendRawMiddleware + default_account),
  * contract handles loaded from the compiled Foundry ABIs in contracts/out/,
  * chain-seeded decision indices — the anchor reverts AlreadyCommitted() on a
    reused (agent_id, decision_index) and the in-process counter dies on restart,
  * a settlement-grade price read AT COMMIT TIME (mantle_spot_price — declares
    `defillama-price:unavailable` honestly, never silently mock),
  * a persisted round record so a later `settle` grades the ALREADY-COMMITTED
    signals against two independent price reads — never a re-derived signal.

Dry-run by default. `--live` is the single flag between paper and chain, exactly as
SettlerService was designed ("the same class drives Sepolia testnet and Mantle
Mainnet without code change"). A LIVE round refuses to start unless the commit-time
price read is live — settlement must never be born ungradeable.

Usage (from repo root, env per .env.example):
    python -m agents.settler.live run --market mETH/USDC             # dry-run round
    python -m agents.settler.live run --market mETH/USDC --live      # real txs
    python -m agents.settler.live settle --record receipts/rounds/round_42.json [--live]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger

from agents.settler.service import RoundOutcome, SettlerService
from agents.shared.tools import mantle_spot_price

load_dotenv()  # `settle` never imports the orchestrator, so .env must be loaded here too

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_RECORD_DIR = _REPO_ROOT / "receipts" / "rounds"

# Same placeholder ids as the orchestrator — real ERC-8004 token ids replace these
# after the identity mints (docs/claims-ledger.md: binding is design-only today).
AGENT_IDS = {"chronos": 1, "web": 2, "mood": 3, "devils_advocate": 4}

_MAX_INDEX_PROBE = 10_000  # runaway guard for the on-chain index probe


# ---------- chain wiring ----------

def load_abi(contract_name: str) -> list[dict[str, Any]]:
    """ABI from the compiled Foundry artifact — single source of truth, no vendored copies."""
    artifact = _REPO_ROOT / "contracts" / "out" / f"{contract_name}.sol" / f"{contract_name}.json"
    if not artifact.exists():
        raise FileNotFoundError(f"{artifact} missing — ABIs are generated, not committed: "
                                "run `forge build` in contracts/ first")
    return json.loads(artifact.read_text())["abi"]


def build_w3(rpc_url: str, private_key: str):
    """Signing web3 client: local-sign middleware + default_account, so the service's
    bare ``.transact()`` shims work against public RPCs (which host no accounts)."""
    from eth_account import Account
    from web3 import Web3
    from web3.middleware import SignAndSendRawMiddlewareBuilder

    account = Account.from_key(private_key)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    signer = SignAndSendRawMiddlewareBuilder.build(account)
    w3.middleware_onion.inject(signer, layer=0)  # type: ignore[arg-type]  # web3 stubs lag the v7 builder
    w3.eth.default_account = account.address
    return w3


def contract_handles(w3) -> dict[str, Any]:
    """RoundState + anchor (required) and AgentExecutor (optional) from env addresses.

    The sender key must be RoundState's `settler` AND (if trading) AgentExecutor's
    `owner` — recordSubmission/setEnsemble/settle and executeTrade are gated on-chain.
    """
    from web3 import Web3

    def _required(env: str) -> str:
        value = os.environ.get(env, "")
        if not value:
            raise RuntimeError(f"{env} is not set — see .env.example (live runner block)")
        address = Web3.to_checksum_address(value)  # env values may arrive lowercase
        # Wrong-chain config (e.g. mainnet RPC + the Sepolia defaults still in .env)
        # must fail HERE with a clear message, not as a confusing revert mid-round.
        if not w3.eth.get_code(address):
            raise RuntimeError(f"{env}={address} has no code on chain {w3.eth.chain_id} — "
                               "wrong chain or stale addresses in .env?")
        return address

    handles: dict[str, Any] = {
        "round_state": w3.eth.contract(address=_required("ROUND_STATE_ADDRESS"),
                                       abi=load_abi("RoundState")),
        "reasoning_anchor": w3.eth.contract(address=_required("REASONING_ANCHOR_ADDRESS"),
                                            abi=load_abi("ReasoningHashAnchor")),
        "executor": None,
    }
    if os.environ.get("AGENT_EXECUTOR_ADDRESS", ""):
        handles["executor"] = w3.eth.contract(address=_required("AGENT_EXECUTOR_ADDRESS"),
                                              abi=load_abi("AgentExecutor"))
    return handles


def next_decision_index(anchor, agent_id: int, start: int = 0) -> int:
    """First free decision_index for an agent, probed off the anchor itself.

    The anchor reverts AlreadyCommitted() on reuse and getCommit() reverts 'no commit'
    on a free slot, so the first index where getCommit REVERTS is safe to commit to.
    Transport errors (dead RPC, rate limit) must PROPAGATE — reading one as a free
    slot would seed a stale index and kill the round at the first commit, after
    openRound already mined. Seeding from the CHAIN (not a local file) is what makes
    a process restart unable to fork history. Sequential probe — commit counts are
    tiny (Sepolia: 2).
    """
    from web3.exceptions import ContractLogicError

    for index in range(start, start + _MAX_INDEX_PROBE):
        try:
            anchor.functions.getCommit(agent_id, index).call()
        except ContractLogicError:  # contract revert 'no commit' — this slot is free
            return index
    raise RuntimeError(f"no free decision_index for agent {agent_id} "
                       f"in [{start}, {start + _MAX_INDEX_PROBE})")


def _build_live_service(run_round_fn=None) -> SettlerService:
    """Wire SettlerService to a real chain from env: RPC, key, addresses, seeded indices."""
    from agents.orchestrator.main import run_round

    rpc_url = os.environ.get("GLASSBOX_RPC_URL", "")
    key = os.environ.get("SETTLER_PRIVATE_KEY") or os.environ.get("DEPLOYER_PRIVATE_KEY", "")
    if not rpc_url or not key:
        raise RuntimeError("GLASSBOX_RPC_URL and SETTLER_PRIVATE_KEY (or DEPLOYER_PRIVATE_KEY) "
                           "must be set for --live — see .env.example")

    w3 = build_w3(rpc_url, key)
    handles = contract_handles(w3)
    indices = {name: next_decision_index(handles["reasoning_anchor"], agent_id)
               for name, agent_id in AGENT_IDS.items()}
    logger.info(f"[live] chain-seeded decision indices: {indices}")

    if run_round_fn is None:
        async def _seeded_run_round(market_id: str, agent_ids: dict[str, int]) -> dict[str, Any]:
            return await run_round(market_id, agent_ids, decision_indices=indices)
        run_round_fn = _seeded_run_round

    return SettlerService(
        run_round_fn=run_round_fn,
        dry_run=False,
        round_state=handles["round_state"],
        reasoning_anchor=handles["reasoning_anchor"],
        executor=handles["executor"],
    )


# ---------- round record persistence ----------

async def run_and_record(market_id: str, live: bool = False,
                         record_dir: Path | str = _DEFAULT_RECORD_DIR,
                         run_round_fn=None, price_fn=None) -> Path:
    """One round end-to-end, persisted so `settle` can grade it later.

    The reference price is read FIRST, at round start — minutes before the commits
    actually land (the LLM phase sits in between); the record carries its observation
    timestamp so the drift is visible, and both ends of the grade use the same source.
    A live round refuses to start without a live price (a commit that can never be
    graded is theater), while a dry-run records the honest `unavailable` tag and
    proceeds — paper rounds stay runnable offline.
    """
    price_fn = price_fn or mantle_spot_price
    price_at_commit = await price_fn(market_id)
    if live and not price_at_commit.get("available"):
        raise RuntimeError("refusing a LIVE round: commit-time price read is unavailable "
                           f"({price_at_commit.get('_provenance')}) — it could never be settled")

    # Persist the reference price BEFORE the first tx: a live round that crashes
    # mid-flight (RPC timeout, NotSettler revert, Ctrl-C during the LLM phase) must
    # still leave the price needed to grade it — otherwise the on-chain round is
    # born ungradeable, the exact thing the price gate above exists to prevent.
    record_dir = Path(record_dir)
    record_dir.mkdir(parents=True, exist_ok=True)
    inflight = record_dir / f"inflight_{int(time.time())}_{market_id.replace('/', '-')}.json"
    inflight.write_text(json.dumps({
        "market_id": market_id,
        "live": live,
        "price_at_commit": price_at_commit,
        "settlement": None,
        "status": "in_flight",  # round_id unknown until openRound mines
    }, indent=2, default=str))

    if live:
        service = _build_live_service(run_round_fn=run_round_fn)
    else:
        if run_round_fn is None:
            from agents.orchestrator.main import run_round as run_round_fn
        service = SettlerService(run_round_fn=run_round_fn, dry_run=True)

    outcome = await service.run_one(market_id, AGENT_IDS)

    record = {
        **asdict(outcome),
        "live": live,
        "price_at_commit": price_at_commit,
        "settlement": None,  # filled by settle_from_record
    }
    # Live ids are chain-sequential from 0; dry-run ids are random pseudo-ids —
    # separate namespaces so a paper round can never clobber a real round's record,
    # and never overwrite: the record is the only copy of the commit-time price.
    prefix = "round" if live else "dry_round"
    path = record_dir / f"{prefix}_{outcome.round_id}.json"
    if path.exists():
        raise RuntimeError(f"{path} already exists — refusing to overwrite a round record "
                           "(it is an audit artifact and the only copy of the commit-time price)")
    path.write_text(json.dumps(record, indent=2, default=str))
    inflight.unlink(missing_ok=True)
    logger.info(f"[live] round {outcome.round_id} recorded -> {path}")
    return path


async def settle_from_record(record_path: Path | str, live: bool = False,
                             price_fn=None) -> dict[str, Any]:
    """Grade a recorded round: ALREADY-COMMITTED signals vs two independent price reads.

    Refuses to grade unless BOTH price reads are live — `resolve_outcome` on an
    invented price would be a fabricated outcome. With --live it also writes the
    realized bps on-chain via RoundState.settle (settler-gated, requires Pending).
    """
    record_path = Path(record_path)
    record = json.loads(record_path.read_text())

    if live and not record.get("live"):
        raise RuntimeError("refusing --live settle: this is a dry-run record "
                           "(record['live'] is false) — its pseudo round_id was never "
                           "opened on-chain, so RoundState.settle would either revert or "
                           "write a fabricated outcome onto someone else's round")
    if record.get("settlement") is not None:
        raise RuntimeError(
            f"round {record['round_id']} is already settled "
            f"(settled_onchain={record['settlement']['settled_onchain']}) — refusing to "
            "overwrite the existing settlement; delete the settlement block from the "
            "record manually if you really mean to re-grade")

    price_at_commit = record.get("price_at_commit") or {}
    if not price_at_commit.get("available"):
        raise RuntimeError("cannot settle: the recorded commit-time price was not live "
                           f"({price_at_commit.get('_provenance')})")
    price_now = await (price_fn or mantle_spot_price)(record["market_id"])
    if not price_now.get("available"):
        raise RuntimeError("cannot settle: settlement-time price read is unavailable "
                           f"({price_now.get('_provenance')}) — retry later, never fake it")

    outcome = RoundOutcome(
        round_id=record["round_id"],
        market_id=record["market_id"],
        ensemble_signal=record["ensemble_signal"],
        ensemble_confidence=record["ensemble_confidence"],
        trade_executed=record["trade_executed"],
        rejection_reason=record["rejection_reason"],
        agent_records=record["agent_records"],
    )
    service = SettlerService(run_round_fn=None, dry_run=not live)  # type: ignore[arg-type]
    scores = service.settle_round(outcome, price_at_commit["price"], price_now["price"])
    realized_bps = service.resolve_outcome(price_at_commit["price"], price_now["price"])

    settled_onchain = False
    if live:
        rpc_url = os.environ.get("GLASSBOX_RPC_URL", "")
        key = os.environ.get("SETTLER_PRIVATE_KEY") or os.environ.get("DEPLOYER_PRIVATE_KEY", "")
        if not rpc_url or not key:
            raise RuntimeError("GLASSBOX_RPC_URL and a settler key are required for --live settle")
        w3 = build_w3(rpc_url, key)
        round_state = contract_handles(w3)["round_state"]
        tx = round_state.functions.settle(record["round_id"], realized_bps).transact()
        w3.eth.wait_for_transaction_receipt(tx)
        settled_onchain = True
        logger.info(f"[live] RoundState.settle({record['round_id']}, {realized_bps}) mined")

    settlement = {
        "realized_move_bps": realized_bps,
        "price_at_settle": price_now,
        "scores": scores,
        "settled_onchain": settled_onchain,
    }
    record["settlement"] = settlement
    record_path.write_text(json.dumps(record, indent=2, default=str))
    return settlement


# ---------- CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Glass-Box live runner (dry-run by default)")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="run one decision round and persist the record")
    run_p.add_argument("--market", default="mETH/USDC")
    run_p.add_argument("--live", action="store_true",
                       help="sign real txs (needs GLASSBOX_RPC_URL + settler key + addresses)")

    settle_p = sub.add_parser("settle", help="grade a recorded round against a fresh price read")
    settle_p.add_argument("--record", required=True)
    settle_p.add_argument("--live", action="store_true",
                          help="also write realized bps on-chain via RoundState.settle")

    args = parser.parse_args()
    if args.command == "run":
        path = asyncio.run(run_and_record(args.market, live=args.live))
        print(path)
    else:
        settlement = asyncio.run(settle_from_record(args.record, live=args.live))
        print(json.dumps(settlement, indent=2, default=str))


if __name__ == "__main__":
    main()
