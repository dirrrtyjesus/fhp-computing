use anchor_lang::prelude::*;
use anchor_spl::token_interface::{self, TransferChecked, TokenAccount, TokenInterface, Mint};
use crate::state::genesis_fund::*;

use crate::constants::{TGF_MINT_STRING, DEPOSIT_FEE_BPS, BPS_DENOMINATOR};
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
    pub investor_token_account: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub fund_vault: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub protocol_fee_vault: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    pub token_program: Interface<'info, TokenInterface>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<Invest>, amount: u64) -> Result<()> {
    // Validate Mint (Security Check)
    // NOTE: For testing on devnet/localhost, this check can be bypassed by
    // building with: anchor build -- --features skip-mint-check
    #[cfg(not(feature = "skip-mint-check"))]
    {
        let incoming_mint = ctx.accounts.investor_token_account.mint;
        let expected_mint = Pubkey::from_str(TGF_MINT_STRING).unwrap();
        require_keys_eq!(incoming_mint, expected_mint, LabuXError::InvalidTokenMint);
    }

    let fund = &mut ctx.accounts.fund;
    require!(!fund.paused, LabuXError::ProtocolPaused);
    let investor_record = &mut ctx.accounts.investor_record;

    // 1. Calculate Fee
    let fee = amount * DEPOSIT_FEE_BPS / BPS_DENOMINATOR;
    let net_amount = amount - fee;

    // 2. Calculate Golden Split on net amount
    // Core = 61.8% (φ⁻¹)
    let core_share = (net_amount as u128 * PHI_INV_SCALED as u128 / SCALE as u128) as u64;
    let allocation_share = net_amount - core_share;

    // 3. Update Fund State
    fund.core_treasury += core_share;
    fund.allocation_pool += allocation_share;
    fund.total_mass += net_amount;
    fund.total_fees_collected += fee;

    // 4. Record Phase Data
    let clock = Clock::get()?;
    let phase = (clock.slot % 360) as u16;

    investor_record.investor = ctx.accounts.investor.key();
    investor_record.amount += net_amount;
    investor_record.phase = phase;
    investor_record.timestamp = clock.unix_timestamp;
    investor_record.claimed = false;
    investor_record.entry_mass = fund.total_mass;

    // 5. Transfer fee to protocol vault (investor signs)
    if fee > 0 {
        let fee_cpi = TransferChecked {
            from: ctx.accounts.investor_token_account.to_account_info(),
            to: ctx.accounts.protocol_fee_vault.to_account_info(),
            authority: ctx.accounts.investor.to_account_info(),
            mint: ctx.accounts.mint.to_account_info(),
        };
        let fee_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), fee_cpi);
        token_interface::transfer_checked(fee_ctx, fee, ctx.accounts.mint.decimals)?;
    }

    // 6. Transfer net amount to fund vault (investor signs)
    let cpi_accounts = TransferChecked {
        from: ctx.accounts.investor_token_account.to_account_info(),
        to: ctx.accounts.fund_vault.to_account_info(),
        authority: ctx.accounts.investor.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
    };
    let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
    token_interface::transfer_checked(cpi_ctx, net_amount, ctx.accounts.mint.decimals)?;

    msg!("Genesis Infall: {} (Fee: {}, Net: {}, Phase: {}°)", amount, fee, net_amount, phase);
    msg!("Core: {} | Alloc: {}", core_share, allocation_share);

    Ok(())
}
