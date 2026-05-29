// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { Deploy } from "../script/Deploy.s.sol";

/// Asserts the core deploy script actually wires the contracts together — in
/// particular that HumanArena's immutable RoundState pointer is the freshly
/// deployed RoundState (a misconfigured pointer would brick the arena).
contract DeployTest is Test {
    function test_DeployWiresHumanArenaToRoundState() public {
        // Standard test private key; settler defaults to its derived address.
        vm.setEnv("DEPLOYER_PRIVATE_KEY", "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d");

        Deploy d = new Deploy();
        d.run();

        assertTrue(address(d.anchor()) != address(0), "anchor");
        assertTrue(address(d.registry()) != address(0), "registry");
        assertTrue(address(d.roundState()) != address(0), "roundState");
        assertTrue(address(d.repToken()) != address(0), "repToken");
        assertTrue(address(d.humanArena()) != address(0), "humanArena");

        // The wiring invariant: the arena points at the deployed RoundState.
        assertEq(address(d.humanArena().rounds()), address(d.roundState()));
    }
}
