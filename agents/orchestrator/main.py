"""Glass-Box Alpha orchestrator.

Runs all 4 agents in parallel on a market signal, collects their decisions +
reasoning chains, commits reasoning hashes on-chain, and emits ensemble verdict.

Adapted from ECHO orchestrator — agent base class transfers; agent identities
(Chronos/DA/Web/Mood) and tools are project-specific.
"""
from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import anthropic
from dotenv import load_dotenv
from loguru import logger

if TYPE_CHECKING:
    from ..shared.base import GlassBoxAgent

load_dotenv()


async def run_round(market_id: str, agents: list["GlassBoxAgent"]) -> dict:
    """One full decision round: all agents reason in parallel."""
    results = await asyncio.gather(*[agent.reason(market_id) for agent in agents])

    payload = {
        "market_id": market_id,
        "agent_outputs": [],
    }

    for agent, (decision, chain) in zip(agents, results, strict=True):
        reasoning_hash = agent.reasoning_hash(chain)
        payload["agent_outputs"].append({
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "decision": decision.model_dump(),
            "reasoning_hash": reasoning_hash.hex(),
            "reasoning_chain": chain.model_dump(),
        })
        logger.info(f"[{agent.name}] decided {decision.kind.name} signal={decision.directional_signal:+.2f}")

    return payload


async def main() -> None:
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Agent IDs filled in after Day 2 mainnet mints.
    # from ..chronos.agent import Chronos
    # from ..devils_advocate.agent import DevilsAdvocate
    # from ..web.agent import Web
    # from ..mood.agent import Mood

    # agents = [
    #     Chronos(client, agent_id=0),
    #     DevilsAdvocate(client, agent_id=0),
    #     Web(client, agent_id=0),
    #     Mood(client, agent_id=0),
    # ]

    # result = await run_round("mETH/USDC", agents)
    # logger.info(result)
    logger.info("Orchestrator scaffold ready. Implement agents/{chronos,devils_advocate,web,mood}/agent.py next.")


if __name__ == "__main__":
    asyncio.run(main())
