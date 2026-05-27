// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { IGlassBoxAgent } from "./IGlassBoxAgent.sol";

/// Routes a Fold ensemble decision to an actual on-chain swap.
///
/// Hard-coded risk caps:
///   - max trade size = 5% of seed per call (MAX_TRADE_BPS = 500)
///   - portfolio circuit-breaker: if cumulative loss exceeds 20% of seed, executor halts
///   - confidence floor: trades below MIN_CONFIDENCE_BPS (5000 = 50%) are rejected
///   - Devil's Advocate veto: if DA emits sizeBps=0 with HOLD, the round is aborted regardless of ensemble
interface ISwapRouter {
    /// Minimal swap interface. Concrete adapter wraps Merchant Moe V3 / Agni / Fluxion.
    function swapExactTokensForTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        address recipient
    ) external returns (uint256 amountOut);
}

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract AgentExecutor {
    uint256 public constant MAX_TRADE_BPS = 500;        // 5% of seed per trade
    uint256 public constant DRAWDOWN_LIMIT_BPS = 2000;  // 20% portfolio drawdown halts trading
    uint256 public constant MIN_CONFIDENCE_BPS = 5000;  // 50% confidence floor
    uint256 public constant BPS_DENOMINATOR = 10_000;

    address public immutable owner;
    address public immutable seedToken;       // e.g. USDC on Mantle
    uint256 public immutable seedAmount;      // initial USDC seed in token decimals

    ISwapRouter public swapRouter;
    uint256 public cumulativeLossNotional;   // total realized loss in seedToken units
    bool public halted;

    event TradeExecuted(
        uint256 indexed roundId,
        uint256 indexed agentEnsembleSignal,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );
    event TradeRejected(uint256 indexed roundId, string reason);
    event LossRecorded(uint256 indexed roundId, uint256 lossNotional, uint256 cumulativeLoss);
    event Halted(uint256 cumulativeLoss);
    event RouterUpdated(address indexed router);

    error NotOwner();
    error AlreadyHalted();
    error ConfidenceTooLow();
    error TradeSizeExceedsCap();
    error DevilsAdvocateVeto();
    error NoSwapRouter();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier whenNotHalted() {
        if (halted) revert AlreadyHalted();
        _;
    }

    constructor(address _seedToken, uint256 _seedAmount, address _swapRouter) {
        owner = msg.sender;
        seedToken = _seedToken;
        seedAmount = _seedAmount;
        swapRouter = ISwapRouter(_swapRouter);
    }

    function setSwapRouter(address newRouter) external onlyOwner {
        swapRouter = ISwapRouter(newRouter);
        emit RouterUpdated(newRouter);
    }

    /// Execute a trade gated by all risk constraints. Reverts on cap violations.
    /// Caller must have approved this contract to spend `tokenIn` from its balance.
    ///
    /// @param roundId           RoundState round identifier
    /// @param ensembleSignal    Fold output magnitude * 1e4 (e.g. 6200 = +0.62)
    /// @param ensembleConfBps   Ensemble confidence in basis points (0-10000)
    /// @param daVetoed          Whether Devil's Advocate vetoed (signal=0 + HOLD)
    /// @param tokenIn / tokenOut Pair (must include seedToken on one side for accounting)
    /// @param sizeBps           Position size in bps of seedAmount (must be ≤ MAX_TRADE_BPS)
    /// @param minAmountOut      Slippage protection
    function executeTrade(
        uint256 roundId,
        int256 ensembleSignal,
        uint256 ensembleConfBps,
        bool daVetoed,
        address tokenIn,
        address tokenOut,
        uint256 sizeBps,
        uint256 minAmountOut
    ) external onlyOwner whenNotHalted returns (uint256 amountOut) {
        if (address(swapRouter) == address(0)) revert NoSwapRouter();
        if (daVetoed) {
            emit TradeRejected(roundId, "DA veto");
            revert DevilsAdvocateVeto();
        }
        if (ensembleConfBps < MIN_CONFIDENCE_BPS) {
            emit TradeRejected(roundId, "confidence < 50%");
            revert ConfidenceTooLow();
        }
        if (sizeBps == 0 || sizeBps > MAX_TRADE_BPS) {
            emit TradeRejected(roundId, "size exceeds 5% cap");
            revert TradeSizeExceedsCap();
        }

        uint256 amountIn = (seedAmount * sizeBps) / BPS_DENOMINATOR;
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenIn).approve(address(swapRouter), amountIn);

        amountOut = swapRouter.swapExactTokensForTokens(
            tokenIn,
            tokenOut,
            amountIn,
            minAmountOut,
            address(this)
        );

        emit TradeExecuted(roundId, uint256(ensembleSignal), tokenIn, tokenOut, amountIn, amountOut);
    }

    /// Record a realized loss after settlement. Triggers halt if cumulative loss
    /// exceeds DRAWDOWN_LIMIT_BPS of the seed.
    function recordLoss(uint256 roundId, uint256 lossNotional) external onlyOwner whenNotHalted {
        cumulativeLossNotional += lossNotional;
        emit LossRecorded(roundId, lossNotional, cumulativeLossNotional);

        uint256 drawdownLimit = (seedAmount * DRAWDOWN_LIMIT_BPS) / BPS_DENOMINATOR;
        if (cumulativeLossNotional >= drawdownLimit) {
            halted = true;
            emit Halted(cumulativeLossNotional);
        }
    }

    /// Manual halt — owner can stop trading anytime.
    function halt() external onlyOwner {
        halted = true;
        emit Halted(cumulativeLossNotional);
    }
}
