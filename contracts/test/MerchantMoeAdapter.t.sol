// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { Test } from "forge-std/Test.sol";
import { MerchantMoeAdapter, ILBRouter } from "../src/MerchantMoeAdapter.sol";

contract MockERC20 {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

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

// Mock LB router that captures the path it was called with + returns a fixed rate.
contract MockLBRouter is ILBRouter {
    uint256 public rateBps = 9_900; // 1% slippage by default
    address public lastTokenIn;
    address public lastTokenOut;
    uint256 public lastBinStep;
    Version public lastVersion;
    uint256 public lastDeadline;

    function setRate(uint256 r) external { rateBps = r; }

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        Path calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256 amountOut) {
        lastTokenIn = path.tokenPath[0];
        lastTokenOut = path.tokenPath[path.tokenPath.length - 1];
        lastBinStep = path.pairBinSteps[0];
        lastVersion = path.versions[0];
        lastDeadline = deadline;

        amountOut = (amountIn * rateBps) / 10_000;
        require(amountOut >= amountOutMin, "LB: slippage");

        MockERC20(lastTokenIn).transferFrom(msg.sender, address(this), amountIn);
        MockERC20(lastTokenOut).mint(to, amountOut);
    }
}

contract MerchantMoeAdapterTest is Test {
    MerchantMoeAdapter internal adapter;
    MockLBRouter internal lbRouter;
    MockERC20 internal usdc;
    MockERC20 internal mETH;

    function setUp() public {
        lbRouter = new MockLBRouter();
        adapter = new MerchantMoeAdapter(address(lbRouter), 20, 300);
        usdc = new MockERC20();
        mETH = new MockERC20();

        usdc.mint(address(this), 1_000 * 1e6);
        usdc.approve(address(adapter), type(uint256).max);
    }

    function test_SwapRoutesToLBRouterWithCorrectPath() public {
        uint256 out = adapter.swapExactTokensForTokens(
            address(usdc), address(mETH), 100 * 1e6, 0, address(this)
        );
        // 1% slippage -> 99
        assertEq(out, 99 * 1e6);
        // verify path was built correctly
        assertEq(lbRouter.lastTokenIn(), address(usdc));
        assertEq(lbRouter.lastTokenOut(), address(mETH));
        assertEq(lbRouter.lastBinStep(), 20);
        assertEq(uint256(lbRouter.lastVersion()), uint256(ILBRouter.Version.V2_2));
    }

    function test_RecipientReceivesOutput() public {
        address bob = address(0xB0B);
        adapter.swapExactTokensForTokens(address(usdc), address(mETH), 50 * 1e6, 0, bob);
        assertEq(mETH.balanceOf(bob), 49_500_000); // 50 * 0.99 in 6-dec
    }

    function test_SlippageReverts() public {
        lbRouter.setRate(8_000); // 20% slippage
        vm.expectRevert("LB: slippage");
        adapter.swapExactTokensForTokens(address(usdc), address(mETH), 100 * 1e6, 90 * 1e6, address(this));
    }

    function test_DeadlineIsBlockTimestampPlusWindow() public {
        adapter.swapExactTokensForTokens(address(usdc), address(mETH), 10 * 1e6, 0, address(this));
        assertEq(lbRouter.lastDeadline(), block.timestamp + 300);
    }

    function test_SetParamsOwnerOnly() public {
        adapter.setParams(15, 600);
        assertEq(adapter.defaultBinStep(), 15);
        assertEq(adapter.deadlineWindow(), 600);

        vm.prank(address(0xBAD));
        vm.expectRevert(MerchantMoeAdapter.NotOwner.selector);
        adapter.setParams(1, 1);
    }

    function test_DefaultsApplied() public {
        MerchantMoeAdapter a = new MerchantMoeAdapter(address(lbRouter), 0, 0);
        assertEq(a.defaultBinStep(), 20);   // 0 -> default 20
        assertEq(a.deadlineWindow(), 300);  // 0 -> default 300
    }
}
