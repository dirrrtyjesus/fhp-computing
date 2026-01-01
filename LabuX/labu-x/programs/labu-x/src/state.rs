use anchor_lang::prelude::*;

/// Global protocol state (PDA)
#[account]
#[derive(Default)]
pub struct ProtocolState {
    /// Protocol authority
    pub authority: Pubkey,

    /// LabuX SPL token mint
    pub labux_mint: Pubkey,

    /// Collateral token mint (e.g., USDC)
    pub collateral_mint: Pubkey,

    /// Collateral vault (token account)
    pub collateral_vault: Pubkey,

    /// Total TCP in system (scaled by PRECISION)
    pub total_tcp: u64,

    /// Network average τₖ
    pub network_tau_k: u64,

    /// Window epoch (Unix timestamp reference)
    pub window_epoch: i64,

    /// Total collateral deposited
    pub total_collateral: u64,

    /// Total LabuX minted
    pub total_supply: u64,

    /// Coherence oracle (can update τₖ)
    pub coherence_oracle: Pubkey,

    /// Protocol paused
    pub paused: bool,

    /// Bump seed
    pub bump: u8,

    /// Reserved for future use
    pub _reserved: [u8; 64],
}

impl ProtocolState {
    pub const SIZE: usize = 8 +  // discriminator
        32 +  // authority
        32 +  // labux_mint
        32 +  // collateral_mint
        32 +  // collateral_vault
        8 +   // total_tcp
        8 +   // network_tau_k
        8 +   // window_epoch
        8 +   // total_collateral
        8 +   // total_supply
        32 +  // coherence_oracle
        1 +   // paused
        1 +   // bump
        64;   // reserved
}

/// Individual account TCP state (PDA per user)
#[account]
#[derive(Default)]
pub struct AccountState {
    /// Account owner
    pub owner: Pubkey,

    /// Accumulated TCP (scaled by PRECISION)
    pub tcp_balance: u64,

    /// Last interaction timestamp
    pub last_activity: i64,

    /// Cumulative hold duration (seconds)
    pub hold_duration: u64,

    /// Phase lock participation count
    pub phase_locks: u32,

    /// τₖ coefficient (scaled by PRECISION)
    pub tau_k: u64,

    /// Number of windows harvested
    pub windows_harvested: u32,

    /// Bump seed
    pub bump: u8,

    /// Reserved
    pub _reserved: [u8; 32],
}

impl AccountState {
    pub const SIZE: usize = 8 +  // discriminator
        32 +  // owner
        8 +   // tcp_balance
        8 +   // last_activity
        8 +   // hold_duration
        4 +   // phase_locks
        8 +   // tau_k
        4 +   // windows_harvested
        1 +   // bump
        32;   // reserved
}
