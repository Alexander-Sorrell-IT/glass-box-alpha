"""Golden-vector tests pinning the on-chain reasoning receipt.

The entire "recompute the hash yourself" verifiability claim rests on ONE fact:
the bytes the agent hashes off-chain are keccak256'd identically to (a) the Solidity
contract and (b) an in-browser viem.keccak256. These tests freeze the canonical
byte spec and the algorithm so a regression to FIPS sha3-256 (the old bug) — or any
drift in the serialization — fails loudly. frontend/lib/receipt.ts MUST reproduce
the exact `canonical bytes` string below.
"""
from __future__ import annotations

import hashlib

from eth_utils import keccak

from agents.shared.base import GlassBoxAgent
from agents.shared.types import ReasoningChain, ReasoningStep

# A fixed receipt — change these and the golden hash below must change in lockstep.
GOLDEN_CHAIN = ReasoningChain(
    agent_id=1,
    decision_index=0,
    model="deepseek-reasoner",
    prompt_tokens=100,
    completion_tokens=200,
    steps=[ReasoningStep(step=1, thought="net inflow +$1.2M"), ReasoningStep(step=2, thought="bullish")],
    data_sources=["nansen"],
    timestamp=1700000000,
)
GOLDEN_CANONICAL = (
    '{"agent_id":1,"completion_tokens":200,"data_sources":["nansen"],"decision_index":0,'
    '"model":"deepseek-reasoner","prompt_tokens":100,'
    '"steps":[{"step":1,"thought":"net inflow +$1.2M"},{"step":2,"thought":"bullish"}],'
    '"timestamp":1700000000}'
)
GOLDEN_KECCAK = "0xf8aed1ad2a6bcdf567b73fb7fe2814f93d83f7ee1ffdea7d6e70eb663f55b82a"

# Second golden vector — PRODUCTION provenance format ("source:mode[@ref]") in data_sources,
# the shape real agents now emit (the first vector uses a legacy bare entry). Pins byte-parity
# for that format across Python / Solidity / browser / kit. Values frozen from this impl.
GOLDEN_CHAIN_V2 = ReasoningChain(
    agent_id=1,
    decision_index=0,
    model="deepseek-reasoner",
    prompt_tokens=100,
    completion_tokens=200,
    steps=[ReasoningStep(step=1, thought="net inflow +$1.2M"), ReasoningStep(step=2, thought="bullish")],
    data_sources=["mantle-rpc:live@block=12345", "nansen:mock"],
    timestamp=1700000000,
)
GOLDEN_CANONICAL_V2 = (
    '{"agent_id":1,"completion_tokens":200,'
    '"data_sources":["mantle-rpc:live@block=12345","nansen:mock"],"decision_index":0,'
    '"model":"deepseek-reasoner","prompt_tokens":100,'
    '"steps":[{"step":1,"thought":"net inflow +$1.2M"},{"step":2,"thought":"bullish"}],'
    '"timestamp":1700000000}'
)
GOLDEN_KECCAK_V2 = "0xdad4f919a0eb10033dde1cc748cc45f72cd1f7b77e8062d599108aeef6cee33e"


def test_provenance_format_canonical_is_frozen():
    """The production source:mode[@ref] provenance format serializes byte-identically."""
    assert GlassBoxAgent.canonical_receipt(GOLDEN_CHAIN_V2).decode("utf-8") == GOLDEN_CANONICAL_V2


def test_provenance_format_keccak_golden():
    assert "0x" + GlassBoxAgent.reasoning_hash(GOLDEN_CHAIN_V2).hex() == GOLDEN_KECCAK_V2


def test_canonical_receipt_is_frozen():
    """The exact bytes the frontend must reproduce verbatim."""
    assert GlassBoxAgent.canonical_receipt(GOLDEN_CHAIN).decode("utf-8") == GOLDEN_CANONICAL


def test_reasoning_hash_golden_keccak():
    """The frozen keccak256 of the canonical receipt — the on-chain commit value."""
    assert "0x" + GlassBoxAgent.reasoning_hash(GOLDEN_CHAIN).hex() == GOLDEN_KECCAK


def test_reasoning_hash_is_keccak_not_fips_sha3():
    """Guard against regressing to hashlib.sha3_256 (FIPS SHA3), which is a DIFFERENT
    digest from Ethereum keccak256 and would never match the contract or viem."""
    canonical = GlassBoxAgent.canonical_receipt(GOLDEN_CHAIN)
    assert GlassBoxAgent.reasoning_hash(GOLDEN_CHAIN) == keccak(canonical)
    assert GlassBoxAgent.reasoning_hash(GOLDEN_CHAIN) != hashlib.sha3_256(canonical).digest()


def test_market_hash_matches_solidity_keccak():
    """settler market hash must equal Solidity keccak256(bytes("mETH/USDC")).
    Frozen value verified against `cast keccak 'mETH/USDC'`."""
    from agents.settler.service import SettlerService

    expected = "0x0c1c31c542b7172613dd74fdf5b47a1788f87c3e8e3a1d7cf3965ec715e1847b"
    assert "0x" + SettlerService._market_hash("mETH/USDC").hex() == expected


def test_canonical_receipt_deterministic_and_sorted():
    a = GlassBoxAgent.canonical_receipt(GOLDEN_CHAIN)
    b = GlassBoxAgent.canonical_receipt(GOLDEN_CHAIN)
    assert a == b
    # keys appear in sorted order (agent_id before completion_tokens before ...)
    s = a.decode()
    assert s.index('"agent_id"') < s.index('"completion_tokens"') < s.index('"timestamp"')
