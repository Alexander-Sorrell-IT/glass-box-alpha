"""Shared types across all 4 Glass-Box Alpha agents.

Mirrors the on-chain IGlassBoxAgent.Decision struct so the agent layer and the
contract layer stay in sync.
"""
from __future__ import annotations

from enum import IntEnum
from typing import Literal

from pydantic import BaseModel, Field


class DecisionType(IntEnum):
    SPOT_SWAP = 0
    LP_DEPOSIT = 1
    LP_WITHDRAW = 2
    PERP_LONG = 3
    PERP_SHORT = 4
    HOLD = 5
    HEDGE = 6


class ReasoningStep(BaseModel):
    step: int
    thought: str


class Decision(BaseModel):
    agent_id: int
    decision_index: int
    timestamp: int
    kind: DecisionType
    market_id: str  # e.g., "mETH/USDC" — hashed to bytes32 on-chain
    directional_signal: float = Field(ge=-1.0, le=1.0)
    size_bps: int = Field(ge=0, le=10_000)
    confidence: float = Field(ge=0.0, le=1.0)
    realized_pnl_bps: int = 0
    reasoning_uri: str = ""


class ReasoningChain(BaseModel):
    agent_id: int
    decision_index: int
    model: str
    prompt_tokens: int
    completion_tokens: int
    steps: list[ReasoningStep]
    data_sources: list[str]
    timestamp: int


AgentName = Literal["chronos", "devils_advocate", "web", "mood"]
