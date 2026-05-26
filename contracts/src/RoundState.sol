// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { IGlassBoxAgent } from "./IGlassBoxAgent.sol";

/// Per-round state contract. One round per market signal: the orchestrator
/// opens a round, agents submit decisions, settler reports realized PnL,
/// reputation writes follow.
contract RoundState {
    enum RoundStatus { Open, Pending, Settled, Cancelled }

    struct AgentSubmission {
        uint256 agentId;
        IGlassBoxAgent.DecisionType kind;
        int256 directionalSignal;
        uint256 sizeBps;
        bytes32 reasoningHash;
        uint256 submittedAt;
    }

    struct Round {
        uint256 roundId;
        bytes32 marketId;
        address opener;
        uint256 openedAt;
        uint256 settledAt;
        RoundStatus status;
        int256 ensembleSignal;     // result of the Fold
        int256 realizedPnlBps;
        AgentSubmission[] submissions;
    }

    Round[] internal _rounds;
    address public immutable settler;

    event RoundOpened(uint256 indexed roundId, bytes32 indexed marketId, address opener);
    event SubmissionRecorded(uint256 indexed roundId, uint256 indexed agentId, bytes32 reasoningHash);
    event EnsembleComputed(uint256 indexed roundId, int256 ensembleSignal);
    event RoundSettled(uint256 indexed roundId, int256 realizedPnlBps);

    error NotSettler();
    error WrongStatus();

    modifier onlySettler() {
        if (msg.sender != settler) revert NotSettler();
        _;
    }

    constructor(address _settler) {
        settler = _settler == address(0) ? msg.sender : _settler;
    }

    function openRound(bytes32 marketId) external returns (uint256 roundId) {
        roundId = _rounds.length;
        _rounds.push();
        Round storage r = _rounds[roundId];
        r.roundId = roundId;
        r.marketId = marketId;
        r.opener = msg.sender;
        r.openedAt = block.timestamp;
        r.status = RoundStatus.Open;
        emit RoundOpened(roundId, marketId, msg.sender);
    }

    function recordSubmission(
        uint256 roundId,
        uint256 agentId,
        IGlassBoxAgent.DecisionType kind,
        int256 directionalSignal,
        uint256 sizeBps,
        bytes32 reasoningHash
    ) external {
        Round storage r = _rounds[roundId];
        if (r.status != RoundStatus.Open) revert WrongStatus();
        r.submissions.push(AgentSubmission({
            agentId: agentId,
            kind: kind,
            directionalSignal: directionalSignal,
            sizeBps: sizeBps,
            reasoningHash: reasoningHash,
            submittedAt: block.timestamp
        }));
        emit SubmissionRecorded(roundId, agentId, reasoningHash);
    }

    function setEnsemble(uint256 roundId, int256 ensembleSignal) external onlySettler {
        Round storage r = _rounds[roundId];
        if (r.status != RoundStatus.Open) revert WrongStatus();
        r.ensembleSignal = ensembleSignal;
        r.status = RoundStatus.Pending;
        emit EnsembleComputed(roundId, ensembleSignal);
    }

    function settle(uint256 roundId, int256 realizedPnlBps) external onlySettler {
        Round storage r = _rounds[roundId];
        if (r.status != RoundStatus.Pending) revert WrongStatus();
        r.realizedPnlBps = realizedPnlBps;
        r.settledAt = block.timestamp;
        r.status = RoundStatus.Settled;
        emit RoundSettled(roundId, realizedPnlBps);
    }

    function roundsCount() external view returns (uint256) {
        return _rounds.length;
    }

    function getRound(uint256 roundId) external view returns (
        bytes32 marketId,
        address opener,
        uint256 openedAt,
        uint256 settledAt,
        RoundStatus status,
        int256 ensembleSignal,
        int256 realizedPnlBps,
        uint256 submissionsCount
    ) {
        Round storage r = _rounds[roundId];
        return (
            r.marketId,
            r.opener,
            r.openedAt,
            r.settledAt,
            r.status,
            r.ensembleSignal,
            r.realizedPnlBps,
            r.submissions.length
        );
    }

    function getSubmission(uint256 roundId, uint256 index) external view returns (AgentSubmission memory) {
        return _rounds[roundId].submissions[index];
    }
}
