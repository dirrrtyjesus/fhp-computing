use anchor_lang::prelude::*;
use crate::state::genesis_fund::GenesisFund;

#[derive(Accounts)]
pub struct EmergencyPause<'info> {
    pub authority: Signer<'info>,

    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump = genesis_fund.bump,
        has_one = authority
    )]
    pub genesis_fund: Account<'info, GenesisFund>,
}

pub fn pause_handler(ctx: Context<EmergencyPause>) -> Result<()> {
    ctx.accounts.genesis_fund.paused = true;
    msg!("Protocol PAUSED by authority");
    Ok(())
}

pub fn unpause_handler(ctx: Context<EmergencyPause>) -> Result<()> {
    ctx.accounts.genesis_fund.paused = false;
    msg!("Protocol UNPAUSED by authority");
    Ok(())
}
