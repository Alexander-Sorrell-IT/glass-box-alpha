"""Base class for the 4 Glass-Box Alpha agents.

Adapted from the ECHO 4-agent orchestrator. ~25-30% of ECHO code carries over
(this base + streaming + orchestrator).

LLM backend: DeepSeek via OpenAI-compatible API. Default model is
`deepseek-v4-pro` (R1) which streams reasoning_content separately from
content — Glass-Box transparency comes for free.
"""
from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import AsyncIterator

from eth_utils import keccak  # real Ethereum keccak256 — must match Solidity + viem
from loguru import logger
from openai import AsyncOpenAI

from .ensemble import SYSTEM_PROMPTS
from .types import AgentName, Decision, DecisionType, ReasoningChain, ReasoningStep


class GlassBoxAgent(ABC):
    """Base class for Chronos, Devil's Advocate, Web, and Mood."""

    name: AgentName
    agent_id: int  # ERC-8004 token ID — set after Day 4 mint
    model: str

    def __init__(self, client: AsyncOpenAI, agent_id: int, model: str | None = None) -> None:
        self.client = client
        self.agent_id = agent_id
        self.model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self._decision_index = 0

    def system_prompt(self) -> str:
        """Agent's reasoning-frame system prompt. Override for custom behavior."""
        return SYSTEM_PROMPTS[self.name]

    @abstractmethod
    async def gather_context(self, market_id: str) -> dict:
        """Pull agent-specific data from external sources (Nansen, Elfa, etc)."""

    async def reason(self, market_id: str) -> tuple[Decision, ReasoningChain]:
        """One full decision cycle: gather context → reason → emit decision + reasoning chain."""
        context = await self.gather_context(market_id)
        # Provenance the agent declared for its inputs (source + live/mock/unavailable).
        # Pulled out before prompting so it never pollutes the LLM context, then committed
        # into the receipt's data_sources — making each input's liveness tamper-evident.
        provenance = context.pop("_provenance", None)
        user_prompt = self._build_prompt(market_id, context)

        steps: list[ReasoningStep] = []
        final_text = ""
        prompt_tokens = 0
        completion_tokens = 0

        async for event in self._stream_reasoning(user_prompt):
            match event:
                case {"kind": "step", "data": ReasoningStep() as step}:
                    steps.append(step)
                    logger.info(f"[{self.name}] step {step.step}: {step.thought[:80]}")
                case {"kind": "final", "data": str() as text}:
                    final_text = text
                case {"kind": "usage", "in": int() as in_tok, "out": int() as out_tok}:
                    prompt_tokens = in_tok
                    completion_tokens = out_tok

        # Prefer the DECISION line in the final answer (content); fall back to the tail of the
        # reasoning if the model only stated it there. Either way, default to a neutral HOLD.
        reasoning_text = "\n".join(s.thought for s in steps)
        decision = (
            self._parse_decision(market_id, final_text)
            or self._parse_decision(market_id, reasoning_text)
            or self._default_decision(market_id)
        )

        chain = ReasoningChain(
            agent_id=self.agent_id,
            decision_index=self._decision_index,
            model=self.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            steps=steps,
            # Deterministic (sorted + deduped) so the same decision hashes identically
            # run-to-run regardless of gather order. An agent that declares no provenance
            # commits ["undeclared:unknown"] — never raw context keys, which would read as
            # legitimate live sources and let a receipt imply liveness it never declared.
            data_sources=(sorted(set(provenance)) if provenance else ["undeclared:unknown"]),
            timestamp=int(time.time()),
        )
        self._decision_index += 1
        return decision, chain

    @staticmethod
    def canonical_receipt(chain: ReasoningChain) -> bytes:
        """The exact, language-neutral bytes that get sealed into the on-chain receipt.

        Deterministic JSON: keys sorted, compact separators, UTF-8, integer-only
        numbers (ReasoningChain carries no floats — token counts, steps, timestamps
        are all ints). The frontend reproduces these bytes verbatim to recompute the
        keccak256 in-browser, and the contract's verify() re-hashes the same bytes, so
        this spec MUST stay byte-for-byte in lockstep with frontend/lib/receipt.ts.
        """
        return json.dumps(
            chain.model_dump(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

    @staticmethod
    def reasoning_hash(chain: ReasoningChain) -> bytes:
        """Ethereum keccak256 of the canonical receipt — byte-identical to an in-browser
        viem.keccak256 recompute and to the contract's keccak256(canonicalJson). This is
        what makes the 'recompute it yourself' verifiability claim literally true."""
        return keccak(GlassBoxAgent.canonical_receipt(chain))

    def _build_prompt(self, market_id: str, context: dict) -> str:
        return (
            f"Market: {market_id}\n"
            f"Context: {json.dumps(context, indent=2, default=str)}\n\n"
            "Reason step-by-step. Then the VERY LAST line of your answer must be exactly one "
            "DECISION line with your own concrete numbers — no angle brackets, no extra words "
            "after it. Format (this is an EXAMPLE; substitute your real values):\n"
            "DECISION: PERP_LONG signal=0.42 size_bps=2500 confidence=0.70\n"
            "Valid actions: SPOT_SWAP, LP_DEPOSIT, LP_WITHDRAW, PERP_LONG, PERP_SHORT, HOLD, HEDGE. "
            "signal in -1..1, size_bps in 0..10000, confidence in 0..1. "
            "For HOLD/HEDGE use size_bps=0 but still give a real confidence."
        )

    async def _stream_reasoning(self, user_prompt: str) -> AsyncIterator[dict]:
        """Stream DeepSeek response.

        For deepseek-v4-pro, `delta.reasoning_content` carries the CoT and
        `delta.content` carries the final answer (visible to user). We emit
        reasoning steps from reasoning_content and the final text from content.

        For deepseek-v4-flash (or non-reasoner models), reasoning_content is None
        so we synthesize steps by splitting `content` on paragraph breaks.
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            max_tokens=8192,  # reasoner burns thousands on CoT — too small and it truncates before the DECISION line
            stream_options={"include_usage": True},
        )

        reasoning_buffer = ""
        content_buffer = ""
        step_num = 0
        has_native_reasoning = False

        async for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                rc = getattr(delta, "reasoning_content", None)
                if rc:
                    has_native_reasoning = True
                    reasoning_buffer += rc
                    while "\n\n" in reasoning_buffer:
                        chunk_text, reasoning_buffer = reasoning_buffer.split("\n\n", 1)
                        if chunk_text.strip():
                            step_num += 1
                            yield {
                                "kind": "step",
                                "data": ReasoningStep(step=step_num, thought=chunk_text.strip()),
                            }
                if delta.content:
                    content_buffer += delta.content
                    if not has_native_reasoning:
                        while "\n\n" in content_buffer:
                            chunk_text, content_buffer = content_buffer.split("\n\n", 1)
                            if chunk_text.strip():
                                step_num += 1
                                yield {
                                    "kind": "step",
                                    "data": ReasoningStep(step=step_num, thought=chunk_text.strip()),
                                }

            if chunk.usage:
                yield {
                    "kind": "usage",
                    "in": chunk.usage.prompt_tokens,
                    "out": chunk.usage.completion_tokens,
                }

        if reasoning_buffer.strip():
            step_num += 1
            yield {
                "kind": "step",
                "data": ReasoningStep(step=step_num, thought=reasoning_buffer.strip()),
            }
        if content_buffer.strip():
            if not has_native_reasoning:
                step_num += 1
                yield {
                    "kind": "step",
                    "data": ReasoningStep(step=step_num, thought=content_buffer.strip()),
                }
            yield {"kind": "final", "data": content_buffer.strip()}

    def _default_decision(self, market_id: str) -> Decision:
        """Neutral fallback when no parseable DECISION line was produced."""
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

    def _parse_decision(self, market_id: str, text: str) -> Decision | None:
        """Extract a structured Decision from `text`, or None if none is present.

        Tolerant by design: scans each `DECISION:` marker from last to first (the real
        answer comes after any prompt-template echo), reads kind + numeric
        signal/size_bps/confidence in any order, clamps to valid ranges. A marker with a
        non-numeric `signal` (e.g. the echoed `signal=<-1..1>` template) is skipped, and
        a marker missing a numeric signal entirely yields None so the caller can fall back.
        """
        if not text:
            return None

        for marker in reversed(list(re.finditer(r"DECISION:\s*([\s\S]{0,200})", text))):
            window = marker.group(1)
            sig_m = re.search(r"signal\s*=\s*(-?\d+(?:\.\d+)?)", window)
            if not sig_m:
                continue  # template echo or malformed — try an earlier marker

            kind = DecisionType.HOLD
            for tok in re.findall(r"[A-Z_]{3,}", window):
                if tok in DecisionType.__members__:
                    kind = DecisionType[tok]
                    break

            def _grab(key: str, lo: float, hi: float, default: float) -> float:
                m = re.search(rf"{key}\s*=\s*(-?\d+(?:\.\d+)?)", window)
                return min(hi, max(lo, float(m.group(1)))) if m else default

            signal = min(1.0, max(-1.0, float(sig_m.group(1))))
            size = int(_grab("size_bps", 0.0, 10000.0, 0.0))
            conf = _grab("confidence", 0.0, 1.0, 0.0)
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
        return None
