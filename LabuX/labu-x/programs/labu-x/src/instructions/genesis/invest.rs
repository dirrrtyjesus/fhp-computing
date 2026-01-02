use anchor_lang::prelude::*;
use anchor_spl::token::{self, Transfer, Token, TokenAccount};
use crate::state::genesis_fund::*;

use crate::constants::TGF_MINT_STRING;
use crate::errors::LabuXError;
use std::str::FromStr;

#[derive(Accounts)]
pub struct Invest<'info> {
    #[account(mut)]
    pub investor: Signer<'info>,

    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump = fund.bump
    )]
    pub fund: Account<'info, GenesisFund>,

    #[account(
        init_if_needed,
        payer = investor,
        space = InvestorRecord::SIZE,
        seeds = [b"investor", investor.key().as_ref(), fund.key().as_ref()],
        bump
    )]
    pub investor_record: Account<'info, InvestorRecord>,

    #[account(mut)]
    pub investor_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub fund_vault: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<Invest>, amount: u64) -> Result<()> {
    // Validate Mint (Security Check)
    let incoming_mint = ctx.accounts.investor_token_account.mint;
    let expected_mint = Pubkey::from_str(TGF_MINT_STRING).unwrap();
    require_keys_eq!(incoming_mint, expected_mint, LabuXError::InvalidTokenMint);

    let fund = &mut ctx.accounts.fund;
    let investor_record = &mut ctx.accounts.investor_record;

    // 1. Calculate Golden Split
    // Core = 61.8% (φ⁻¹)
    let core_share = (amount as u128 * PHI_INV_SCALED as u128 / SCALE as u128) as u64;
    let allocation_share = amount - core_share;

    // 2. Update Fund State
    fund.core_treasury += core_share;
    fund.allocation_pool += allocation_share;
    fund.total_mass += amount;

    // 3. Record Phase Data
    let clock = Clock::get()?;
    let phase = (clock.slot % 360) as u16;

    // If existing record, weight average the phase (simplified: just update for now)
    // Ideally, we'd have a list or weighted avg logic.
    // For MVP: Overwrite/Update timestamp and amount
    investor_record.investor = ctx.accounts.investor.key();
    investor_record.amount += amount;
    investor_record.phase = phase; // Simplified: New phase overwrites
    investor_record.timestamp = clock.unix_timestamp;
    investor_record.claimed = false;
    investor_record.entry_mass = fund.total_mass;

    // 4. Transfer Tokens
    let cpi_accounts = Transfer {
        from: ctx.accounts.investor_token_account.to_account_info(),
        to: ctx.accounts.fund_vault.to_account_info(),
        authority: ctx.accounts.investor.to_account_info(),
    };
    let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
    token::transfer(cpi_ctx, amount)?;

    msg!("Genesis Infall: {} (Phase: {}°)", amount, phase);
    msg!("Core: {} | Alloc: {}", core_share, allocation_share);

    Ok(())
}
