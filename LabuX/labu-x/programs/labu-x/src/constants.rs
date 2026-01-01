//! Harmonic constants for the 369-365 system

/// Earth cycle (365 days) - manifest reality
pub const EARTH_CYCLE: u64 = 365;

/// Tesla cycle (369) - ideal harmonic
pub const TESLA_CYCLE: u64 = 369;

/// Precision for fixed-point math (1e9 for Solana compatibility)
pub const PRECISION: u64 = 1_000_000_000;

/// Tesla/Earth ratio = 369/365 * PRECISION
/// = 1.01095890410958904... * 1e9
/// = 1_010_958_904
pub const TESLA_RATIO: u64 = 1_010_958_904;

/// Peg value = $1.00 * PRECISION
pub const PEG_VALUE: u64 = PRECISION;

/// Maximum TCP = Tesla Ratio - Peg
/// = 10_958_904 (~1.096%)
pub const TCP_MAX: u64 = TESLA_RATIO - PEG_VALUE;

/// Quarterly window period (91.25 days in seconds)
pub const QUARTERLY_WINDOW_PERIOD: i64 = 7_884_000;

/// Quarterly window duration (3 days in seconds)
pub const QUARTERLY_WINDOW_DURATION: i64 = 259_200;

/// Micro window period (9.125 days in seconds)
pub const MICRO_WINDOW_PERIOD: i64 = 788_400;

/// Micro window duration (12 hours in seconds)
pub const MICRO_WINDOW_DURATION: i64 = 43_200;

/// Primary window period (92.25 years - for reference)
pub const PRIMARY_WINDOW_YEARS: f64 = 92.25;

/// Minimum τₖ (3.0 * PRECISION)
pub const TAU_K_MIN: u64 = 3 * PRECISION;

/// Maximum τₖ (9.0 * PRECISION)
pub const TAU_K_MAX: u64 = 9 * PRECISION;

/// Default τₖ (7.0 * PRECISION)
pub const TAU_K_DEFAULT: u64 = 7 * PRECISION;

/// Seeds for PDAs
pub mod seeds {
    pub const PROTOCOL_STATE: &[u8] = b"protocol_state";
    pub const ACCOUNT_STATE: &[u8] = b"account_state";
    pub const MINT: &[u8] = b"labux_mint";
    pub const COLLATERAL_VAULT: &[u8] = b"collateral_vault";
}

/// Token decimals (standard for Solana SPL tokens)
pub const TOKEN_DECIMALS: u8 = 9;
