// scripts/initialize.ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { Labux } from "../target/types/labu-x";
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
