# LabuX Deployment Guide - X1 Network

## X1 Overview

X1 is a **Solana Virtual Machine (SVM) compatible** Layer 1 blockchain.

| Property | Value |
|----------|-------|
| VM | SVM (Solana Compatible) |
| Native Token | XN |
| Mainnet RPC | `https://rpc.mainnet.x1.xyz` |
| Testnet RPC | `https://rpc.testnet.x1.xyz` |
| Explorer | `https://explorer.mainnet.x1.xyz` |
| Launched | October 6th, 2025 |

**Key Insight**: Since X1 is SVM-compatible, we use **Solana tooling** (Anchor, Solana CLI, Rust programs) - NOT EVM/Solidity.

---

## Prerequisites

### Install Solana CLI

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Add to PATH
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Verify installation
solana --version
```

### Install Anchor

```bash
# Install Rust if not present
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Anchor
cargo install --git https://github.com/coral-xyz/anchor anchor-cli --locked

# Verify
anchor --version
```

### Configure for X1

```bash
# Create deployer keypair
solana-keygen new --outfile ~/.config/solana/x1-deployer.json

# Configure for X1 Testnet
solana config set --url https://rpc.testnet.x1.xyz
solana config set --keypair ~/.config/solana/x1-deployer.json

# Verify configuration
solana config get

# Check balance (need XN for deployment)
solana balance
```

---

## Project Structure

```
labux-x1/
├── Anchor.toml
├── Cargo.toml
├── programs/
│   └── labux/
│       ├── Cargo.toml
│       └── src/
│           ├── lib.rs
│           ├── state.rs
│           ├── constants.rs
│           ├── errors.rs
│           └── instructions/
│               ├── mod.rs
│               ├── initialize.rs
│               ├── mint.rs
│               ├── burn.rs
│               ├── transfer.rs
│               ├── accrue_tcp.rs
│               └── harvest_tcp.rs
├── tests/
│   └── labux.ts
└── migrations/
    └── deploy.ts
```

---

## Anchor.toml Configuration

```toml
[features]
seeds = false
skip-lint = false

[programs.testnet]
labux = "LABUX111111111111111111111111111111111111111"  # Will be replaced after build

[programs.mainnet]
labux = "LABUX111111111111111111111111111111111111111"

[registry]
url = "https://api.apr.dev"

[provider]
cluster = "https://rpc.testnet.x1.xyz"
wallet = "~/.config/solana/x1-deployer.json"

[scripts]
test = "yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts"

[test]
startup_wait = 5000
shutdown_wait = 2000

# X1 Specific Settings
[programs.localnet]
labux = "LABUX111111111111111111111111111111111111111"

# Custom cluster definitions for X1
[clusters.x1-testnet]
url = "https://rpc.testnet.x1.xyz"

[clusters.x1-mainnet]
url = "https://rpc.mainnet.x1.xyz"
```

---

## Core Program: lib.rs

```rust
use anchor_lang::prelude::*;

pub mod constants;
pub mod errors;
pub mod instructions;
pub mod state;

use instructions::*;

declare_id!("LABUX111111111111111111111111111111111111111");

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
    pub fn initialize(
        ctx: Context<Initialize>,
        window_epoch: i64,
    ) -> Result<()> {
        instructions::initialize::handler(ctx, window_epoch)
    }

    /// Mint LabuX with 1:1 collateral backing
    pub fn mint(
        ctx: Context<MintLabuX>,
        amount: u64,
    ) -> Result<()> {
        instructions::mint::handler(ctx, amount)
    }

    /// Burn LabuX and receive collateral
    pub fn burn(
        ctx: Context<BurnLabuX>,
        amount: u64,
    ) -> Result<()> {
        instructions::burn::handler(ctx, amount)
    }

    /// Transfer LabuX with optional TCP
    pub fn transfer_with_tcp(
        ctx: Context<TransferWithTCP>,
        amount: u64,
        include_tcp: bool,
    ) -> Result<()> {
        instructions::transfer::handler(ctx, amount, include_tcp)
    }

    /// Accrue TCP for an account
    pub fn accrue_tcp(ctx: Context<AccrueTCP>) -> Result<()> {
        instructions::accrue_tcp::handler(ctx)
    }

    /// Harvest TCP during harmonic window
    pub fn harvest_tcp(ctx: Context<HarvestTCP>) -> Result<()> {
        instructions::harvest_tcp::handler(ctx)
    }

    /// Update account τₖ (oracle/governance)
    pub fn update_tau_k(
        ctx: Context<UpdateTauK>,
        new_tau_k: u64,
    ) -> Result<()> {
        instructions::update_tau_k::handler(ctx, new_tau_k)
    }

    /// Record phase lock event
    pub fn record_phase_lock(ctx: Context<RecordPhaseLock>) -> Result<()> {
        instructions::record_phase_lock::handler(ctx)
    }
}
```

---

## Constants: constants.rs

```rust
//! Harmonic constants for the 369-365 system

