// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Anchors agent reasoning-chain hashes on-chain — the Reasoning Receipt primitive.
/// Each agent calls commit() with the keccak256 of its canonical reasoning receipt
/// BEFORE the market settles. Later, anyone recomputes the hash from the published
/// JSON via verify() — edit one byte and it stops matching. Verifiable, not "trust me."
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

    /// Recompute the receipt hash from the raw canonical JSON and compare it to the
    /// stored on-chain commit. Powers the in-browser tamper test: pass the published
    /// reasoning bytes and `ok` is true; flip a single byte and `ok` flips to false.
    /// `canonicalJson` must be the exact bytes the agent hashed (see
    /// agents/shared/base.py canonical_receipt / frontend/lib/receipt.ts).
    function verify(uint256 agentId, uint256 decisionIndex, bytes calldata canonicalJson)
        external
        view
        returns (bool ok, bytes32 stored, bytes32 recomputed)
    {
        uint256 idx = commitIndexOf[agentId][decisionIndex];
        require(idx != 0, "no commit");
        stored = commits[idx - 1].reasoningHash;
        recomputed = keccak256(canonicalJson);
        ok = (recomputed == stored);
    }
}
