use anchor_lang::prelude::*;
use anchor_spl::token_interface::{self, TransferChecked, TokenAccount, TokenInterface, Mint};
use crate::state::genesis_fund::*;
use crate::constants::{YIELD_FEE_BPS, BPS_DENOMINATOR};

#[derive(Accounts)]
pub struct EmitYield<'info> {
    #[account(mut)]
    pub investor: Signer<'info>,

    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump = fund.bump
    )]
    pub fund: Account<'info, GenesisFund>,

    #[account(
        mut,
        seeds = [b"investor", investor.key().as_ref(), fund.key().as_ref()],
        bump = investor_record.bump,
        constraint = !investor_record.claimed
    )]
    pub investor_record: Account<'info, InvestorRecord>,

    #[account(mut)]
    pub fund_vault: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub investor_token_account: InterfaceAccount<'info, TokenAccount>,

    #[account(mut)]
    pub protocol_fee_vault: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    pub token_program: Interface<'info, TokenInterface>,
}

pub fn handler(ctx: Context<EmitYield>, coherence_score: u16) -> Result<()> {
    let fund = &mut ctx.accounts.fund;
    let record = &mut ctx.accounts.investor_record;

    // 1. Calculate Yield
    // Base Yield = Amount * (Coherence / 1000)
    let base_yield = (record.amount as u128 * coherence_score as u128 / 1000) as u64;

    // 2. Calculate Tier Multiplier based on Entry Mass (Simplified thresholds)
    // Genesis (0-1M): 1.618x
    // Foundation (1M-5M): 1.45x
    // Growth (>5M): 1.0x
    let tier_multiplier = if record.entry_mass < 1_000_000_000 {
         1618 // Scaled by 1000
    } else if record.entry_mass < 5_000_000_000 {
         1450
    } else {
         1000
    };

    let yields_tiered = base_yield as u128 * tier_multiplier as u128 / 1000;

    // 3. Phase Modulation (Original Logic preserved as secondary harmonic)
    let phase_bonus = (yields_tiered * PHI_INV_SCALED as u128 / SCALE as u128) as u64;
    let total_yield = (yields_tiered as u64) + phase_bonus;

    // 4. Calculate fee on total yield
    let fee = total_yield * YIELD_FEE_BPS / BPS_DENOMINATOR;
    let net_yield = total_yield - fee;

    fund.total_fees_collected += fee;

    // 5. Emit
    let seeds = &[b"genesis_fund".as_ref(), &[fund.bump]];
    let signer = &[&seeds[..]];

    // Transfer fee to protocol vault (fund PDA signs)
    if fee > 0 {
        let fee_cpi = TransferChecked {
            from: ctx.accounts.fund_vault.to_account_info(),
            to: ctx.accounts.protocol_fee_vault.to_account_info(),
            authority: fund.to_account_info(),
            mint: ctx.accounts.mint.to_account_info(),
        };
        let fee_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            fee_cpi,
            signer
        );
        token_interface::transfer_checked(fee_ctx, fee, ctx.accounts.mint.decimals)?;
    }

    // Transfer net yield to investor (fund PDA signs)
    let cpi_accounts = TransferChecked {
        from: ctx.accounts.fund_vault.to_account_info(),
        to: ctx.accounts.investor_token_account.to_account_info(),
        authority: fund.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
    };
    let cpi_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        cpi_accounts,
        signer
    );
    token_interface::transfer_checked(cpi_ctx, net_yield, ctx.accounts.mint.decimals)?;

    // 6. Update Record
    record.claimed = true;

    msg!("Hawking Emission: {} (Fee: {}, Net: {})", total_yield, fee, net_yield);

    Ok(())
}
