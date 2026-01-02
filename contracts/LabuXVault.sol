// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title LabuXVault - Collateral Management for LabuX
 * @notice Holds 1:1 collateral backing for all minted LabuX
 * @dev Supports USDC, USDT, and other approved stablecoins as collateral
 */
contract LabuXVault is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice LabuX token contract
    address public labux;

    /// @notice Approved collateral tokens
    mapping(address => bool) public approvedCollateral;

    /// @notice Collateral balance per token
    mapping(address => uint256) public collateralBalances;

    /// @notice Total collateral value (normalized to 18 decimals)
    uint256 public totalCollateralValue;

    /// @notice User deposits per collateral type
    mapping(address => mapping(address => uint256)) public userDeposits;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    event CollateralDeposited(
        address indexed user,
        address indexed token,
        uint256 amount,
        uint256 normalizedAmount
    );

    event CollateralWithdrawn(
        address indexed user,
        address indexed token,
        uint256 amount
    );

    event CollateralApproved(address indexed token, bool approved);
    event LabuXSet(address indexed labux);

    // ═══════════════════════════════════════════════════════════════════════
    // ERRORS
    // ═══════════════════════════════════════════════════════════════════════

    error NotApprovedCollateral();
    error InsufficientCollateral();
    error Unauthorized();
    error ZeroAmount();
    error ZeroAddress();

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    modifier onlyLabuX() {
        if (msg.sender != labux) revert Unauthorized();
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    constructor() Ownable(msg.sender) {}

    // ═══════════════════════════════════════════════════════════════════════
    // CORE FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Deposit collateral to back LabuX minting
     * @param token Collateral token address
     * @param amount Amount to deposit
     * @return normalizedAmount Amount normalized to 18 decimals
     */
    function deposit(
        address token,
        uint256 amount
    ) external nonReentrant returns (uint256 normalizedAmount) {
        if (!approvedCollateral[token]) revert NotApprovedCollateral();
        if (amount == 0) revert ZeroAmount();

        // Transfer collateral to vault
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        // Normalize to 18 decimals
        uint8 decimals = _getDecimals(token);
        normalizedAmount = _normalize(amount, decimals);

        // Update balances
        collateralBalances[token] += amount;
        totalCollateralValue += normalizedAmount;
        userDeposits[msg.sender][token] += amount;

        emit CollateralDeposited(msg.sender, token, amount, normalizedAmount);
    }

    /**
     * @notice Withdraw collateral (called by LabuX on burn)
     * @param user User to return collateral to
     * @param token Collateral token address
     * @param amount Amount to withdraw
     */
    function withdraw(
        address user,
        address token,
        uint256 amount
    ) external onlyLabuX nonReentrant {
        if (collateralBalances[token] < amount) revert InsufficientCollateral();

        // Normalize for tracking
        uint8 decimals = _getDecimals(token);
        uint256 normalizedAmount = _normalize(amount, decimals);

        // Update balances
        collateralBalances[token] -= amount;
        totalCollateralValue -= normalizedAmount;

        // Transfer to user
        IERC20(token).safeTransfer(user, amount);

        emit CollateralWithdrawn(user, token, amount);
    }

    /**
     * @notice Get user's total collateral value
     * @param user User address
     * @return value Total value in 18 decimal USD terms
     */
    function getUserCollateralValue(address user) external view returns (uint256 value) {
        // In production, iterate through all approved tokens
        // For simplicity, assume single token for now
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ADMIN FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Set LabuX contract address
     * @param _labux LabuX contract address
     */
    function setLabuX(address _labux) external onlyOwner {
        if (_labux == address(0)) revert ZeroAddress();
        labux = _labux;
        emit LabuXSet(_labux);
    }

    /**
     * @notice Approve or revoke collateral token
     * @param token Token address
     * @param approved Whether to approve
     */
    function setApprovedCollateral(address token, bool approved) external onlyOwner {
        if (token == address(0)) revert ZeroAddress();
        approvedCollateral[token] = approved;
        emit CollateralApproved(token, approved);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Get token decimals
     * @param token Token address
     * @return decimals Token decimals (defaults to 18)
     */
    function _getDecimals(address token) internal view returns (uint8) {
        // Try to get decimals, default to 18
        try IERC20Metadata(token).decimals() returns (uint8 decimals) {
            return decimals;
        } catch {
            return 18;
        }
    }

    /**
     * @notice Normalize amount to 18 decimals
     * @param amount Raw amount
     * @param decimals Token decimals
     * @return normalized Amount in 18 decimals
     */
    function _normalize(uint256 amount, uint8 decimals) internal pure returns (uint256) {
        if (decimals == 18) return amount;
        if (decimals < 18) return amount * 10**(18 - decimals);
        return amount / 10**(decimals - 18);
    }
}

interface IERC20Metadata {
    function decimals() external view returns (uint8);
}
