// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { ISwapRouter, IERC20 } from "./AgentExecutor.sol";

/// Adapter that translates AgentExecutor's simple ISwapRouter interface into
/// Merchant Moe's Liquidity Book router calls.
///
/// Merchant Moe is a Liquidity Book DEX on Mantle (Trader Joe LB v2.2 fork).
/// Its router uses a path-based interface with bin steps + versions, which we
/// wrap behind the simple swapExactTokensForTokens(tokenIn, tokenOut, ...)
/// signature that AgentExecutor expects.
///
/// Real LBRouter address on Mantle Mainnet is set at deploy time (configurable).
interface ILBRouter {
    enum Version { V1, V2, V2_1, V2_2 }

    struct Path {
        uint256[] pairBinSteps;
        Version[] versions;
        address[] tokenPath;
    }

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        Path calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256 amountOut);
}

contract MerchantMoeAdapter is ISwapRouter {
    ILBRouter public immutable lbRouter;
    uint256 public defaultBinStep;     // e.g. 20 for a 0.20% bin step pool
    uint256 public deadlineWindow;     // seconds to add to block.timestamp

    address public immutable owner;

    event Swapped(address indexed tokenIn, address indexed tokenOut, uint256 amountIn, uint256 amountOut);
    event ParamsUpdated(uint256 binStep, uint256 deadlineWindow);

    error NotOwner();
    error TransferFailed();
    error ApprovalFailed();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor(address _lbRouter, uint256 _defaultBinStep, uint256 _deadlineWindow) {
        owner = msg.sender;
        lbRouter = ILBRouter(_lbRouter);
        defaultBinStep = _defaultBinStep == 0 ? 20 : _defaultBinStep;
        deadlineWindow = _deadlineWindow == 0 ? 300 : _deadlineWindow;
    }

    function setParams(uint256 _binStep, uint256 _deadlineWindow) external onlyOwner {
        defaultBinStep = _binStep;
        deadlineWindow = _deadlineWindow;
        emit ParamsUpdated(_binStep, _deadlineWindow);
    }

    /// @inheritdoc ISwapRouter
    function swapExactTokensForTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        address recipient
    ) external returns (uint256 amountOut) {
        // Caller (AgentExecutor) must have approved this adapter to pull tokenIn.
        if (!IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn)) revert TransferFailed();
        if (!IERC20(tokenIn).approve(address(lbRouter), amountIn)) revert ApprovalFailed();

        ILBRouter.Path memory path = _buildDirectPath(tokenIn, tokenOut);

        amountOut = lbRouter.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            recipient,
            block.timestamp + deadlineWindow
        );

        emit Swapped(tokenIn, tokenOut, amountIn, amountOut);
    }

    /// Build a single-hop path (tokenIn -> tokenOut) using the default bin step + V2_2.
    function _buildDirectPath(address tokenIn, address tokenOut)
        internal
        view
        returns (ILBRouter.Path memory path)
    {
        path.pairBinSteps = new uint256[](1);
        path.pairBinSteps[0] = defaultBinStep;

        path.versions = new ILBRouter.Version[](1);
        path.versions[0] = ILBRouter.Version.V2_2;

        path.tokenPath = new address[](2);
        path.tokenPath[0] = tokenIn;
        path.tokenPath[1] = tokenOut;
    }
}
