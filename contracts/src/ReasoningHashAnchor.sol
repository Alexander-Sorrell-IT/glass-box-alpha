// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Anchors agent reasoning chain hashes on-chain. The Verity primitive.
/// Each agent calls commit() with the keccak256 of its full reasoning chain JSON
/// before publishing the JSON off-chain. Later, anyone can verify the off-chain
/// JSON wasn't tampered with by recomputing the hash.
contract ReasoningHashAnchor {
    struct Commit {
        uint256 agentId;
        uint256 decisionIndex;
        bytes32 reasoningHash;
        uint256 timestamp;
        address committer;
    }

    Commit[] public commits;

    mapping(uint256 => mapping(uint256 => uint256)) public commitIndexOf;

    event ReasoningCommitted(
        uint256 indexed agentId,
        uint256 indexed decisionIndex,
        bytes32 reasoningHash,
        address committer
    );

    error AlreadyCommitted();

    function commit(uint256 agentId, uint256 decisionIndex, bytes32 reasoningHash) external returns (uint256 commitIdx) {
        if (commitIndexOf[agentId][decisionIndex] != 0) revert AlreadyCommitted();

        commits.push(Commit({
            agentId: agentId,
            decisionIndex: decisionIndex,
            reasoningHash: reasoningHash,
            timestamp: block.timestamp,
            committer: msg.sender
        }));
        commitIdx = commits.length;
        commitIndexOf[agentId][decisionIndex] = commitIdx;

        emit ReasoningCommitted(agentId, decisionIndex, reasoningHash, msg.sender);
    }

    function commitsCount() external view returns (uint256) {
        return commits.length;
    }

    function getCommit(uint256 agentId, uint256 decisionIndex) external view returns (Commit memory) {
        uint256 idx = commitIndexOf[agentId][decisionIndex];
        require(idx != 0, "no commit");
        return commits[idx - 1];
    }
}