/// Earth cycle (365 days) - manifest reality
pub const EARTH_CYCLE: u64 = 365;

/// Tesla cycle (369) - ideal harmonic
pub const TESLA_CYCLE: u64 = 369;

/// Precision for fixed-point math (1e9 for Solana compatibility)
pub const PRECISION: u64 = 1_000_000_000;

/// Tesla/Earth ratio = 369/365 * PRECISION
/// = 1.01095890410958904... * 1e9
/// = 1_010_958_904
pub const TESLA_RATIO: u64 = 1_010_958_904;

/// Peg value = $1.00 * PRECISION
pub const PEG_VALUE: u64 = PRECISION;

/// Maximum TCP = Tesla Ratio - Peg
/// = 10_958_904 (~1.096%)
pub const TCP_MAX: u64 = TESLA_RATIO - PEG_VALUE;

/// Quarterly window period (91.25 days in seconds)
pub const QUARTERLY_WINDOW_PERIOD: i64 = 7_884_000;

/// Quarterly window duration (3 days in seconds)
pub const QUARTERLY_WINDOW_DURATION: i64 = 259_200;

/// Micro window period (9.125 days in seconds)
pub const MICRO_WINDOW_PERIOD: i64 = 788_400;

/// Micro window duration (12 hours in seconds)
pub const MICRO_WINDOW_DURATION: i64 = 43_200;

/// Primary window period (92.25 years - for reference)
pub const PRIMARY_WINDOW_YEARS: f64 = 92.25;

/// Minimum τₖ (3.0 * PRECISION)
pub const TAU_K_MIN: u64 = 3 * PRECISION;

/// Maximum τₖ (9.0 * PRECISION)
pub const TAU_K_MAX: u64 = 9 * PRECISION;

/// Default τₖ (7.0 * PRECISION)
pub const TAU_K_DEFAULT: u64 = 7 * PRECISION;

/// Seeds for PDAs
pub mod seeds {
    pub const PROTOCOL_STATE: &[u8] = b"protocol_state";
    pub const ACCOUNT_STATE: &[u8] = b"account_state";
    pub const MINT: &[u8] = b"labux_mint";
    pub const COLLATERAL_VAULT: &[u8] = b"collateral_vault";
}

/// Token decimals (standard for Solana SPL tokens)
pub const TOKEN_DECIMALS: u8 = 9;
```

---

## State: state.rs

```rust
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
```

---

## Errors: errors.rs

```rust
use anchor_lang::prelude::*;

#[error_code]
pub enum LabuXError {
    #[msg("Insufficient balance")]
    InsufficientBalance,

    #[msg("Insufficient collateral")]
    InsufficientCollateral,

    #[msg("Invalid amount - must be greater than zero")]
    InvalidAmount,

    #[msg("Invalid τₖ - must be between 3.0 and 9.0")]
    InvalidTauK,

    #[msg("Not in harmonic window - harvest only available during windows")]
    NotInHarmonicWindow,

    #[msg("No TCP to harvest")]
    NoTCPToHarvest,

    #[msg("Unauthorized")]
    Unauthorized,

    #[msg("Protocol is paused")]
    ProtocolPaused,

    #[msg("Math overflow")]
    MathOverflow,

