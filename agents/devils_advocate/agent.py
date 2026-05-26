"""Devil's Advocate — contradiction / risk-frame agent.

Unlike the other three, Devil's Advocate reads the OUTPUTS of Chronos, Web,
and Mood and finds what's missing or under-considered. It's invoked after
the other agents complete.
"""
from __future__ import annotations

from typing import Any

from ..shared.base import GlassBoxAgent


class DevilsAdvocate(GlassBoxAgent):
    name = "devils_advocate"

    def __init__(self, *args, peer_outputs: dict[str, Any] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.peer_outputs = peer_outputs or {}

    def set_peer_outputs(self, peer_outputs: dict[str, Any]) -> None:
        """Called by orchestrator after Chronos/Web/Mood produce their reasoning."""
        self.peer_outputs = peer_outputs

    async def gather_context(self, market_id: str) -> dict[str, Any]:
        return {
            "market_id": market_id,
            "chronos_reasoning": self.peer_outputs.get("chronos", {}),
            "web_reasoning": self.peer_outputs.get("web", {}),
            "mood_reasoning": self.peer_outputs.get("mood", {}),
            "note": "Inject null into each agent's stated assumptions. Find what they did NOT consider.",
        }
