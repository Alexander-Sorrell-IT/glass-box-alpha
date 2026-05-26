// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Interface other teams' agents implement to appear on the Glass-Box Alpha
/// broadcast leaderboard. See docs/integration-spec/SCHEMA.md.
interface IGlassBoxAgent {
    enum DecisionType { SPOT_SWAP, LP_DEPOSIT, LP_WITHDRAW, PERP_LONG, PERP_SHORT, HOLD, HEDGE }

    struct Decision {
        uint256 timestamp;
        DecisionType kind;
        bytes32 marketId;
        int256 directionalSignal;
        uint256 sizeBps;
        int256 realizedPnlBps;
        string reasoningUri;
    }

    function agentId() external view returns (uint256);
    function decisionCount() external view returns (uint256);
    function getDecision(uint256 index) external view returns (Decision memory);
    function reasoningHash(uint256 decisionIndex) external view returns (bytes32);

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
}
