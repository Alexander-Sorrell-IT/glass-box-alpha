"""Settler service — the off-chain orchestration loop.

Flow per round:
  1. Open a round on RoundState (assigns round_id).
  2. Run the orchestrator: 4 agents reason, Fold ensemble computes final signal.
  3. For each agent, call ReasoningHashAnchor.commit(agent_id, decision_idx, reasoning_hash).
  4. Call RoundState.recordSubmission for each agent.
  5. Call RoundState.setEnsemble with the Fold signal.
  6. Risk-gate: if signal passes confidence + DA-veto checks, call AgentExecutor.executeTrade.
  7. After settlement window, compute realized PnL, call RoundState.settle + AgentExecutor.recordLoss (if loss).
  8. Write ERC-8004 Reputation Registry feedback per agent based on outcome.

Decoupled from main.py orchestrator so each layer can be tested independently.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class RiskConfig:
    """All risk knobs in one place. Mirrors AgentExecutor.sol constants."""
    max_trade_bps: int = 500            # 5% per trade
    drawdown_limit_bps: int = 2000      # 20% portfolio halt
    min_confidence_bps: int = 5000      # 50% confidence floor
    bps_denominator: int = 10_000

    def validate_decision(self, ensemble_signal: float, ensemble_conf: float,
                          da_signal: float, da_conf: float) -> tuple[bool, str]:
        """Returns (is_safe_to_execute, reason). Mirrors on-chain checks for fail-fast.

        Devil's Advocate veto convention: if DA decided HOLD with signal=0 AND
        conf >= 0.5 (i.e. DA actively recommended no-trade), we treat it as a veto.
        """
        if abs(da_signal) < 0.01 and da_conf >= 0.5:
            return False, "Devil's Advocate veto"

        conf_bps = int(ensemble_conf * self.bps_denominator)
        if conf_bps < self.min_confidence_bps:
            return False, f"confidence {conf_bps}bps < floor {self.min_confidence_bps}bps"

        if abs(ensemble_signal) < 0.05:
            return False, "signal magnitude < 0.05 — too weak"

        return True, "ok"

    def signal_to_size_bps(self, ensemble_signal: float, ensemble_conf: float) -> int:
        """Map (signal, confidence) -> position size in bps, capped at MAX_TRADE_BPS.

        Risk-weighted sizing: size = max_size * |signal| * confidence.
        """
        raw_size = self.max_trade_bps * abs(ensemble_signal) * ensemble_conf
        return min(self.max_trade_bps, max(1, int(raw_size)))


@dataclass
class RoundOutcome:
    round_id: int
    market_id: str
    ensemble_signal: float
    ensemble_confidence: float
    trade_executed: bool
    rejection_reason: str | None
    agent_records: list[dict[str, Any]]


class SettlerService:
    """Coordinates one full decision round end-to-end.

    Designed for dependency injection: pass in a w3 client (web3.py) + contract
    handles + the orchestrator's run_round function. That way the same class
    drives Sepolia testnet and Mantle Mainnet without code change.

    For Day 3-7 we run with `dry_run=True` (no on-chain calls — just logs the
    payload). Day 7+ flip dry_run=False once contracts are deployed on Sepolia.
    """

    def __init__(
        self,
        run_round_fn,
        risk: RiskConfig | None = None,
        dry_run: bool = True,
        round_state=None,        # web3 contract handle, optional in dry_run
        reasoning_anchor=None,
        executor=None,
    ) -> None:
        self.run_round_fn = run_round_fn
        self.risk = risk or RiskConfig()
        self.dry_run = dry_run
        self.round_state = round_state
        self.reasoning_anchor = reasoning_anchor
        self.executor = executor

    async def run_one(self, market_id: str, agent_ids: dict[str, int]) -> RoundOutcome:
        """Open a round, run agents, commit reasoning hashes, gate trade by risk."""
        round_id = self._open_round(market_id)
        logger.info(f"[settler] opened round {round_id} for {market_id}")

        payload = await self.run_round_fn(market_id, agent_ids)
        ensemble_signal = payload["ensemble"]["directional_signal"]
        ensemble_conf = payload["ensemble"]["confidence"]

        # Pull Devil's Advocate output for veto check.
        da_decision = next(
            a["decision"] for a in payload["agents"] if a["name"] == "devils_advocate"
        )
        da_signal = da_decision["directional_signal"]
        da_conf = da_decision["confidence"]

        # Commit each reasoning hash on-chain.
        for agent in payload["agents"]:
            self._commit_reasoning_hash(
                agent_id=agent["agent_id"],
                decision_idx=agent["decision"]["decision_index"],
                reasoning_hash_hex=agent["reasoning_hash"],
            )
            self._record_submission(
                round_id=round_id,
                agent_id=agent["agent_id"],
                decision=agent["decision"],
                reasoning_hash_hex=agent["reasoning_hash"],
            )

        # Set ensemble on-chain.
        self._set_ensemble(round_id, ensemble_signal)

        # Risk-gate the trade.
        is_safe, reason = self.risk.validate_decision(
            ensemble_signal, ensemble_conf, da_signal, da_conf
        )
        trade_executed = False
        if is_safe:
            size_bps = self.risk.signal_to_size_bps(ensemble_signal, ensemble_conf)
            tokens = self._resolve_tokens(market_id, ensemble_signal)
            trade_executed = self._execute_trade(
                round_id=round_id,
                ensemble_signal=ensemble_signal,
                ensemble_conf=ensemble_conf,
                size_bps=size_bps,
                token_in=tokens["in"],
                token_out=tokens["out"],
            )
            logger.info(f"[settler] round {round_id} trade executed: {trade_executed}, size={size_bps}bps")
        else:
            logger.info(f"[settler] round {round_id} trade rejected: {reason}")

        return RoundOutcome(
            round_id=round_id,
            market_id=market_id,
            ensemble_signal=ensemble_signal,
            ensemble_confidence=ensemble_conf,
            trade_executed=trade_executed,
            rejection_reason=None if trade_executed else (reason if not is_safe else "execution failed"),
            agent_records=payload["agents"],
        )

    # ---------- On-chain shims (dry-run safe) ----------

    def _open_round(self, market_id: str) -> int:
        if self.dry_run or self.round_state is None:
            return int.from_bytes(os.urandom(4), "big") % 10_000  # pseudo round_id for dry-run
        market_hash = self._market_hash(market_id)
        tx = self.round_state.functions.openRound(market_hash).transact()
        receipt = self.round_state.web3.eth.wait_for_transaction_receipt(tx)
        # parse RoundOpened event for round_id
        event = self.round_state.events.RoundOpened().process_receipt(receipt)[0]
        return event["args"]["roundId"]

    def _commit_reasoning_hash(self, agent_id: int, decision_idx: int, reasoning_hash_hex: str) -> None:
        if self.dry_run or self.reasoning_anchor is None:
            logger.debug(f"[dry-run] commit agentId={agent_id} idx={decision_idx} hash={reasoning_hash_hex[:16]}…")
            return
        rh_bytes = bytes.fromhex(reasoning_hash_hex)
        self.reasoning_anchor.functions.commit(agent_id, decision_idx, rh_bytes).transact()

    def _record_submission(self, round_id: int, agent_id: int, decision: dict, reasoning_hash_hex: str) -> None:
        if self.dry_run or self.round_state is None:
            logger.debug(f"[dry-run] recordSubmission round={round_id} agent={agent_id} signal={decision['directional_signal']:+.2f}")
            return
        self.round_state.functions.recordSubmission(
            round_id,
            agent_id,
            decision["kind"],
            int(decision["directional_signal"] * 1e18),
            decision["size_bps"],
            bytes.fromhex(reasoning_hash_hex),
        ).transact()

    def _set_ensemble(self, round_id: int, ensemble_signal: float) -> None:
        if self.dry_run or self.round_state is None:
            logger.debug(f"[dry-run] setEnsemble round={round_id} signal={ensemble_signal:+.3f}")
            return
        self.round_state.functions.setEnsemble(round_id, int(ensemble_signal * 1e18)).transact()

    def _execute_trade(self, round_id: int, ensemble_signal: float, ensemble_conf: float,
                       size_bps: int, token_in: str, token_out: str) -> bool:
        if self.dry_run or self.executor is None:
            logger.debug(f"[dry-run] executeTrade round={round_id} {token_in}->{token_out} size_bps={size_bps}")
            return True
        try:
            self.executor.functions.executeTrade(
                round_id,
                int(ensemble_signal * 1e4),
                int(ensemble_conf * 1e4),
                False,                       # daVetoed (already gated client-side)
                token_in,
                token_out,
                size_bps,
                0,                           # minAmountOut — slippage handled in router adapter
            ).transact()
            return True
        except Exception as exc:
            logger.warning(f"[settler] trade execution failed: {exc}")
            return False

    @staticmethod
    def _market_hash(market_id: str) -> bytes:
        import hashlib
        return hashlib.sha3_256(market_id.encode()).digest()

    @staticmethod
    def _resolve_tokens(market_id: str, signal: float) -> dict[str, str]:
        """Map "BASE/QUOTE" + signed signal -> swap direction.

        Bullish signal (>0): buy BASE with QUOTE (token_in=QUOTE, token_out=BASE).
        Bearish (<0): sell BASE for QUOTE (token_in=BASE, token_out=QUOTE).

        Token addresses placeholder — overridden via env per chain.
        """
        base_sym, quote_sym = market_id.split("/")
        # Will be replaced with real Mantle token addresses post-deploy.
        token_map = {
            "USDC": os.environ.get("MANTLE_USDC", "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9"),
            "mETH": os.environ.get("MANTLE_METH", "0xcDA86A272531e8640cD7F1a92c01839911B90bb0"),
            "MNT":  os.environ.get("MANTLE_MNT",  "0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8"),
            "USDY": os.environ.get("MANTLE_USDY", "0x5bE26527e817998A7206475496fDE1E68957c5A6"),
            "fBTC": os.environ.get("MANTLE_FBTC", "0xC96dE26018A54D51c097160568752c4E3BD6C364"),
        }
        if signal >= 0:
            return {"in": token_map[quote_sym], "out": token_map[base_sym]}
        return {"in": token_map[base_sym], "out": token_map[quote_sym]}
