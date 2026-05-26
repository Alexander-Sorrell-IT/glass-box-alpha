"""Base class for the 4 Glass-Box Alpha agents.

Adapted from the ECHO 4-agent orchestrator. ~25-30% of ECHO code carries over
(this base + streaming + orchestrator). Agent prompts + tools + market data
adapters are all new.
"""
from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import AsyncIterator

import anthropic
from loguru import logger

from .types import AgentName, Decision, DecisionType, ReasoningChain, ReasoningStep


class GlassBoxAgent(ABC):
    """Base class for Chronos, Devil's Advocate, Web, and Mood."""

    name: AgentName
    agent_id: int  # ERC-8004 token ID — set after Day 2 mint
    model: str = "claude-sonnet-4-6"

    def __init__(self, client: anthropic.AsyncAnthropic, agent_id: int) -> None:
        self.client = client
        self.agent_id = agent_id
        self._decision_index = 0

    @abstractmethod
    def system_prompt(self) -> str:
        """Agent-specific system prompt defining personality + analysis frame."""

    @abstractmethod
    async def gather_context(self, market_id: str) -> dict:
        """Pull agent-specific data from external sources (Nansen, Elfa, etc)."""

    async def reason(self, market_id: str) -> tuple[Decision, ReasoningChain]:
        """One full decision cycle: gather context → reason → emit decision + reasoning chain."""
        context = await self.gather_context(market_id)
        prompt = self._build_prompt(market_id, context)

        steps: list[ReasoningStep] = []
        async for step in self._stream_reasoning(prompt):
            steps.append(step)
            logger.info(f"[{self.name}] step {step.step}: {step.thought[:80]}")

        final_step = steps[-1]
        decision = self._parse_decision(market_id, final_step.thought)

        chain = ReasoningChain(
            agent_id=self.agent_id,
            decision_index=self._decision_index,
            model=self.model,
            prompt_tokens=0,  # filled by stream wrapper
            completion_tokens=0,
            steps=steps,
            data_sources=list(context.keys()),
            timestamp=int(time.time()),
        )
        self._decision_index += 1
        return decision, chain

    @staticmethod
    def reasoning_hash(chain: ReasoningChain) -> bytes:
        """keccak-equivalent: sha3-256 of canonical JSON. Match against on-chain commit."""
        canonical = json.dumps(chain.model_dump(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha3_256(canonical.encode()).digest()

    def _build_prompt(self, market_id: str, context: dict) -> str:
        return (
            f"Market: {market_id}\n"
            f"Context: {json.dumps(context, indent=2)}\n\n"
            "Reason step-by-step. End with a single line:\n"
            "DECISION: <SPOT_SWAP|LP_DEPOSIT|LP_WITHDRAW|PERP_LONG|PERP_SHORT|HOLD|HEDGE> "
            "signal=<-1..1> size_bps=<0..10000> confidence=<0..1>"
        )

    async def _stream_reasoning(self, prompt: str) -> AsyncIterator[ReasoningStep]:
        """Stream Claude's response, emitting one ReasoningStep per sentence/paragraph break."""
        step_num = 0
        buffer = ""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt(),
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for delta in stream.text_stream:
                buffer += delta
                while "\n\n" in buffer:
                    chunk, buffer = buffer.split("\n\n", 1)
                    step_num += 1
                    yield ReasoningStep(step=step_num, thought=chunk.strip())
            if buffer.strip():
                step_num += 1
                yield ReasoningStep(step=step_num, thought=buffer.strip())

    def _parse_decision(self, market_id: str, final_thought: str) -> Decision:
        line = next(
            (ln for ln in final_thought.splitlines() if ln.strip().startswith("DECISION:")),
            None,
        )
        if line is None:
            return Decision(
                agent_id=self.agent_id,
                decision_index=self._decision_index,
                timestamp=int(time.time()),
                kind=DecisionType.HOLD,
                market_id=market_id,
                directional_signal=0.0,
                size_bps=0,
                confidence=0.0,
            )

        parts = line.replace("DECISION:", "").strip().split()
        kind = DecisionType[parts[0]]
        signal = float(next(p for p in parts if p.startswith("signal=")).split("=")[1])
        size = int(next(p for p in parts if p.startswith("size_bps=")).split("=")[1])
        conf = float(next(p for p in parts if p.startswith("confidence=")).split("=")[1])

        return Decision(
            agent_id=self.agent_id,
            decision_index=self._decision_index,
            timestamp=int(time.time()),
            kind=kind,
            market_id=market_id,
            directional_signal=signal,
            size_bps=size,
            confidence=conf,
        )
