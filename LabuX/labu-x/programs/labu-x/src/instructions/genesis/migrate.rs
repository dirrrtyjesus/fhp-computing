use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount, Mint};
use crate::state::genesis_fund::GenesisFund;

#[derive(Accounts)]
pub struct MigrateGenesisFund<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump = genesis_fund.bump,
        realloc = GenesisFund::SIZE,
        realloc::payer = authority,
        realloc::zero = false,
        has_one = authority
    )]
    pub genesis_fund: Account<'info, GenesisFund>,

    #[account(
        init,
        payer = authority,
        seeds = [b"protocol_treasury", genesis_fund.key().as_ref()],
        bump,
        token::mint = mint,
        token::authority = genesis_fund,
    )]
    pub protocol_fee_vault: Account<'info, TokenAccount>,

    pub mint: Account<'info, Mint>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

pub fn handler(ctx: Context<MigrateGenesisFund>) -> Result<()> {
    let fund = &mut ctx.accounts.genesis_fund;

    fund.protocol_treasury = ctx.accounts.protocol_fee_vault.key();
    fund.total_fees_collected = 0;
    fund.paused = false;

    msg!("Migration complete!");
    msg!("  Protocol treasury: {}", fund.protocol_treasury);
    msg!("  Paused: false");

    Ok(())
}
