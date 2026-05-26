// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { GlassBoxRegistry } from "../src/GlassBoxRegistry.sol";
import { IGlassBoxAgent } from "../src/IGlassBoxAgent.sol";

contract MockAgent is IGlassBoxAgent {
    uint256 public immutable _id;
    constructor(uint256 id) { _id = id; }
    function agentId() external view returns (uint256) { return _id; }
    function decisionCount() external pure returns (uint256) { return 0; }
    function getDecision(uint256) external pure returns (Decision memory d) { return d; }
    function reasoningHash(uint256) external pure returns (bytes32) { return bytes32(0); }
}

contract BadAgent {
    // does not implement IGlassBoxAgent
}

contract GlassBoxRegistryTest is Test {
    GlassBoxRegistry internal registry;

    function setUp() public {
        registry = new GlassBoxRegistry();
    }

    function test_RegisterEmitsEventAndStores() public {
        MockAgent a = new MockAgent(42);
        registry.register(42, address(a));

        GlassBoxRegistry.Registration memory reg = registry.getRegistration(42);
        assertEq(reg.agentId, 42);
        assertEq(reg.agentContract, address(a));
        assertEq(registry.registrationsCount(), 1);
    }

    function test_RevertOnAgentIdMismatch() public {
        MockAgent a = new MockAgent(42);
        vm.expectRevert("agentId mismatch");
        registry.register(43, address(a));
    }

    function test_RevertOnNonInterface() public {
        BadAgent b = new BadAgent();
        vm.expectRevert(GlassBoxRegistry.NotInterface.selector);
        registry.register(1, address(b));
    }

    function test_RevertOnDoubleRegister() public {
        MockAgent a = new MockAgent(1);
        registry.register(1, address(a));
        vm.expectRevert(GlassBoxRegistry.AlreadyRegistered.selector);
        registry.register(1, address(a));
    }
}
