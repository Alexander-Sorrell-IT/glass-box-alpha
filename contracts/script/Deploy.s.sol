// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Script, console2 } from "forge-std/Script.sol";
import { ReasoningHashAnchor } from "../src/ReasoningHashAnchor.sol";
import { GlassBoxRegistry } from "../src/GlassBoxRegistry.sol";
import { RoundState } from "../src/RoundState.sol";
import { ReasoningRepToken } from "../src/ReasoningRepToken.sol";
import { HumanArena } from "../src/HumanArena.sol";

/// Deploys the Glass-Box Alpha round + human-arena path to Mantle (mainnet or sepolia).
///
/// Order matters: RoundState must exist before HumanArena (immutable dependency,
/// guarded by a code-size check in HumanArena's constructor). The settler/minter
/// default to the deployer; set SETTLER_ADDRESS to point them at the settler service.
///
/// AgentExecutor + MerchantMoeAdapter deploy separately — they need the live
/// MerchantMoe LB router + seed-token addresses, so they are not wired here.
///
/// Usage:
///   forge script script/Deploy.s.sol --rpc-url mantle_sepolia --broadcast --verify   # Sepolia first
///   forge script script/Deploy.s.sol --rpc-url mantle_mainnet --broadcast --verify   # Mainnet after
contract Deploy is Script {
    // Exposed so a test (and post-run tooling) can read + assert wiring.
    ReasoningHashAnchor public anchor;
    GlassBoxRegistry public registry;
    RoundState public roundState;
    ReasoningRepToken public repToken;
    HumanArena public humanArena;

    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address settler = vm.envOr("SETTLER_ADDRESS", vm.addr(deployerKey));

        vm.startBroadcast(deployerKey);

        anchor = new ReasoningHashAnchor();
        registry = new GlassBoxRegistry();
        roundState = new RoundState(settler);
        repToken = new ReasoningRepToken(settler);
        humanArena = new HumanArena(address(roundState)); // guarded: roundState now has code

        vm.stopBroadcast();

        console2.log("ReasoningHashAnchor:", address(anchor));
        console2.log("GlassBoxRegistry:  ", address(registry));
        console2.log("RoundState:        ", address(roundState));
        console2.log("ReasoningRepToken: ", address(repToken));
        console2.log("HumanArena:        ", address(humanArena));
        console2.log("settler/minter:    ", settler);
    }
}
