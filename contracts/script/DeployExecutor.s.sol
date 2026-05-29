// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Script, console2 } from "forge-std/Script.sol";
import { MerchantMoeAdapter } from "../src/MerchantMoeAdapter.sol";
import { AgentExecutor } from "../src/AgentExecutor.sol";

/// Deploys the trade-execution path: MerchantMoeAdapter (wraps the live Merchant
/// Moe Liquidity Book router) then AgentExecutor seeded with trading capital.
/// Separate from Deploy.s.sol because it needs LIVE addresses that only exist on
/// the target network — author now, run Day-7/Day-14.
///
/// Required env:
///   DEPLOYER_PRIVATE_KEY  - deployer
///   MANTLE_LB_ROUTER      - Merchant Moe Liquidity Book router on the target chain
///   SEED_TOKEN            - seed token (e.g. USDC) address
///   SEED_AMOUNT           - seed amount in token decimals
/// Optional:
///   LB_BIN_STEP (default 20) · LB_DEADLINE_WINDOW (default 300)
///
/// Usage:
///   forge script script/DeployExecutor.s.sol --rpc-url mantle_sepolia --broadcast --verify
contract DeployExecutor is Script {
    MerchantMoeAdapter public adapter;
    AgentExecutor public executor;

    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address lbRouter = vm.envAddress("MANTLE_LB_ROUTER");
        address seedToken = vm.envAddress("SEED_TOKEN");
        uint256 seedAmount = vm.envUint("SEED_AMOUNT");
        uint256 binStep = vm.envOr("LB_BIN_STEP", uint256(20));
        uint256 deadlineWindow = vm.envOr("LB_DEADLINE_WINDOW", uint256(300));

        vm.startBroadcast(deployerKey);
        adapter = new MerchantMoeAdapter(lbRouter, binStep, deadlineWindow);
        // AgentExecutor's constructor reverts on a zero router, so the adapter must
        // exist first — that ordering is the whole reason this is its own script.
        executor = new AgentExecutor(seedToken, seedAmount, address(adapter));
        vm.stopBroadcast();

        console2.log("MerchantMoeAdapter:", address(adapter));
        console2.log("AgentExecutor:     ", address(executor));
        console2.log("LB router:         ", lbRouter);
        console2.log("seed token:        ", seedToken);
    }
}
