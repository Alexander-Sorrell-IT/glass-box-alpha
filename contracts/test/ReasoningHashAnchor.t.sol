// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { ReasoningHashAnchor } from "../src/ReasoningHashAnchor.sol";

contract ReasoningHashAnchorTest is Test {
    ReasoningHashAnchor internal anchor;
    address internal alice = address(0xA11CE);

    function setUp() public {
        anchor = new ReasoningHashAnchor();
    }

    function test_CommitEmitsEventAndStores() public {
        vm.prank(alice);
        bytes32 hash = keccak256("agent-chronos-decision-0-reasoning-chain");
        anchor.commit(1, 0, hash);

        ReasoningHashAnchor.Commit memory c = anchor.getCommit(1, 0);
        assertEq(c.agentId, 1);
        assertEq(c.decisionIndex, 0);
        assertEq(c.reasoningHash, hash);
        assertEq(c.committer, alice);
        assertEq(anchor.commitsCount(), 1);
    }

    function test_RevertOnDoubleCommit() public {
        anchor.commit(1, 0, keccak256("first"));
        vm.expectRevert(ReasoningHashAnchor.AlreadyCommitted.selector);
        anchor.commit(1, 0, keccak256("second"));
    }

    function test_DifferentAgentsCanCommitSameDecisionIndex() public {
        anchor.commit(1, 0, keccak256("chronos"));
        anchor.commit(2, 0, keccak256("devils-advocate"));
        anchor.commit(3, 0, keccak256("web"));
        anchor.commit(4, 0, keccak256("mood"));
        assertEq(anchor.commitsCount(), 4);
    }

    function testFuzz_CommitRoundTrip(uint256 agentId, uint256 decisionIndex, bytes32 hash) public {
        vm.assume(agentId != 0); // contract uses 0 as "not committed" sentinel
        anchor.commit(agentId, decisionIndex, hash);
        assertEq(anchor.getCommit(agentId, decisionIndex).reasoningHash, hash);
    }
}
