// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { HumanArena } from "../src/HumanArena.sol";
import { RoundState } from "../src/RoundState.sol";
import { IGlassBoxAgent } from "../src/IGlassBoxAgent.sol";

contract HumanArenaTest is Test {
    RoundState internal rs;
    HumanArena internal arena;

    address internal alice = address(0xA11CE);
    address internal bob = address(0xB0B);
    bytes32 internal MARKET = keccak256("mETH/USDC");

    // This test contract is the settler, so it can drive setEnsemble/settle.
    function setUp() public {
        rs = new RoundState(address(this));
        arena = new HumanArena(address(rs));
    }

    function _openWithChronos(int256 chronosSignal, uint256 chronosSizeBps) internal returns (uint256 id) {
        id = rs.openRound(MARKET);
        // Chronos = agentId 1, submission index 0
        rs.recordSubmission(id, 1, IGlassBoxAgent.DecisionType.PERP_LONG, chronosSignal, chronosSizeBps, keccak256("chronos"));
    }

    function _settle(uint256 id, int256 pnlBps) internal {
        rs.setEnsemble(id, 1);
        rs.settle(id, pnlBps);
    }

    // ---- the shared scoring rule ----

    function test_ScoreRuleSignAndWeight() public view {
        // bull call, full conviction, market +100bps => +100
        assertEq(arena.score(1, 10_000, 100), 100);
        // bear call, full conviction, market +100bps => -100 (wrong way)
        assertEq(arena.score(-1, 10_000, 100), -100);
        // bull, half conviction, +100bps => +50
        assertEq(arena.score(1, 5_000, 100), 50);
        // hold / zero direction => 0 regardless of pnl
        assertEq(arena.score(0, 10_000, 100), 0);
        // any direction with zero weight => 0
        assertEq(arena.score(1, 0, 100), 0);
        // sign(direction) is normalized: a large signed signal scores like +1
        assertEq(arena.score(62e16, 10_000, 100), 100);
        // weightBps is clamped to BPS — an out-of-bounds agent sizeBps cannot exceed
        // realized PnL or break the fair-fight symmetry.
        assertEq(arena.score(1, 20_000, 100), 100);   // clamps to 10_000
        assertEq(arena.score(1, 50_000, 100), 100);
    }

    function test_ConstructorRejectsNonContract() public {
        vm.expectRevert(HumanArena.NotAContract.selector);
        new HumanArena(address(0));
        vm.expectRevert(HumanArena.NotAContract.selector);
        new HumanArena(address(0xDEAD)); // EOA, no code
    }

    // ---- play guards ----

    function test_SubmitCallStoresAndEmits() public {
        uint256 id = _openWithChronos(62e16, 2500);
        bytes32 thesis = keccak256("inflows look real");

        vm.expectEmit(true, true, false, true);
        emit HumanArena.CallSubmitted(id, alice, int8(1), uint16(8000), thesis);

        vm.prank(alice);
        arena.submitCall(id, 1, 8000, thesis);

        HumanArena.Call memory c = arena.getCall(id, alice);
        assertEq(c.direction, 1);
        assertEq(c.convictionBps, 8000);
        assertEq(c.reasoningHash, thesis);
        assertTrue(c.exists);
        assertEq(arena.playerCount(id), 1);
        assertEq(arena.playerAt(id, 0), alice);
    }

    function test_RevertBadDirection() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.prank(alice);
        vm.expectRevert(HumanArena.BadDirection.selector);
        arena.submitCall(id, 2, 5000, bytes32(0));
    }

    function test_RevertBadConviction() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.startPrank(alice);
        vm.expectRevert(HumanArena.BadConviction.selector);
        arena.submitCall(id, 1, 0, bytes32(0));
        vm.expectRevert(HumanArena.BadConviction.selector);
        arena.submitCall(id, 1, 10_001, bytes32(0));
        vm.stopPrank();
    }

    function test_RevertCallOnSettledRound() public {
        uint256 id = _openWithChronos(62e16, 2500);
        _settle(id, 50);
        vm.prank(alice);
        vm.expectRevert(HumanArena.RoundNotOpen.selector);
        arena.submitCall(id, 1, 5000, bytes32(0));
    }

    function test_RevertDoubleCall() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.startPrank(alice);
        arena.submitCall(id, 1, 5000, bytes32(0));
        vm.expectRevert(HumanArena.AlreadyCalled.selector);
        arena.submitCall(id, -1, 5000, bytes32(0));
        vm.stopPrank();
    }

    function test_RevertScoreBeforeSettle() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.prank(alice);
        arena.submitCall(id, 1, 5000, bytes32(0));
        vm.expectRevert(HumanArena.NotSettled.selector);
        arena.humanScore(id, alice);
    }

    function test_RevertScoreNoCall() public {
        uint256 id = _openWithChronos(62e16, 2500);
        _settle(id, 50);
        vm.expectRevert(HumanArena.NoCall.selector);
        arena.humanScore(id, alice);
    }

    // ---- the money path: human beats Chronos ----

    function test_HumanBeatsChronos() public {
        // Chronos goes long with 25% conviction; alice goes bull with 80%.
        uint256 id = _openWithChronos(62e16, 2500);
        vm.prank(alice);
        arena.submitCall(id, 1, 8000, keccak256("i'm more sure"));

        // Market moves +120bps. Both called the direction right, but alice
        // had higher conviction, so she scores more under the same rule.
        _settle(id, 120);

        (bool beat, int256 human, int256 agent, uint256 agentId) = arena.beatAgent(id, alice, 0);
        assertEq(agentId, 1);
        assertEq(human, 96);  // 120 * 8000/10000
        assertEq(agent, 30);  // 120 * 2500/10000
        assertTrue(beat);
    }

    function test_HumanLosesToChronos_WrongDirection() public {
        uint256 id = _openWithChronos(62e16, 2500); // Chronos bullish
        vm.prank(bob);
        arena.submitCall(id, -1, 10_000, bytes32(0)); // bob bearish, max conviction

        _settle(id, 80); // market up => bob wrong

        (bool beat, int256 human, int256 agent,) = arena.beatAgent(id, bob, 0);
        assertEq(human, -80); // full conviction, wrong way
        assertEq(agent, 20);  // 80 * 2500/10000
        assertFalse(beat);
    }

    function test_AgentScoreReadsSubmission() public {
        uint256 id = _openWithChronos(-50e16, 4000); // Chronos bearish, 40% size
        _settle(id, -150); // market down 150bps => bearish call wins
        (uint256 agentId, int256 s) = arena.agentScore(id, 0);
        assertEq(agentId, 1);
        assertEq(s, 60); // sign(-) * (-150) * 4000/10000 = +60
    }

    function test_HumanScoreNegativePnL() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.prank(alice);
        arena.submitCall(id, 1, 10_000, bytes32(0)); // bull, full conviction
        _settle(id, -90);                            // market down => bull call loses
        assertEq(arena.humanScore(id, alice), -90);
    }

    function test_ZeroPnLResultsInTie() public {
        uint256 id = _openWithChronos(62e16, 2500);
        vm.prank(alice);
        arena.submitCall(id, 1, 8000, bytes32(0));
        _settle(id, 0);                              // flat market => everyone scores 0
        (bool beat, int256 human, int256 agent,) = arena.beatAgent(id, alice, 0);
        assertEq(human, 0);
        assertEq(agent, 0);
        assertFalse(beat);                           // a tie is not a win (strict >)
    }
}
