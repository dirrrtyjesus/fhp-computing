use anchor_lang::prelude::*;

/// Golden Ratio (φ) scaled by 1e9 for precision
pub const PHI_SCALED: u64 = 1_618_033_988;
/// Inverse Golden Ratio (φ⁻¹) scaled by 1e9
pub const PHI_INV_SCALED: u64 = 618_033_988;
/// Allocation Ratio (1 - φ⁻¹) = 38.2% scaled by 1e9
pub const ALLOCATION_RATIO_SCALED: u64 = 381_966_011;
/// Scaling factor
pub const SCALE: u64 = 1_000_000_000;

/// The Supermassive Temporal Attractor (PTO²)
///
/// Funds and coordinates child PTOs via Golden Ratio logic.
#[account]
#[derive(Default)]
pub struct GenesisFund {
    /// Authority (Core Council)
    pub authority: Pubkey,

    /// Core Treasury Balance (61.8% of capital)
    /// Used for stability, emergency liquidity, and yield buffering.
    pub core_treasury: u64,

    /// Allocation Pool Balance (38.2% of capital)
    /// Used to seed new child PTOs.
    pub allocation_pool: u64,

    /// Total Mass (Total Capital Infall)
    pub total_mass: u64,

    /// Bump seed
    pub bump: u8,

    /// Protocol fee treasury wallet (set via migration)
    pub protocol_treasury: Pubkey,

    /// Running total of all fees collected
    pub total_fees_collected: u64,
}

impl GenesisFund {
    pub const SIZE: usize = 8 + // discriminator
        32 + // authority
        8 +  // core_treasury
        8 +  // allocation_pool
        8 +  // total_mass
        1 +  // bump
        32 + // protocol_treasury
        8;   // total_fees_collected
}

/// A Child PTO spawned by the Genesis Fund
#[account]
pub struct ChildPTO {
    /// The project creator
    pub creator: Pubkey,

    /// The sector (e.g., "DeFi", "AI")
    pub sector: [u8; 16],

    /// Funding Goal (in USDC/LabuX)
    pub funding_goal: u64,

    /// Coherence Mass (τₖ × Clarity)
    pub coherence_mass: u64,

    /// Seed Capital received from Genesis Fund
    pub seed_capital: u64,

    /// Is emission active?
    pub emission_active: bool,

    /// Current coherence score (0-1000)
    pub coherence_score: u16,

    /// Bump seed
    pub bump: u8,
}

impl ChildPTO {
    pub const SIZE: usize = 8 +
        32 + // creator
        16 + // sector
        8 +  // funding_goal
        8 +  // coherence_mass
        8 +  // seed_capital
        1 +  // emission_active
        2 +  // coherence_score
        1;   // bump
}

/// Records an investment infall event with phase data
#[account]
pub struct InvestorRecord {
    /// The investor
    pub investor: Pubkey,

    /// Amount invested
    pub amount: u64,

    /// Phase angle (e.g., block slot % 360)
    pub phase: u16,

    /// Timestamp
    pub timestamp: i64,

    /// Has yield been claimed?
    pub claimed: bool,

    /// Total ecosystem mass at time of entry (for Phase Tiers)
    pub entry_mass: u64,

    /// Bump seed
    pub bump: u8,
}

impl InvestorRecord {
    pub const SIZE: usize = 8 +
        32 + // investor
        8 +  // amount
        2 +  // phase
        8 +  // timestamp
        1 +  // claimed
        8 +  // entry_mass
        1;   // bump
}
