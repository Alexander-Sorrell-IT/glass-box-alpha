// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { RoundState } from "../src/RoundState.sol";
import { IGlassBoxAgent } from "../src/IGlassBoxAgent.sol";

contract RoundStateTest is Test {
    RoundState internal rs;
    address internal alice = address(0xA11CE);
    bytes32 internal MARKET = keccak256("mETH/USDC");

    function setUp() public {
        rs = new RoundState(address(this));
    }

    function test_OpenRoundCreatesRecord() public {
        vm.prank(alice);
        uint256 id = rs.openRound(MARKET);
        assertEq(id, 0);
        assertEq(rs.roundsCount(), 1);

        (bytes32 m,, , , RoundState.RoundStatus status,,, uint256 subCount) = rs.getRound(0);
        assertEq(m, MARKET);
        assertEq(uint256(status), uint256(RoundState.RoundStatus.Open));
        assertEq(subCount, 0);
    }

    function test_RecordSubmissionAppendsAndEmits() public {
        uint256 id = rs.openRound(MARKET);
        bytes32 rh = keccak256("chronos-reasoning");

        rs.recordSubmission(id, 1, IGlassBoxAgent.DecisionType.PERP_LONG, 7e17, 2500, rh);
        rs.recordSubmission(id, 2, IGlassBoxAgent.DecisionType.HOLD, 0, 0, keccak256("da-reasoning"));

        (, , , , , , , uint256 subCount) = rs.getRound(id);
        assertEq(subCount, 2);

        RoundState.AgentSubmission memory s = rs.getSubmission(id, 0);
        assertEq(s.agentId, 1);
        assertEq(s.reasoningHash, rh);
    }

    function test_FullLifecycle() public {
        uint256 id = rs.openRound(MARKET);
        rs.recordSubmission(id, 1, IGlassBoxAgent.DecisionType.PERP_LONG, 5e17, 1000, keccak256("r"));
        rs.setEnsemble(id, 3e17);
        rs.settle(id, 42); // +0.42%

        (, , , uint256 settledAt, RoundState.RoundStatus status, int256 ensemble, int256 pnl,) = rs.getRound(id);
        assertEq(uint256(status), uint256(RoundState.RoundStatus.Settled));
        assertEq(ensemble, 3e17);
        assertEq(pnl, 42);
        assertGt(settledAt, 0);
    }

    function test_RevertSettleBeforeEnsemble() public {
        uint256 id = rs.openRound(MARKET);
        vm.expectRevert(RoundState.WrongStatus.selector);
        rs.settle(id, 100);
    }

    function test_RevertNonSettlerSettings() public {
        uint256 id = rs.openRound(MARKET);
        vm.prank(alice);
        vm.expectRevert(RoundState.NotSettler.selector);
        rs.setEnsemble(id, 0);
    }

    function test_RevertNonSettlerSubmission() public {
        // Anyone could previously forge agent submissions — now gated to the settler.
        uint256 id = rs.openRound(MARKET);
        vm.prank(alice);
        vm.expectRevert(RoundState.NotSettler.selector);
        rs.recordSubmission(id, 1, IGlassBoxAgent.DecisionType.PERP_LONG, 5e17, 1000, keccak256("forged"));
    }

    function test_RevertSettleTwice() public {
        uint256 id = rs.openRound(MARKET);
        rs.setEnsemble(id, 1);
        rs.settle(id, 42);
        // Round is now Settled; a second settle must revert (status no longer Pending).
        vm.expectRevert(RoundState.WrongStatus.selector);
        rs.settle(id, 99);
    }

    function test_GetSubmissionOutOfBounds() public {
        uint256 id = rs.openRound(MARKET);
        vm.expectRevert(); // array index OOB panic
        rs.getSubmission(id, 0);
    }
}
