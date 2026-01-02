use anchor_lang::prelude::*;

pub mod constants;
pub mod errors;
pub mod instructions;
pub mod state;

use instructions::*;

declare_id!("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");

/// LabuX - The Harmonic Constraint Stablecoin
///
/// Pegged to $1.00 (Earth/365) with TCP up to 1.096% (Tesla/369)
///
/// The $1 peg is the EARTH HARMONIC - manifest economic reality.
/// The TCP ceiling is the TESLA HARMONIC - ideal coherent value.
/// The 4-cent gap is CREATIVE TENSION - the engine that makes it work.
#[program]
pub mod labux {
    use super::*;

    /// Initialize the LabuX protocol
    // pub fn initialize(
    //     ctx: Context<Initialize>,
    //     window_epoch: i64,
    // ) -> Result<()> {
    //     instructions::initialize::handler(ctx, window_epoch)
    // }

    /// Mint LabuX with 1:1 collateral backing
    // pub fn mint(
    //     ctx: Context<MintLabuX>,
    //     amount: u64,
    // ) -> Result<()> {
    //     instructions::mint::handler(ctx, amount)
    // }

    /// Burn LabuX and receive collateral
    // pub fn burn(
    //     ctx: Context<BurnLabuX>,
    //     amount: u64,
    // ) -> Result<()> {
    //     instructions::burn::handler(ctx, amount)
    // }

    /// Transfer LabuX with optional TCP
    // pub fn transfer_with_tcp(
    //     ctx: Context<TransferWithTCP>,
    //     amount: u64,
    //     include_tcp: bool,
    // ) -> Result<()> {
    //     instructions::transfer::handler(ctx, amount, include_tcp)
    // }

    /// Accrue TCP for an account
    // pub fn accrue_tcp(ctx: Context<AccrueTCP>) -> Result<()> {
    //     instructions::accrue_tcp::handler(ctx)
    // }

    /// Harvest TCP during harmonic window
    // pub fn harvest_tcp(ctx: Context<HarvestTCP>) -> Result<()> {
    //     instructions::harvest_tcp::handler(ctx)
    // }

    /// Update account τₖ (oracle/governance)
    // pub fn update_tau_k(
    //     ctx: Context<UpdateTauK>,
    //     new_tau_k: u64,
    // ) -> Result<()> {
    //     instructions::update_tau_k::handler(ctx, new_tau_k)
    // }

    /// Record phase lock event
    // pub fn record_phase_lock(ctx: Context<RecordPhaseLock>) -> Result<()> {
    //     instructions::record_phase_lock::handler(ctx)
    // }

    // --- Genesis Fund (PTO²) Instructions ---

    /// Initialize the Temporal Genesis Fund (PTO²)
    /// Must be called once before any other Genesis Fund operations
    pub fn initialize_genesis_fund(ctx: Context<InitializeGenesisFund>) -> Result<()> {
        genesis::initialize::handler(ctx)
    }

    /// Invest in the Temporal Genesis Fund
    pub fn invest_infall(
        ctx: Context<Invest>,
        amount: u64,
    ) -> Result<()> {
        genesis::invest::handler(ctx, amount)
    }

    /// Spawn a new Child PTO
    pub fn spawn_child_pto(
        ctx: Context<SpawnChildPTO>,
        sector: [u8; 16],
        funding_goal: u64,
        coherence_mass: u64,
    ) -> Result<()> {
        genesis::spawn::handler(ctx, sector, funding_goal, coherence_mass)
    }

    /// Emit Hawking Yields
    pub fn emit_hawking_yield(
        ctx: Context<EmitYield>,
        coherence_score: u16,
    ) -> Result<()> {
        genesis::emit::handler(ctx, coherence_score)
    }
}
