// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { AgentExecutor, ISwapRouter, IERC20 } from "../src/AgentExecutor.sol";

// Minimal mock USDC-like token.
contract MockERC20 {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    string public symbol;
    uint8 public decimals = 6;

    constructor(string memory _symbol) {
        symbol = _symbol;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "balance");
        require(allowance[from][msg.sender] >= amount, "allowance");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }
}

// Mock swap router that returns a fixed exchange rate.
contract MockSwapRouter is ISwapRouter {
    uint256 public rateBps = 10_000; // 1:1 by default

    function setRate(uint256 newRateBps) external {
        rateBps = newRateBps;
    }

    function swapExactTokensForTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        address recipient
    ) external returns (uint256 amountOut) {
        amountOut = (amountIn * rateBps) / 10_000;
        require(amountOut >= amountOutMin, "slippage");
        MockERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        MockERC20(tokenOut).mint(recipient, amountOut);
    }
}

contract AgentExecutorTest is Test {
    AgentExecutor internal executor;
    MockERC20 internal usdc;
    MockERC20 internal mETH;
    MockSwapRouter internal router;

    uint256 internal constant SEED_USDC = 200 * 1e6; // $200 in 6-decimal USDC

    function setUp() public {
        usdc = new MockERC20("USDC");
        mETH = new MockERC20("mETH");
        router = new MockSwapRouter();
        executor = new AgentExecutor(address(usdc), SEED_USDC, address(router));

        // Owner is this test contract. Fund + approve.
        usdc.mint(address(this), SEED_USDC);
        usdc.approve(address(executor), type(uint256).max);
    }

    function test_HappyPath_5pctTradeExecutes() public {
        // 500 bps = 5% of $200 = $10 trade
        uint256 amountOut = executor.executeTrade(
            1,                  // roundId
            6200,               // ensembleSignal +0.62
            7000,               // 70% confidence
            false,              // not vetoed
            address(usdc),
            address(mETH),
            500,                // 5%
            0                   // minAmountOut
        );
        assertEq(amountOut, 10 * 1e6);
        assertEq(mETH.balanceOf(address(executor)), 10 * 1e6);
    }

    function test_RevertOn_DAVeto() public {
        vm.expectRevert(AgentExecutor.DevilsAdvocateVeto.selector);
        executor.executeTrade(1, 6200, 7000, true, address(usdc), address(mETH), 500, 0);
    }

    function test_RevertOn_LowConfidence() public {
        vm.expectRevert(AgentExecutor.ConfidenceTooLow.selector);
        executor.executeTrade(1, 6200, 4900, false, address(usdc), address(mETH), 500, 0);
    }

    function test_RevertOn_OversizedTrade() public {
        // 501 bps > 500 bps cap
        vm.expectRevert(AgentExecutor.TradeSizeExceedsCap.selector);
        executor.executeTrade(1, 6200, 7000, false, address(usdc), address(mETH), 501, 0);
    }

    function test_RevertOn_ZeroSize() public {
        vm.expectRevert(AgentExecutor.TradeSizeExceedsCap.selector);
        executor.executeTrade(1, 6200, 7000, false, address(usdc), address(mETH), 0, 0);
    }

    function test_HaltsOn20pctDrawdown() public {
        // 20% of $200 = $40 loss
        uint256 dd = (SEED_USDC * 2000) / 10_000;
        executor.recordLoss(1, dd);
        assertTrue(executor.halted());

        // Any further trade should revert
        vm.expectRevert(AgentExecutor.AlreadyHalted.selector);
        executor.executeTrade(2, 6200, 7000, false, address(usdc), address(mETH), 500, 0);
    }

    function test_CumulativeLossTriggersHalt() public {
        // Three losses adding up to >= 20% should halt
        executor.recordLoss(1, 15 * 1e6);
        executor.recordLoss(2, 15 * 1e6);
        assertFalse(executor.halted(), "should not halt yet at $30 of $40");
        executor.recordLoss(3, 11 * 1e6);
        assertTrue(executor.halted(), "should halt at $41 cumulative loss");
    }

    function test_ManualHalt() public {
        executor.halt();
        assertTrue(executor.halted());
    }

    function test_OwnerOnly() public {
        vm.prank(address(0xBEEF));
        vm.expectRevert(AgentExecutor.NotOwner.selector);
        executor.executeTrade(1, 6200, 7000, false, address(usdc), address(mETH), 500, 0);
    }

    function test_SlippageProtection() public {
        router.setRate(8_000); // 80% rate = 20% slippage
        vm.expectRevert("slippage");
        executor.executeTrade(1, 6200, 7000, false, address(usdc), address(mETH), 500, 10 * 1e6);
    }
}