    #[msg("Math underflow")]
    MathUnderflow,
}
```

---

## Deployment Script

```bash
#!/bin/bash
# deploy-x1.sh - Deploy LabuX to X1 Network

set -e

echo "═══════════════════════════════════════════════════════════════════"
echo "  LabuX Deployment - X1 Network (SVM)"
echo "═══════════════════════════════════════════════════════════════════"

# Configuration
NETWORK=${1:-testnet}

if [ "$NETWORK" = "mainnet" ]; then
    RPC_URL="https://rpc.mainnet.x1.xyz"
    EXPLORER="https://explorer.mainnet.x1.xyz"
else
    RPC_URL="https://rpc.testnet.x1.xyz"
    EXPLORER="https://explorer.testnet.x1.xyz"
fi

echo ""
echo "Network: $NETWORK"
echo "RPC: $RPC_URL"
echo ""

# Configure Solana CLI for X1
solana config set --url $RPC_URL

# Check deployer balance
echo "1. Checking deployer balance..."
BALANCE=$(solana balance)
echo "   Balance: $BALANCE XN"

if [ "$BALANCE" = "0 SOL" ]; then
    echo "   ERROR: Need XN tokens for deployment!"
    echo "   Get testnet XN from X1 faucet"
    exit 1
fi

# Build the program
echo ""
echo "2. Building program..."
anchor build

# Get program ID from keypair
PROGRAM_ID=$(solana-keygen pubkey target/deploy/labux-keypair.json)
echo "   Program ID: $PROGRAM_ID"

# Update lib.rs with correct program ID
echo ""
echo "3. Updating program ID in source..."
sed -i "s/declare_id!(\".*\")/declare_id!(\"$PROGRAM_ID\")/" programs/labux/src/lib.rs

# Rebuild with correct ID
anchor build

# Deploy
echo ""
echo "4. Deploying to X1 $NETWORK..."
anchor deploy --provider.cluster $RPC_URL

# Verify deployment
echo ""
echo "5. Verifying deployment..."
solana program show $PROGRAM_ID

# Initialize protocol
echo ""
echo "6. Initializing protocol..."
WINDOW_EPOCH=$(date +%s)

# Run initialization script
npx ts-node scripts/initialize.ts --epoch $WINDOW_EPOCH

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  Program ID:    $PROGRAM_ID"
echo "  Network:       X1 $NETWORK"
echo "  RPC:           $RPC_URL"
echo "  Explorer:      $EXPLORER/address/$PROGRAM_ID"
echo "  Window Epoch:  $WINDOW_EPOCH"
echo ""
echo "  Harmonic Constants:"
echo "    Tesla Ratio: 1.01095890410958904"
echo "    TCP Max:     1.096%"
echo "    Quarterly:   91.25 days"
echo ""
echo "═══════════════════════════════════════════════════════════════════"

# Save deployment info
mkdir -p deployments

cat > deployments/x1-$NETWORK.json << EOF
{
    "network": "x1-$NETWORK",
    "rpc": "$RPC_URL",
    "programId": "$PROGRAM_ID",
    "windowEpoch": $WINDOW_EPOCH,
    "timestamp": "$(date -Iseconds)",
    "explorer": "$EXPLORER/address/$PROGRAM_ID",
    "harmonicConstants": {
        "teslaRatio": "1010958904",
        "tcpMax": "10958904",
        "precision": "1000000000",
        "quarterlyWindowDays": 91.25,
        "microWindowDays": 9.125
    }
}
EOF

echo "Deployment info saved to deployments/x1-$NETWORK.json"
```

---

## Initialize Script (TypeScript)

```typescript
// scripts/initialize.ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { Labux } from "../target/types/labux";
import {
    PublicKey,
    Keypair,
    SystemProgram,
    SYSVAR_RENT_PUBKEY,
} from "@solana/web3.js";
import {
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
    createMint,
    getOrCreateAssociatedTokenAccount,
} from "@solana/spl-token";

