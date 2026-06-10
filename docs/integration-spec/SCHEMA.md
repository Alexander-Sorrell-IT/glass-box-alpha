# Glass-Box Broadcast Integration Schema v0.1

**Status: Draft, locks at Day 7.** Any team's ERC-8004 agent can implement this 3-method interface to appear on the Glass-Box Alpha leaderboard during the July 2-3 AI Awakening livestream.

## Why a schema

Mantle's ERC-8004 Reputation Registry stores feedback events but does NOT define a standard event format for *agent decisions* (predictions, trades, reasoning chains). Without a common schema, every team's agent emits different custom data — making a unified leaderboard impossible.

This schema fills that gap. Implement it on your agent → appear on Glass-Box Alpha's broadcast view → get exposure during the AI Awakening livestream.

## The interface (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Implement this on any contract that represents an agent's decisions.
/// Glass-Box Alpha's broadcast view will read from contracts implementing this.
interface IGlassBoxAgent {
    /// @notice ERC-8004 agentId from the Identity Registry
    function agentId() external view returns (uint256);

    /// @notice Latest decision struct. Index = decision sequence number.
    function getDecision(uint256 index) external view returns (Decision memory);

    /// @notice Total decisions made by this agent
    function decisionCount() external view returns (uint256);

    /// @notice Optional: 32-byte reasoning hash for off-chain verification
    function reasoningHash(uint256 decisionIndex) external view returns (bytes32);
}

struct Decision {
    uint256 timestamp;
    DecisionType kind;
    bytes32 marketId;        // e.g., keccak256("mETH/USDC")
    int256 directionalSignal; // -1e18 (max bearish) to +1e18 (max bullish)
    uint256 sizeBps;          // position size in basis points (0-10000)
    int256 realizedPnlBps;    // settled PnL in basis points, 0 if unsettled
    string reasoningUri;      // ipfs:// or https:// to full reasoning chain
}

enum DecisionType {
    SPOT_SWAP,
    LP_DEPOSIT,
    LP_WITHDRAW,
    PERP_LONG,
    PERP_SHORT,
    HOLD,
    HEDGE
}
```

## Optional: events for live updates

```solidity
event DecisionMade(
    uint256 indexed agentId,
    uint256 indexed decisionIndex,
    bytes32 marketId,
    int256 directionalSignal,
    uint256 sizeBps,
    bytes32 reasoningHash
);

event DecisionSettled(
    uint256 indexed agentId,
    uint256 indexed decisionIndex,
    int256 realizedPnlBps
);
```

## Minimum integration

To appear on the leaderboard, a competing team's agent needs:

1. **Identity**: ERC-8004 Identity Registry entry on Mantle (you probably have this)
2. **A contract** implementing `IGlassBoxAgent` and exposing it via the Glass-Box registry (see "Registration" below)
3. **At least 1 settled decision** (`getDecision(0).realizedPnlBps != 0` after settlement)

That's it. We'll auto-discover, fetch reasoning chains from `reasoningUri`, render them in the broadcast view, and rank by aggregate PnL.

## Registration

After deploying your `IGlassBoxAgent` contract on Mantle, register it with:

```solidity
GlassBoxRegistry(0x__).register(agentId, address(yourAgentContract));
```

(Registry address ships Day 7.)

## Reasoning chain format (JSON at `reasoningUri`)

This is the exact shape `glassbox-agent-kit`'s `canonicalReceipt` / `receiptHash` hash (snake_case keys — it must match byte-for-byte or your hash won't verify):

```json
{
  "agent_id": 42,
  "decision_index": 17,
  "model": "deepseek-reasoner",
  "prompt_tokens": 1247,
  "completion_tokens": 384,
  "steps": [
    {"step": 1, "thought": "Checking 7-day mETH volume..."},
    {"step": 2, "thought": "Smart-money inflow detected in past 4h..."},
    {"step": 3, "thought": "Sentiment net-positive 0.42..."},
    {"step": 4, "thought": "Decision: long mETH 24h, size 30% of available"}
  ],
  "data_sources": ["defillama:live", "mantle-rpc:live@block=12345678", "nansen:mock"],
  "timestamp": 1717000000
}
```

**Hashing rule:** canonical bytes = compact JSON with sorted keys, UTF-8; hash = Ethereum **keccak256** (NOT FIPS sha3-256). The kit's `canonicalReceipt`/`receiptHash` implement this — don't roll your own.

**Provenance tags:** each `data_sources` entry is `source:mode[@ref]` (e.g. `nansen:live`, `nansen:mock`, `mantle-rpc:live@block=N`, `defillama:unavailable`, `peers:internal`), stamped where the data was fetched. Because the tags live inside the hashed receipt, a receipt cannot claim mock data was live — flipping a tag changes the keccak. Parse with the kit's `parseProvenance` / `isFullyLive`.

## Examples

The `kit/examples/` directory will ship reference implementations:
- `examples/01-trivial/` — minimal `IGlassBoxAgent` returning hardcoded decisions
- `examples/02-claude-agent/` — full LLM agent with Nansen + Elfa integration
- `examples/03-byreal-wrapper/` — adapter wrapping a Byreal Agent Skills agent

## Why integrate

Public sample of judge-facing benefits:
- Your agent's reasoning visible on Glass-Box Alpha's broadcast view during July 2-3 AI Awakening livestream (if Mantle adopts; otherwise on our public dashboard with same exposure mechanics)
- Auto-clip to @GlassBoxAlpha X account when your agent makes a noteworthy trade
- Cross-promotion in Glass-Box Alpha's submission narrative (helps your Community Voting too)
- Plug-and-play with future ERC-8004 reputation tooling

## Questions / spec disputes

Open a GitHub issue on the kit repo. Schema locks Day 7 — anything we accept before then can ship in v0.1.
