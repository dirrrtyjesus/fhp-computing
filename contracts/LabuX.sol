// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title LabuX - The Harmonic Constraint Stablecoin
 * @author LaBubuntu
 * @notice Pegged to $1.00 (Earth/365) with TCP up to 1.096% (Tesla/369)
 *
 * The $1 peg is the EARTH HARMONIC (365) - manifest economic reality.
 * The TCP ceiling is the TESLA HARMONIC (369/365) - ideal coherent value.
 * The 4-cent gap between them is CREATIVE TENSION - the engine that makes it work.
 *
 * ═══════════════════════════════════════════════════════════════════════════
 *
 *          $1.00                                           $1.01096
 *            │                                                │
 *      ══════╪════════════════════════════════════════════════╪══════
 *            │              HARMONIC GAP                      │
 *            │                (TCP zone)                      │
 *            │                                                │
 *          EARTH                                           TESLA
 *          (365)                                           (369)
 *           PEG                                           MAX TCP
 *
 * ═══════════════════════════════════════════════════════════════════════════
 */
contract LabuX is ERC20, ERC20Permit, Ownable, ReentrancyGuard {

    // ═══════════════════════════════════════════════════════════════════════
    // HARMONIC CONSTANTS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Earth cycle - days in year, manifest reality
    uint256 public constant EARTH_CYCLE = 365;

    /// @notice Tesla cycle - vortex number, ideal harmonic
    uint256 public constant TESLA_CYCLE = 369;

    /// @notice Precision for fixed-point math
    uint256 public constant PRECISION = 1e18;

    /// @notice Tesla/Earth ratio = 369/365 * 1e18 = 1.01095890410958904...
    uint256 public constant TESLA_RATIO = 1010958904109589041;

    /// @notice Peg value = $1.00 * 1e18
    uint256 public constant PEG_VALUE = 1e18;

    /// @notice Maximum TCP = Tesla Ratio - Peg = ~0.01096 * 1e18
    uint256 public constant TCP_MAX = TESLA_RATIO - PEG_VALUE;

    /// @notice Quarterly window period (91.25 days in seconds)
    uint256 public constant QUARTERLY_WINDOW_PERIOD = 7_884_000; // 91.25 * 86400

    /// @notice Quarterly window duration (3 days in seconds)
    uint256 public constant QUARTERLY_WINDOW_DURATION = 259_200; // 3 * 86400

    /// @notice Micro window period (9.125 days in seconds)
    uint256 public constant MICRO_WINDOW_PERIOD = 788_400; // 9.125 * 86400

    /// @notice Micro window duration (12 hours in seconds)
    uint256 public constant MICRO_WINDOW_DURATION = 43_200; // 12 * 3600

    /// @notice Minimum τₖ value (3.0)
    uint256 public constant TAU_K_MIN = 3e18;

    /// @notice Maximum τₖ value (9.0)
    uint256 public constant TAU_K_MAX = 9e18;

    /// @notice Default τₖ value (7.0)
    uint256 public constant TAU_K_DEFAULT = 7e18;

    // ═══════════════════════════════════════════════════════════════════════
    // STATE VARIABLES
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Account TCP and coherence state
    struct Account {
        uint256 tcpBalance;       // Accumulated TCP (scaled by 1e18)
        uint256 lastActivity;     // Last interaction timestamp
        uint256 holdDuration;     // Cumulative hold time in seconds
        uint256 phaseLocks;       // Network participation count
        uint256 tauK;             // Coherence coefficient (3e18 to 9e18)
        uint256 windowsHarvested; // Number of harvest events
    }

    /// @notice Mapping of account addresses to their state
    mapping(address => Account) public accounts;

    /// @notice Collateral vault address
    address public vault;

    /// @notice Total collateral backing the supply
    uint256 public totalCollateral;

    /// @notice Total TCP accumulated across all accounts
    uint256 public totalTCP;

    /// @notice Network average τₖ
    uint256 public networkTauK = TAU_K_DEFAULT;

    /// @notice Reference timestamp for window calculations
    uint256 public windowEpoch;

    /// @notice Coherence oracle address (can update τₖ values)
    address public coherenceOracle;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    event Minted(address indexed to, uint256 amount, uint256 collateral);
    event Burned(address indexed from, uint256 amount, uint256 collateralReturned);
    event TCPAccrued(address indexed account, uint256 amount, uint256 multiplier);
    event TCPHarvested(address indexed account, uint256 tcpAmount, uint256 newLabux);
    event TCPTransferred(address indexed from, address indexed to, uint256 amount);
    event TauKUpdated(address indexed account, uint256 oldTauK, uint256 newTauK);
    event PhaseLockRecorded(address indexed account, uint256 totalLocks);
    event WindowEntered(string windowType, uint256 multiplier);
    event CoherenceOracleUpdated(address indexed oldOracle, address indexed newOracle);

    // ═══════════════════════════════════════════════════════════════════════
    // ERRORS
    // ═══════════════════════════════════════════════════════════════════════

    error InsufficientBalance();
    error InsufficientCollateral();
    error InvalidAmount();
    error InvalidTauK();
    error NotInHarmonicWindow();
    error NoTCPToHarvest();
    error Unauthorized();
    error ZeroAddress();

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    modifier onlyCoherenceOracle() {
        if (msg.sender != coherenceOracle && msg.sender != owner()) {
            revert Unauthorized();
        }
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Initialize LabuX with vault and window epoch
     * @param _vault Address of collateral vault
     * @param _windowEpoch Reference timestamp for harmonic windows
     */
    constructor(address _vault, uint256 _windowEpoch)
        ERC20("LabuX", "LABUX")
        ERC20Permit("LabuX")
        Ownable(msg.sender)
    {
        if (_vault == address(0)) revert ZeroAddress();

        vault = _vault;
        windowEpoch = _windowEpoch == 0 ? block.timestamp : _windowEpoch;
        coherenceOracle = msg.sender;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CORE FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Mint LabuX with 1:1 collateral backing
     * @param to Recipient address
     * @param amount Amount to mint (1e18 = 1 LABUX = $1.00)
     * @dev Requires prior collateral deposit to vault
     */
    function mint(address to, uint256 amount) external nonReentrant {
        if (amount == 0) revert InvalidAmount();
        if (to == address(0)) revert ZeroAddress();

        // In production: verify collateral has been deposited to vault
        // For now, track internally
        totalCollateral += amount;

        // Initialize account if new
        _initializeAccount(to);

        // Accrue any pending TCP before balance change
        _accrueTCP(to);

        // Mint tokens
        _mint(to, amount);

        emit Minted(to, amount, amount);
    }

    /**
     * @notice Burn LabuX and receive collateral back
     * @param amount Amount to burn
     */
    function burn(uint256 amount) external nonReentrant {
        if (amount == 0) revert InvalidAmount();
        if (balanceOf(msg.sender) < amount) revert InsufficientBalance();

        // Accrue TCP before burn
        _accrueTCP(msg.sender);

        // Calculate proportional TCP to forfeit
        Account storage acc = accounts[msg.sender];
        uint256 balance = balanceOf(msg.sender);

        if (balance > 0 && acc.tcpBalance > 0) {
            uint256 tcpForfeit = (acc.tcpBalance * amount) / balance;
            acc.tcpBalance -= tcpForfeit;
            totalTCP -= tcpForfeit;
        }

        // Burn tokens
        _burn(msg.sender, amount);

        // Return collateral
        totalCollateral -= amount;
        // In production: transfer actual collateral from vault

        emit Burned(msg.sender, amount, amount);
    }

    /**
     * @notice Transfer LabuX with optional TCP inclusion
     * @param to Recipient address
     * @param amount Amount of LabuX to transfer
     * @param includeTCP Whether to transfer proportional TCP
     * @return success True if transfer succeeded
     */
    function transferWithTCP(
        address to,
        uint256 amount,
        bool includeTCP
    ) external nonReentrant returns (bool) {
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert InvalidAmount();
        if (balanceOf(msg.sender) < amount) revert InsufficientBalance();

        // Initialize recipient if new
        _initializeAccount(to);

        // Accrue TCP for both parties
        _accrueTCP(msg.sender);
        _accrueTCP(to);

        // Calculate and transfer TCP if requested
        if (includeTCP) {
            Account storage sender = accounts[msg.sender];
            uint256 senderBalance = balanceOf(msg.sender);

            if (sender.tcpBalance > 0 && senderBalance > 0) {
                uint256 tcpTransfer = (sender.tcpBalance * amount) / senderBalance;
                sender.tcpBalance -= tcpTransfer;
                accounts[to].tcpBalance += tcpTransfer;

                emit TCPTransferred(msg.sender, to, tcpTransfer);
            }
        }

        // Execute transfer
        _transfer(msg.sender, to, amount);

        return true;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TCP FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Manually trigger TCP accrual for caller
     */
    function accrueTCP() external {
        _accrueTCP(msg.sender);
    }

    /**
     * @notice Manually trigger TCP accrual for any account
     * @param account Account to accrue TCP for
     */
    function accrueTCPFor(address account) external {
        _accrueTCP(account);
    }

    /**
     * @notice Harvest accumulated TCP during a harmonic window
     * @return harvested Amount of TCP harvested and converted to LabuX
     */
    function harvestTCP() external nonReentrant returns (uint256 harvested) {
        if (!isWindowActive()) revert NotInHarmonicWindow();

        _accrueTCP(msg.sender);

        Account storage acc = accounts[msg.sender];
        harvested = acc.tcpBalance;

        if (harvested == 0) revert NoTCPToHarvest();

        // TCP converts 1:1 to LabuX (it's already in dollar terms)
        uint256 newLabux = harvested;

        // Reset TCP and increment harvest count
        acc.tcpBalance = 0;
        acc.windowsHarvested += 1;
        totalTCP -= harvested;

        // Mint new LabuX
        _mint(msg.sender, newLabux);

        emit TCPHarvested(msg.sender, harvested, newLabux);
    }

    /**
     * @notice Internal TCP accrual logic
     * @param account Account to accrue for
     */
    function _accrueTCP(address account) internal {
        Account storage acc = accounts[account];
        uint256 balance = balanceOf(account);

        // Nothing to accrue if no balance
        if (balance == 0) {
            acc.lastActivity = block.timestamp;
            return;
        }

        uint256 elapsed = block.timestamp - acc.lastActivity;
        if (elapsed == 0) return;

        // Calculate TCP rate based on account state
        uint256 rate = calculateTCPRate(account);

        // Apply window multiplier
        uint256 multiplier = getCurrentWindowMultiplier();

        // Calculate accrual: balance * rate * elapsed * multiplier / (365 days * PRECISION)
        uint256 accrued = (balance * rate * elapsed * multiplier) / (365 days * PRECISION);

        // Cap at TCP_MAX per unit
        uint256 maxTCP = (balance * TCP_MAX) / PRECISION;
        uint256 newTCP = acc.tcpBalance + accrued;

        if (newTCP > maxTCP) {
            newTCP = maxTCP;
        }

        uint256 tcpDelta = newTCP - acc.tcpBalance;

        // Update state
        acc.tcpBalance = newTCP;
        acc.holdDuration += elapsed;
        acc.lastActivity = block.timestamp;

        if (tcpDelta > 0) {
            totalTCP += tcpDelta;
            emit TCPAccrued(account, tcpDelta, multiplier);
        }
    }

    /**
     * @notice Calculate TCP accrual rate for an account
     * @param account Account to calculate rate for
     * @return rate Annual TCP rate (scaled by PRECISION)
     */
    function calculateTCPRate(address account) public view returns (uint256 rate) {
        Account storage acc = accounts[account];

        // Base rate: TCP_MAX per year at maximum coherence
        uint256 baseRate = TCP_MAX;

        // τₖ multiplier: (τₖ - 3) / 6, clamped to [0.1, 1.0]
        uint256 tauMult = PRECISION / 10; // Minimum 10%
        if (acc.tauK > TAU_K_MIN) {
            tauMult = ((acc.tauK - TAU_K_MIN) * PRECISION) / (6 * PRECISION);
            if (tauMult > PRECISION) tauMult = PRECISION;
            if (tauMult < PRECISION / 10) tauMult = PRECISION / 10;
        }

        // Duration multiplier: 1 + holdDuration / (10 * 365 days), capped at 1.5
        uint256 durMult = PRECISION + (acc.holdDuration * PRECISION) / (10 * 365 days);
        if (durMult > (15 * PRECISION) / 10) durMult = (15 * PRECISION) / 10;

        // Phase lock multiplier: 1 + phaseLocks / 20, capped at 1.5
        uint256 lockMult = PRECISION + (acc.phaseLocks * PRECISION) / 20;
        if (lockMult > (15 * PRECISION) / 10) lockMult = (15 * PRECISION) / 10;

        // Combine multipliers
        rate = (baseRate * tauMult) / PRECISION;
        rate = (rate * durMult) / PRECISION;
        rate = (rate * lockMult) / PRECISION;
    }

    /**
     * @notice Initialize account with default values if not exists
     * @param account Account to initialize
     */
    function _initializeAccount(address account) internal {
        if (accounts[account].tauK == 0) {
            accounts[account].tauK = TAU_K_DEFAULT;
            accounts[account].lastActivity = block.timestamp;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // WINDOW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Check if currently in any harmonic window
     * @return active True if in a window
     */
    function isWindowActive() public view returns (bool active) {
        (bool quarterly, bool micro) = getWindowStatus();
        active = quarterly || micro;
    }

    /**
     * @notice Get detailed window status
     * @return quarterlyActive True if in quarterly window
     * @return microActive True if in micro window
     */
    function getWindowStatus() public view returns (bool quarterlyActive, bool microActive) {
        uint256 elapsed = block.timestamp - windowEpoch;

        // Quarterly: 91.25 day period, 3 day duration
        uint256 quarterlyPhase = elapsed % QUARTERLY_WINDOW_PERIOD;
        quarterlyActive = quarterlyPhase < QUARTERLY_WINDOW_DURATION;

        // Micro: 9.125 day period, 12 hour duration
        uint256 microPhase = elapsed % MICRO_WINDOW_PERIOD;
        microActive = microPhase < MICRO_WINDOW_DURATION;
    }

    /**
     * @notice Get current window TCP multiplier
     * @return multiplier Multiplier scaled by PRECISION (1e18 = 1.0x)
     */
    function getCurrentWindowMultiplier() public view returns (uint256 multiplier) {
        (bool quarterly, bool micro) = getWindowStatus();

        if (quarterly) {
            multiplier = (15 * PRECISION) / 10; // 1.5x
        } else if (micro) {
            multiplier = (12 * PRECISION) / 10; // 1.2x
        } else {
            multiplier = PRECISION; // 1.0x
        }
    }

    /**
     * @notice Get time until next windows
     * @return nextQuarterly Seconds until next quarterly window (0 if active)
     * @return nextMicro Seconds until next micro window (0 if active)
     */
    function getNextWindowTime() external view returns (uint256 nextQuarterly, uint256 nextMicro) {
        uint256 elapsed = block.timestamp - windowEpoch;

        uint256 quarterlyPhase = elapsed % QUARTERLY_WINDOW_PERIOD;
        nextQuarterly = quarterlyPhase < QUARTERLY_WINDOW_DURATION
            ? 0
            : QUARTERLY_WINDOW_PERIOD - quarterlyPhase;

        uint256 microPhase = elapsed % MICRO_WINDOW_PERIOD;
        nextMicro = microPhase < MICRO_WINDOW_DURATION
            ? 0
            : MICRO_WINDOW_PERIOD - microPhase;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Get account's total value including TCP
     * @param account Account to query
     * @return totalValue LabuX balance + TCP (scaled by 1e18)
     */
    function getTotalValue(address account) external view returns (uint256 totalValue) {
        totalValue = balanceOf(account) + accounts[account].tcpBalance;
    }

    /**
     * @notice Get account's effective exchange rate including TCP
     * @param account Account to query
     * @return effectiveRate Rate scaled by 1e18 (1e18 = $1.00)
     */
    function getEffectiveRate(address account) external view returns (uint256 effectiveRate) {
        uint256 balance = balanceOf(account);
        if (balance == 0) return PEG_VALUE;

        effectiveRate = ((balance + accounts[account].tcpBalance) * PEG_VALUE) / balance;
    }

    /**
     * @notice Get comprehensive network statistics
     */
    function getNetworkStats() external view returns (
        uint256 supply,
        uint256 tcp,
        uint256 tcpRatio,
        uint256 collateral,
        uint256 windowMult,
        bool inQuarterly,
        bool inMicro
    ) {
        supply = totalSupply();
        tcp = totalTCP;
        tcpRatio = supply > 0 ? (tcp * PRECISION) / supply : 0;
        collateral = totalCollateral;
        windowMult = getCurrentWindowMultiplier();
        (inQuarterly, inMicro) = getWindowStatus();
    }

    /**
     * @notice Get full account state
     * @param account Account to query
     */
    function getAccountState(address account) external view returns (
        uint256 balance,
        uint256 tcpBalance,
        uint256 tauK,
        uint256 holdDuration,
        uint256 phaseLocks,
        uint256 windowsHarvested,
        uint256 effectiveRate,
        uint256 currentTCPRate
    ) {
        Account storage acc = accounts[account];
        balance = balanceOf(account);
        tcpBalance = acc.tcpBalance;
        tauK = acc.tauK;
        holdDuration = acc.holdDuration;
        phaseLocks = acc.phaseLocks;
        windowsHarvested = acc.windowsHarvested;
        effectiveRate = balance > 0 ? ((balance + tcpBalance) * PEG_VALUE) / balance : PEG_VALUE;
        currentTCPRate = calculateTCPRate(account);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ADMIN FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Update account's τₖ value
     * @param account Account to update
     * @param newTauK New τₖ value (must be between 3e18 and 9e18)
     */
    function updateTauK(address account, uint256 newTauK) external onlyCoherenceOracle {
        if (newTauK < TAU_K_MIN || newTauK > TAU_K_MAX) revert InvalidTauK();

        _initializeAccount(account);
        _accrueTCP(account);

        uint256 oldTauK = accounts[account].tauK;
        accounts[account].tauK = newTauK;

        emit TauKUpdated(account, oldTauK, newTauK);
    }

    /**
     * @notice Record a phase lock event for an account
     * @param account Account that achieved phase lock
     */
    function recordPhaseLock(address account) external onlyCoherenceOracle {
        _initializeAccount(account);
        accounts[account].phaseLocks += 1;

        emit PhaseLockRecorded(account, accounts[account].phaseLocks);
    }

    /**
     * @notice Update coherence oracle address
     * @param newOracle New oracle address
     */
    function setCoherenceOracle(address newOracle) external onlyOwner {
        if (newOracle == address(0)) revert ZeroAddress();

        address oldOracle = coherenceOracle;
        coherenceOracle = newOracle;

        emit CoherenceOracleUpdated(oldOracle, newOracle);
    }

    /**
     * @notice Update vault address
     * @param newVault New vault address
     */
    function setVault(address newVault) external onlyOwner {
        if (newVault == address(0)) revert ZeroAddress();
        vault = newVault;
    }

    /**
     * @notice Update window epoch (for synchronization)
     * @param newEpoch New epoch timestamp
     */
    function setWindowEpoch(uint256 newEpoch) external onlyOwner {
        windowEpoch = newEpoch;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // OVERRIDES
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Override to accrue TCP on all transfers
     */
    function _update(address from, address to, uint256 value) internal override {
        // Accrue TCP for sender (if not minting)
        if (from != address(0)) {
            _initializeAccount(from);
            _accrueTCP(from);
        }

        // Accrue TCP for recipient (if not burning)
        if (to != address(0) && to != from) {
            _initializeAccount(to);
            _accrueTCP(to);
        }

        super._update(from, to, value);
    }
}
