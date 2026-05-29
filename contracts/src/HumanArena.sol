// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Minimal read surface of RoundState that the arena needs. Kept as a local
/// interface so HumanArena stays decoupled from RoundState's storage layout.
interface IRoundState {
    function getRound(uint256 roundId) external view returns (
        bytes32 marketId,
        address opener,
        uint256 openedAt,
        uint256 settledAt,
        uint8 status,            // 0 Open · 1 Pending · 2 Settled · 3 Cancelled
        int256 ensembleSignal,
        int256 realizedPnlBps,
        uint256 submissionsCount
    );
    function getSubmission(uint256 roundId, uint256 index) external view returns (
        uint256 agentId,
        uint8 kind,
        int256 directionalSignal,
        uint256 sizeBps,
        bytes32 reasoningHash,
        uint256 submittedAt
    );
}

/// The HUMAN side of the "AI vs Human" arena — the piece that makes the
/// hackathon's namesake real instead of a label.
///
/// Anyone can submit a directional call (bull/bear + conviction) on an OPEN
/// round. No capital required: you predict, you're scored. An optional
/// reasoning hash lets a human anchor their thesis exactly like an agent does,
/// so the glass box is symmetric.
///
/// The win/lose result is graded by the SAME deterministic rule applied to the
/// agents, against the round's realized PnL. Only `submitCall` costs gas — every
/// "did I beat Chronos?" read is a gasless view. That keeps the viral loop free
/// to play and free to check.
contract HumanArena {
    IRoundState public immutable rounds;

    uint8 private constant STATUS_OPEN = 0;
    uint8 private constant STATUS_SETTLED = 2;
    uint256 private constant BPS = 10_000;

    struct Call {
        int8 direction;        // +1 bull, -1 bear
        uint16 convictionBps;  // 1..10000 — skin-in-the-game weight
        bytes32 reasoningHash; // optional thesis anchor, 0x0 if none
        uint64 submittedAt;
        bool exists;
    }

    mapping(uint256 => mapping(address => Call)) private _calls; // roundId => player => call
    mapping(uint256 => address[]) private _players;             // roundId => players (for keyless leaderboard reads)

    event CallSubmitted(
        uint256 indexed roundId,
        address indexed player,
        int8 direction,
        uint16 convictionBps,
        bytes32 reasoningHash
    );

    error BadDirection();
    error BadConviction();
    error RoundNotOpen();
    error AlreadyCalled();
    error NoCall();
    error NotSettled();
    error NotAContract();

    constructor(address roundState) {
        // Guard against deploying against a wrong/empty address — the pointer is
        // immutable, so a misconfigured deploy would brick every view permanently.
        if (roundState.code.length == 0) revert NotAContract();
        rounds = IRoundState(roundState);
    }

    // --------------------------------------------------------------------- //
    // Play (the only state-changing, gas-costing path)
    // --------------------------------------------------------------------- //

    /// Submit a directional call on an open round. One call per address per round.
    function submitCall(uint256 roundId, int8 direction, uint16 convictionBps, bytes32 reasoningHash) external {
        if (direction != 1 && direction != -1) revert BadDirection();
        if (convictionBps == 0 || convictionBps > BPS) revert BadConviction();

        (, , , , uint8 status, , , ) = rounds.getRound(roundId);
        if (status != STATUS_OPEN) revert RoundNotOpen();
        if (_calls[roundId][msg.sender].exists) revert AlreadyCalled();

        _calls[roundId][msg.sender] = Call({
            direction: direction,
            convictionBps: convictionBps,
            reasoningHash: reasoningHash,
            submittedAt: uint64(block.timestamp),
            exists: true
        });
        _players[roundId].push(msg.sender);

        emit CallSubmitted(roundId, msg.sender, direction, convictionBps, reasoningHash);
    }

    // --------------------------------------------------------------------- //
    // The shared scoring rule — applied identically to humans and agents.
    // --------------------------------------------------------------------- //

    /// score = sign(direction) · realizedPnlBps · weightBps / 10000
    /// A pure function so the equal-footing claim is auditable in one place.
    function score(int256 direction, uint256 weightBps, int256 realizedPnlBps) public pure returns (int256) {
        if (direction == 0 || weightBps == 0) return 0;
        // Agent sizeBps comes from RoundState (which does not bound it); cap to the
        // same ceiling humans face so neither side can exceed realized PnL — keeps
        // the "same rule, fair fight" guarantee and prevents an int256 overflow.
        if (weightBps > BPS) weightBps = BPS;
        int256 dir = direction > 0 ? int256(1) : int256(-1);
        return (dir * realizedPnlBps * int256(weightBps)) / int256(BPS);
    }

    // --------------------------------------------------------------------- //
    // Gasless reads — the viral "did I win?" surface
    // --------------------------------------------------------------------- //

    function getCall(uint256 roundId, address player) external view returns (Call memory) {
        return _calls[roundId][player];
    }

    function playerCount(uint256 roundId) external view returns (uint256) {
        return _players[roundId].length;
    }

    function playerAt(uint256 roundId, uint256 i) external view returns (address) {
        return _players[roundId][i];
    }

    /// A human player's score for a settled round.
    function humanScore(uint256 roundId, address player) public view returns (int256) {
        Call memory c = _calls[roundId][player];
        if (!c.exists) revert NoCall();
        (, , , , uint8 status, , int256 pnl, ) = rounds.getRound(roundId);
        if (status != STATUS_SETTLED) revert NotSettled();
        return score(int256(c.direction), c.convictionBps, pnl);
    }

    /// An agent's score under the SAME rule, derived from its on-chain submission.
    function agentScore(uint256 roundId, uint256 submissionIndex) public view returns (uint256 agentId, int256 s) {
        (, , , , uint8 status, , int256 pnl, ) = rounds.getRound(roundId);
        if (status != STATUS_SETTLED) revert NotSettled();
        (uint256 aid, , int256 dirSignal, uint256 sizeBps, , ) = rounds.getSubmission(roundId, submissionIndex);
        return (aid, score(dirSignal, sizeBps, pnl));
    }

    /// The money read: did `player` beat the agent at `submissionIndex` this round?
    function beatAgent(uint256 roundId, address player, uint256 submissionIndex)
        external
        view
        returns (bool beat, int256 human, int256 agent, uint256 agentId)
    {
        human = humanScore(roundId, player);
        (agentId, agent) = agentScore(roundId, submissionIndex);
        beat = human > agent;
    }
}
