// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Non-transferable ERC-20-ish reputation token.
///
/// Minted to an agent every time its reasoning hash is committed via the
/// authorized minter (typically ReasoningHashAnchor or the settler service).
/// Tokens are tiered:
///   tier 0: raw (1 mint per reasoning commit)
///   tier 1: refined (10 raw rolled up)
///   tier 2: crystallized (10 refined rolled up)
///   tier 3: transcendent (10 crystallized rolled up)
///
/// The combine() function rolls low-tier into next tier — same wallet, no transfer.
/// Tokens are bound to the agent's owner address and cannot be sent or sold.
contract ReasoningRepToken {
    string public constant name = "Glass-Box Reasoning Reputation";
    string public constant symbol = "GBRR";
    uint8 public constant decimals = 0;

    uint8 public constant MAX_TIER = 3;
    uint256 public constant COMBINE_RATIO = 10;

    address public immutable owner;
    address public minter;

    // balances[holder][tier] = token count
    mapping(address => mapping(uint8 => uint256)) public balances;
    mapping(uint8 => uint256) public totalByTier;

    event Minted(address indexed holder, uint8 indexed tier, uint256 amount);
    event Combined(address indexed holder, uint8 indexed fromTier, uint8 indexed toTier, uint256 fromAmount, uint256 toAmount);
    event MinterUpdated(address indexed newMinter);

    error NotOwner();
    error NotMinter();
    error InvalidTier();
    error InsufficientBalance();
    error AtMaxTier();
    error NonTransferable();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyMinter() {
        if (msg.sender != minter && msg.sender != owner) revert NotMinter();
        _;
    }

    constructor(address _minter) {
        owner = msg.sender;
        minter = _minter == address(0) ? msg.sender : _minter;
    }

    function setMinter(address newMinter) external onlyOwner {
        minter = newMinter;
        emit MinterUpdated(newMinter);
    }

    /// Minter calls this when a reasoning hash is committed.
    function mint(address holder, uint256 amount) external onlyMinter {
        balances[holder][0] += amount;
        totalByTier[0] += amount;
        emit Minted(holder, 0, amount);
    }

    /// Roll `amount * COMBINE_RATIO` tier-N tokens into `amount` tier-(N+1) tokens.
    /// Anyone can call this for their own balance — gas-paid promotion.
    function combine(uint8 fromTier, uint256 toAmount) external returns (uint256 burned) {
        if (fromTier >= MAX_TIER) revert AtMaxTier();
        burned = toAmount * COMBINE_RATIO;
        if (balances[msg.sender][fromTier] < burned) revert InsufficientBalance();
        balances[msg.sender][fromTier] -= burned;
        totalByTier[fromTier] -= burned;
        balances[msg.sender][fromTier + 1] += toAmount;
        totalByTier[fromTier + 1] += toAmount;
        emit Combined(msg.sender, fromTier, fromTier + 1, burned, toAmount);
    }

    function balanceOf(address holder, uint8 tier) external view returns (uint256) {
        if (tier > MAX_TIER) revert InvalidTier();
        return balances[holder][tier];
    }

    function totalBalanceOf(address holder) external view returns (uint256 total) {
        for (uint8 t = 0; t <= MAX_TIER; t++) {
            // weight by tier^10 so transcendent counts much more in aggregate score
            uint256 weight = 1;
            for (uint8 i = 0; i < t; i++) weight *= COMBINE_RATIO;
            total += balances[holder][t] * weight;
        }
    }

    /// Non-transferable — no transfer / approve / transferFrom.
    /// These functions exist only to fail loudly when wallets / explorers probe.
    function transfer(address, uint256) external pure returns (bool) {
        revert NonTransferable();
    }

    function transferFrom(address, address, uint256) external pure returns (bool) {
        revert NonTransferable();
    }

    function approve(address, uint256) external pure returns (bool) {
        revert NonTransferable();
    }

    function allowance(address, address) external pure returns (uint256) {
        return 0;
    }
}
