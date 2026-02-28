use anchor_lang::prelude::*;
use anchor_lang::system_program;
use anchor_spl::token_interface::{TokenAccount, TokenInterface, Mint};
use crate::state::genesis_fund::GenesisFund;
use crate::errors::LabuXError;

#[derive(Accounts)]
pub struct MigrateGenesisFund<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,

    /// CHECK: Manual realloc + deserialization — existing GenesisFund PDA (65 bytes on chain)
    #[account(
        mut,
        seeds = [b"genesis_fund"],
        bump,
    )]
    pub genesis_fund: UncheckedAccount<'info>,

    #[account(
        init,
        payer = authority,
        seeds = [b"protocol_treasury", genesis_fund.key().as_ref()],
        bump,
        token::mint = mint,
        token::authority = genesis_fund,
        token::token_program = token_program,
    )]
    pub protocol_fee_vault: InterfaceAccount<'info, TokenAccount>,

    pub mint: InterfaceAccount<'info, Mint>,

    pub system_program: Program<'info, System>,
    pub token_program: Interface<'info, TokenInterface>,
    pub rent: Sysvar<'info, Rent>,
}

pub fn handler(ctx: Context<MigrateGenesisFund>) -> Result<()> {
    let genesis_fund = &ctx.accounts.genesis_fund;

    // Verify owned by this program
    require_keys_eq!(*genesis_fund.owner, crate::ID, LabuXError::Unauthorized);

    // Read authority from raw data (bytes 8..40, after 8-byte discriminator)
    let data = genesis_fund.try_borrow_data()?;
    require!(data.len() >= 65, LabuXError::Unauthorized);

    let authority_bytes: [u8; 32] = data[8..40].try_into().unwrap();
    let stored_authority = Pubkey::new_from_array(authority_bytes);
    require_keys_eq!(stored_authority, ctx.accounts.authority.key(), LabuXError::Unauthorized);
    drop(data);

    // Realloc: 65 -> 106 bytes (zero-init new region)
    let new_size = GenesisFund::SIZE;
    genesis_fund.realloc(new_size, true)?;

    // Transfer additional rent to cover the extra bytes
    let rent = Rent::get()?;
    let new_minimum = rent.minimum_balance(new_size);
    let lamports_diff = new_minimum.saturating_sub(genesis_fund.lamports());
    if lamports_diff > 0 {
        system_program::transfer(
            CpiContext::new(
                ctx.accounts.system_program.to_account_info(),
                system_program::Transfer {
                    from: ctx.accounts.authority.to_account_info(),
                    to: genesis_fund.to_account_info(),
                },
            ),
            lamports_diff,
        )?;
    }

    // Write new fields into extended region
    let vault_key = ctx.accounts.protocol_fee_vault.key();
    let mut data = genesis_fund.try_borrow_mut_data()?;
    // protocol_treasury: bytes 65..97
    data[65..97].copy_from_slice(vault_key.as_ref());
    // total_fees_collected: bytes 97..105 (u64 = 0, already zeroed)
    data[97..105].copy_from_slice(&0u64.to_le_bytes());
    // paused: byte 105 (false, already zeroed)
    data[105] = 0;

    msg!("Migration complete!");
    msg!("  Protocol treasury: {}", vault_key);
    msg!("  Size: {} -> {} bytes", 65, new_size);

    Ok(())
}
