use anchor_lang::prelude::*;

#[error_code]
pub enum LabuXError {
    #[msg("Insufficient capital in Allocation Pool")]
    InsufficientBasinDepth,
    #[msg("Token Mint does not match Temporal Genesis Fund")]
    InvalidTokenMint,

    #[msg("Insufficient collateral")]
    InsufficientCollateral,

    #[msg("Invalid amount - must be greater than zero")]
    InvalidAmount,

    #[msg("Invalid τₖ - must be between 3.0 and 9.0")]
    InvalidTauK,

    #[msg("Not in harmonic window - harvest only available during windows")]
    NotInHarmonicWindow,

    #[msg("No TCP to harvest")]
    NoTCPToHarvest,

    #[msg("Unauthorized")]
    Unauthorized,

    #[msg("Protocol is paused")]
    ProtocolPaused,

    #[msg("Math overflow")]
    MathOverflow,

    #[msg("Math underflow")]
    MathUnderflow,
}
