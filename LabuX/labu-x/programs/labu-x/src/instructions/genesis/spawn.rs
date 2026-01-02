use anchor_lang::prelude::*;
use anchor_spl::token_interface::{self, TransferChecked, TokenAccount, TokenInterface, Mint};
use crate::state::genesis_fund::*;
use crate::errors::LabuXError;

#[derive(Accounts)]
#[instruction(sector: [u8; 16], funding_goal: u64, coherence_mass: u64)]
pub struct SpawnChildPTO<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump = fund.bump,
        has_one = authority
    )]
    pub fund: Account<'info, GenesisFund>,

    #[account(
        init,
        payer = authority,
        space = ChildPTO::SIZE,
        seeds = [b"child_pto", creator.key().as_ref(), sector.as_ref()],
        bump
    )]
    pub child_pto: Account<'info, ChildPTO>,

    /// CHECK: The creator of the child project - only used for PDA derivation and recording
    pub creator: UncheckedAccount<'info>,

    #[account(mut)]
    pub fund_vault: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub child_vault: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    pub token_program: Interface<'info, TokenInterface>,
    pub system_program: Program<'info, System>,
}

pub fn handler(
    ctx: Context<SpawnChildPTO>,
    sector: [u8; 16],
    funding_goal: u64,
    coherence_mass: u64
) -> Result<()> {
    let fund = &mut ctx.accounts.fund;
    let child = &mut ctx.accounts.child_pto;

    // 1. Calculate Seed Capital
    // Cap A: 38.2% of Funding Goal
    let cap_a = (funding_goal as u128 * ALLOCATION_RATIO_SCALED as u128 / SCALE as u128) as u64;
    // Cap B: 10% of Allocation Pool
    let cap_b = fund.allocation_pool / 10;
    
    // Seed = min(Cap A, Cap B)
    let seed_capital = std::cmp::min(cap_a, cap_b);
    
    // Safety check: must be > 0
    require!(seed_capital > 0, LabuXError::InsufficientBasinDepth);

    // 2. Transfer Seed
    fund.allocation_pool -= seed_capital;

    let seeds = &[b"genesis_fund".as_ref(), &[fund.bump]];
    let signer = &[&seeds[..]];

    let cpi_accounts = TransferChecked {
        from: ctx.accounts.fund_vault.to_account_info(),
        to: ctx.accounts.child_vault.to_account_info(),
        authority: fund.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
    };
    let cpi_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        cpi_accounts,
        signer
    );
    token_interface::transfer_checked(cpi_ctx, seed_capital, ctx.accounts.mint.decimals)?;

    // 3. Initialize Child
    child.creator = ctx.accounts.creator.key();
    child.sector = sector;
    child.funding_goal = funding_goal;
    child.coherence_mass = coherence_mass;
    child.seed_capital = seed_capital;
    child.emission_active = false;
    child.coherence_score = 0;
    child.bump = ctx.bumps.child_pto;

    msg!("Spawned Child PTO in sector {:?}", sector);
    msg!("Seed: {}", seed_capital);

    Ok(())
}
