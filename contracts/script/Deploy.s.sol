// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Script } from "forge-std/Script.sol";
import { ReasoningHashAnchor } from "../src/ReasoningHashAnchor.sol";
import { GlassBoxRegistry } from "../src/GlassBoxRegistry.sol";

/// Deploys ReasoningHashAnchor + GlassBoxRegistry to Mantle (mainnet or sepolia).
///
/// Usage:
///   # Sepolia first (recommended)
///   forge script script/Deploy.s.sol --rpc-url mantle_sepolia --broadcast --verify
///
///   # Mainnet after sepolia is green
///   forge script script/Deploy.s.sol --rpc-url mantle_mainnet --broadcast --verify
contract Deploy is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(deployerKey);

        ReasoningHashAnchor anchor = new ReasoningHashAnchor();
        GlassBoxRegistry registry = new GlassBoxRegistry();

        vm.stopBroadcast();

        // Print for CONTRACTS.md update
        // forge cleartext logging keeps these visible after --broadcast
        // solhint-disable no-console
        // console.log("ReasoningHashAnchor:", address(anchor));
        // console.log("GlassBoxRegistry:", address(registry));
    }
}
