"""Glass-Box Alpha orchestrator.

Runs all 4 agents on a market signal, collects decisions + reasoning chains,
applies the Fold ensemble, returns final call + per-agent receipts ready for
on-chain commit.

Flow:
  1. Chronos, Web, Mood reason in parallel (gather context + LLM call)
  2. Devil's Advocate is fed their outputs, then reasons
  3. Fold ensemble combines all 4 signals into final call + confidence
  4. Return payload with reasoning hashes ready for ReasoningHashAnchor.commit
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI

from ..chronos.agent import Chronos
from ..devils_advocate.agent import DevilsAdvocate
from ..mood.agent import Mood
from ..shared.ensemble import fold_ensemble
from ..shared.types import Decision, ReasoningChain
from ..web.agent import Web

load_dotenv()


async def run_round(market_id: str, agent_ids: dict[str, int],
                    decision_indices: dict[str, int] | None = None) -> dict[str, Any]:
    """One full decision round on a market.

    Args:
        market_id: e.g. "mETH/USDC"
        agent_ids: mapping of agent name -> ERC-8004 agent_id (from Day 2 mints)
        decision_indices: optional per-agent starting decision_index, seeded from the
            anchor by the live runner so a process restart can't recommit an index the
            chain already holds (AlreadyCommitted revert). Defaults to 0 for dry-run.

    Returns:
        payload with per-agent decisions, reasoning hashes, fold ensemble result.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY is not set. Copy .env.example to .env and add your key "
            "(get one free at https://platform.deepseek.com)."
        )
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )

    idx = decision_indices or {}
    chronos = Chronos(client, agent_id=agent_ids["chronos"],
                      decision_index=idx.get("chronos", 0))
    web = Web(client, agent_id=agent_ids["web"], decision_index=idx.get("web", 0))
    mood = Mood(client, agent_id=agent_ids["mood"], decision_index=idx.get("mood", 0))
    devils_advocate = DevilsAdvocate(client, agent_id=agent_ids["devils_advocate"],
                                     decision_index=idx.get("devils_advocate", 0))

    # 1. Run Chronos / Web / Mood in parallel
    logger.info(f"[round] market={market_id} — launching Chronos/Web/Mood in parallel")
    parallel_results = await asyncio.gather(
        chronos.reason(market_id),
        web.reason(market_id),
        mood.reason(market_id),
    )
    chronos_decision, chronos_chain = parallel_results[0]
    web_decision, web_chain = parallel_results[1]
    mood_decision, mood_chain = parallel_results[2]

    # 2. Feed peer outputs to Devil's Advocate
    devils_advocate.set_peer_outputs({
        "chronos": {"decision": chronos_decision.model_dump(), "reasoning": chronos_chain.model_dump()},
        "web": {"decision": web_decision.model_dump(), "reasoning": web_chain.model_dump()},
        "mood": {"decision": mood_decision.model_dump(), "reasoning": mood_chain.model_dump()},
    })
    logger.info(f"[round] running Devil's Advocate with peer context")
    da_decision, da_chain = await devils_advocate.reason(market_id)

    # 3. Fold ensemble
    final_signal, confidence = fold_ensemble(
        chronos_signal=chronos_decision.directional_signal,
        da_signal=da_decision.directional_signal,
        web_signal=web_decision.directional_signal,
        mood_signal=mood_decision.directional_signal,
        chronos_conf=chronos_decision.confidence,
        da_conf=da_decision.confidence,
        web_conf=web_decision.confidence,
        mood_conf=mood_decision.confidence,
    )
    logger.info(f"[round] Fold ensemble: signal={final_signal:+.3f} confidence={confidence:.3f}")

    # 4. Compute reasoning hashes for on-chain commit
    return {
        "market_id": market_id,
        "ensemble": {
            "directional_signal": final_signal,
            "confidence": confidence,
        },
        "agents": [
            _agent_record("chronos", chronos, chronos_decision, chronos_chain),
            _agent_record("web", web, web_decision, web_chain),
            _agent_record("mood", mood, mood_decision, mood_chain),
            _agent_record("devils_advocate", devils_advocate, da_decision, da_chain),
        ],
    }


def _agent_record(name: str, agent: Any, decision: Decision, chain: ReasoningChain) -> dict[str, Any]:
    return {
        "name": name,
        "agent_id": agent.agent_id,
        "decision": decision.model_dump(),
        "reasoning_hash": agent.reasoning_hash(chain).hex(),
        "reasoning_chain": chain.model_dump(),
    }


async def main() -> None:
    # Placeholder agent_ids — replace with real Mantle mainnet token IDs after Day 2 mints.
    agent_ids = {"chronos": 1, "web": 2, "mood": 3, "devils_advocate": 4}
    result = await run_round("mETH/USDC", agent_ids)
    import json
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
