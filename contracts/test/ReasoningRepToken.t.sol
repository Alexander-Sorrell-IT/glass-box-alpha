// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { ReasoningRepToken } from "../src/ReasoningRepToken.sol";

contract ReasoningRepTokenTest is Test {
    ReasoningRepToken internal token;
    address internal minter = address(0xBEEF);
    address internal alice = address(0xA11CE);

    function setUp() public {
        token = new ReasoningRepToken(minter);
    }

    function test_MintIncreasesTier0Balance() public {
        vm.prank(minter);
        token.mint(alice, 5);
        assertEq(token.balanceOf(alice, 0), 5);
        assertEq(token.totalByTier(0), 5);
    }

    function test_RevertOnNonMinterMint() public {
        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.NotMinter.selector);
        token.mint(alice, 1);
    }

    function test_CombineRollsTenToOne() public {
        vm.prank(minter);
        token.mint(alice, 10);
        vm.prank(alice);
        token.combine(0, 1); // burn 10 tier-0 -> 1 tier-1
        assertEq(token.balanceOf(alice, 0), 0);
        assertEq(token.balanceOf(alice, 1), 1);
    }

    function test_FullCascadeToTranscendent() public {
        // Need 1000 tier-0 to reach 1 tier-3
        vm.prank(minter);
        token.mint(alice, 1000);

        vm.startPrank(alice);
        token.combine(0, 100); // 1000 -> 100 tier-1
        token.combine(1, 10);  // 100 -> 10 tier-2
        token.combine(2, 1);   // 10 -> 1 tier-3
        vm.stopPrank();

        assertEq(token.balanceOf(alice, 0), 0);
        assertEq(token.balanceOf(alice, 1), 0);
        assertEq(token.balanceOf(alice, 2), 0);
        assertEq(token.balanceOf(alice, 3), 1);
    }

    function test_RevertCombineAtMaxTier() public {
        vm.prank(minter);
        token.mint(alice, 10_000);
        vm.startPrank(alice);
        token.combine(0, 1000);
        token.combine(1, 100);
        token.combine(2, 10);
        vm.expectRevert(ReasoningRepToken.AtMaxTier.selector);
        token.combine(3, 1);
        vm.stopPrank();
    }

    function test_RevertCombineInsufficient() public {
        vm.prank(minter);
        token.mint(alice, 5);
        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.InsufficientBalance.selector);
        token.combine(0, 1); // needs 10
    }

    function test_TotalBalanceWeightedByTier() public {
        vm.prank(minter);
        token.mint(alice, 1000); // 1000 tier-0

        vm.startPrank(alice);
        token.combine(0, 50);  // 500 tier-0 -> 50 tier-1. Balance: 500 tier-0, 50 tier-1
        token.combine(1, 5);   // 50 tier-1 -> 5 tier-2. Balance: 500 tier-0, 0 tier-1, 5 tier-2
        vm.stopPrank();

        // weighted total = 500*1 + 0*10 + 5*100 + 0*1000 = 1000
        assertEq(token.totalBalanceOf(alice), 1000);
    }

    function test_NonTransferable() public {
        vm.prank(minter);
        token.mint(alice, 10);

        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.NonTransferable.selector);
        token.transfer(address(0xCAFE), 1);

        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.NonTransferable.selector);
        token.transferFrom(alice, address(0xCAFE), 1);

        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.NonTransferable.selector);
        token.approve(address(0xCAFE), 1);
    }

    function test_SetMinterOwnerOnly() public {
        address newMinter = address(0xFEED);
        token.setMinter(newMinter);
        assertEq(token.minter(), newMinter);

        vm.prank(alice);
        vm.expectRevert(ReasoningRepToken.NotOwner.selector);
        token.setMinter(alice);
    }
}