async function main() {
    // Parse args
    const args = process.argv.slice(2);
    const epochIndex = args.indexOf("--epoch");
    const windowEpoch = epochIndex !== -1
        ? parseInt(args[epochIndex + 1])
        : Math.floor(Date.now() / 1000);

    console.log("Initializing LabuX Protocol...");
    console.log(`Window Epoch: ${windowEpoch}`);

    // Setup provider
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    const program = anchor.workspace.Labux as Program<Labux>;
    const authority = provider.wallet.publicKey;

    console.log(`Authority: ${authority.toBase58()}`);
    console.log(`Program ID: ${program.programId.toBase58()}`);

    // Derive PDAs
    const [protocolState, protocolBump] = PublicKey.findProgramAddressSync(
        [Buffer.from("protocol_state")],
        program.programId
    );

    const [labuxMint, mintBump] = PublicKey.findProgramAddressSync(
        [Buffer.from("labux_mint")],
        program.programId
    );

    console.log(`Protocol State PDA: ${protocolState.toBase58()}`);
    console.log(`LabuX Mint PDA: ${labuxMint.toBase58()}`);

    // For testnet, use a mock USDC or create one
    // In production, use actual USDC mint
    const collateralMint = new PublicKey(
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" // USDC on Solana
        // For X1 testnet, you'd use X1's testnet USDC equivalent
    );

    // Derive collateral vault PDA
    const [collateralVault, vaultBump] = PublicKey.findProgramAddressSync(
        [Buffer.from("collateral_vault")],
        program.programId
    );

    // Initialize
    try {
        const tx = await program.methods
            .initialize(new anchor.BN(windowEpoch))
            .accounts({
                authority,
                protocolState,
                labuxMint,
                collateralMint,
                collateralVault,
                systemProgram: SystemProgram.programId,
                tokenProgram: TOKEN_PROGRAM_ID,
                rent: SYSVAR_RENT_PUBKEY,
            })
            .rpc();

        console.log(`\nInitialization TX: ${tx}`);
        console.log("\nProtocol initialized successfully!");

        // Log final state
        const state = await program.account.protocolState.fetch(protocolState);
        console.log("\nProtocol State:");
        console.log(`  Authority: ${state.authority.toBase58()}`);
        console.log(`  LabuX Mint: ${state.labuxMint.toBase58()}`);
        console.log(`  Window Epoch: ${state.windowEpoch.toString()}`);
        console.log(`  Network τₖ: ${state.networkTauK.toString()}`);

    } catch (error) {
        console.error("Initialization failed:", error);
        process.exit(1);
    }
}

main().then(() => process.exit(0));
```

---

## Testing on X1

```bash
# 1. Configure for X1 testnet
solana config set --url https://rpc.testnet.x1.xyz

# 2. Get testnet XN (check X1 docs for faucet)

# 3. Build
anchor build

# 4. Deploy to testnet
./deploy-x1.sh testnet

# 5. Run tests
anchor test --provider.cluster https://rpc.testnet.x1.xyz

# 6. When ready, deploy to mainnet
./deploy-x1.sh mainnet
```

---

## Key Differences from Solana Mainnet

| Aspect | Solana | X1 |
|--------|--------|-----|
| RPC Testnet | `https://api.devnet.solana.com` | `https://rpc.testnet.x1.xyz` |
| RPC Mainnet | `https://api.mainnet-beta.solana.com` | `https://rpc.mainnet.x1.xyz` |
| Native Token | SOL | XN |
| Explorer | solscan.io | explorer.mainnet.x1.xyz |
| VM | SVM | SVM (compatible) |
| Tooling | Solana CLI, Anchor | Same (SVM compatible) |

---

## Summary

X1 is **SVM-compatible**, meaning:

1. ✅ Use **Solana tooling** (Anchor, Solana CLI)
2. ✅ Write programs in **Rust** (not Solidity)
3. ✅ Same account model as Solana
4. ✅ Same SPL token standard
5. ✅ Different RPC endpoints
6. ✅ Native token is **XN**T (not SOL)

```
X1 Network
├── VM: Solana Virtual Machine (SVM)
├── Token: XNT
├── Testnet: https://rpc.testnet.x1.xyz
├── Mainnet: https://rpc.mainnet.x1.xyz
└── Tooling: Anchor, Solana CLI, Rust
```

**LabuX on X1 = Same Solana program, different RPC endpoint.**
