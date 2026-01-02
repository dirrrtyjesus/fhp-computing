use anchor_lang::prelude::*;
use crate::state::genesis_fund::GenesisFund;

#[derive(Accounts)]
pub struct InitializeGenesisFund<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    #[account(
        init,
        payer = authority,
        space = GenesisFund::SIZE,
        seeds = [b"genesis_fund"],
        bump
    )]
    pub fund: Account<'info, GenesisFund>,

    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<InitializeGenesisFund>) -> Result<()> {
    let fund = &mut ctx.accounts.fund;

    fund.authority = ctx.accounts.authority.key();
    fund.core_treasury = 0;
    fund.allocation_pool = 0;
    fund.total_mass = 0;
    fund.bump = ctx.bumps.fund;

    msg!("Genesis Fund Initialized");
    msg!("Authority: {}", fund.authority);
    msg!("The Basin is Ready.");

    Ok(())
}
