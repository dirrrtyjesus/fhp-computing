import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
// import { LabuX } from "../target/types/labu_x"; // Types not generated yet
import { PublicKey, SystemProgram } from "@solana/web3.js";
import {
    getAssociatedTokenAddress,
    TOKEN_PROGRAM_ID,
    createAssociatedTokenAccountInstruction,
    createInitializeMintInstruction,
    createMintToInstruction
} from "@solana/spl-token";

// Config: Amount to ignite (adjust as needed)
// 10,000 TGF tokens (with 6 decimals)
const IGNITION_AMOUNT = new anchor.BN(10_000 * 1_000_000);

const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");

async function main() {
    // 0. Set Defaults for Environment Variables
    if (!process.env.ANCHOR_PROVIDER_URL) {
        process.env.ANCHOR_PROVIDER_URL = "http://127.0.0.1:8899";
    }
    if (!process.env.ANCHOR_WALLET) {
        const home = process.env.HOME || "/home/augmntd";
        process.env.ANCHOR_WALLET = `${home}/.config/solana/id.json`;
    }

    // 1. Setup Environment
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    // Load program - Fallback to manual IDL loading for reliability
    const idl = require("../target/idl/labux.json");
    const programId = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");
    const program = new Program(idl, provider);

    console.log("🚀 Starting Genesis Ignition Sequence...");
    console.log("RPC Endpoint:", provider.connection.rpcEndpoint);

    try {
        const slot = await provider.connection.getSlot();
        console.log("Connection verified. Current Slot:", slot);
    } catch (e) {
        console.error("❌ Failed to connect to Solana cluster at", provider.connection.rpcEndpoint);
        console.error("Make sure `solana-test-validator` is running if using localhost.");
        process.exit(1);
    }

    console.log("Wallet:", provider.wallet.publicKey.toBase58());

    // 1.5 Verify Mint Existence
    let mintToUse = TGF_MINT;
    if (process.env.TGF_MINT) {
        mintToUse = new PublicKey(process.env.TGF_MINT);
        console.log("Using constrained Mint from ENV:", mintToUse.toBase58());
    } else {
        console.log("Using hardcoded Mint:", mintToUse.toBase58());
    }

    const mintInfo = await provider.connection.getAccountInfo(mintToUse);
    if (!mintInfo) {
        if (provider.connection.rpcEndpoint.includes("127.0.0.1") || provider.connection.rpcEndpoint.includes("localhost")) {
            console.log("⚠️ Mint not found on Localhost. Creating Mock TGF Mint...");
            const mintKeypair = anchor.web3.Keypair.generate();

            // Create Mint
            const lamports = await provider.connection.getMinimumBalanceForRentExemption(82);
            const createMintTx = new anchor.web3.Transaction().add(
                anchor.web3.SystemProgram.createAccount({
                    fromPubkey: provider.wallet.publicKey,
                    newAccountPubkey: mintKeypair.publicKey,
                    space: 82,
                    lamports,
                    programId: TOKEN_PROGRAM_ID,
                }),
                createInitializeMintInstruction(
                    mintKeypair.publicKey,
                    6,
                    provider.wallet.publicKey,
                    provider.wallet.publicKey
                )
            );
            await provider.sendAndConfirm(createMintTx, [mintKeypair]);
            console.log("✅ Mock TGF Mint Created:", mintKeypair.publicKey.toBase58());
            mintToUse = mintKeypair.publicKey;

            // Mint Tokens to Wallet (for Injection)
            const walletAta = await getAssociatedTokenAddress(mintToUse, provider.wallet.publicKey);
            const mintCtx = new anchor.web3.Transaction().add(
                createAssociatedTokenAccountInstruction(
                    provider.wallet.publicKey, walletAta, provider.wallet.publicKey, mintToUse
                ),
                createMintToInstruction(
                    mintToUse, walletAta, provider.wallet.publicKey, IGNITION_AMOUNT.toNumber() * 2 // Mint extra just in case
                )
            );
            await provider.sendAndConfirm(mintCtx);
            console.log(`✅ Minted ${IGNITION_AMOUNT.toNumber() / 1_000_000} Mock TGF to wallet.`);

        } else {
            console.error("❌ ERROR: Mint account not found on this cluster!");
            console.error("The hardcoded mint (2M7H...) likely implies Mainnet.");
            process.exit(1);
        }
    } else if (!mintInfo.owner.equals(TOKEN_PROGRAM_ID)) {
        console.error("❌ ERROR: Mint is not owned by Token Program!");
        console.error("Owner:", mintInfo.owner.toBase58());
        process.exit(1);
    }
    console.log("✅ Mint verified:", mintToUse.toBase58());

    // Update constant usage below to `mintToUse`


    // 2. Derive PDAs
    const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("genesis_fund")],
        program.programId
    );

    const [investorRecordPda] = PublicKey.findProgramAddressSync(
        [
            Buffer.from("investor"),
            provider.wallet.publicKey.toBuffer(),
            fundPda.toBuffer()
        ],
        program.programId
    );

    // Derive Vaults (ATA or otherwise)
    // For `fund_vault`, let's assume it's an ATA owned by the Fund PDA?
    // Wait, looking at `invest.rs`: 
    // pub fund_vault: Account<'info, TokenAccount>
    // It doesn't use `init`... it expects it to exist.
    // BUT: usually the vault might be an ATA of the PDA.
    // Let's derive the ATA for the Fund PDA.
    const fundVault = await getAssociatedTokenAddress(
        mintToUse,
        fundPda,
        true // allowOwnerOffCurve = true for PDAs
    );

    const walletAta = await getAssociatedTokenAddress(
        mintToUse,
        provider.wallet.publicKey
    );

    console.log("Fund PDA:", fundPda.toBase58());
    console.log("Fund Vault (ATA):", fundVault.toBase58());
    console.log("Investor Record:", investorRecordPda.toBase58());

    // 3. Check & Create Fund Vault (if missing)
    const vaultInfo = await provider.connection.getAccountInfo(fundVault);
    if (!vaultInfo) {
        console.log("⚠️ Fund Vault ATA not found. Creating...");
        try {
            const createAtax = new anchor.web3.Transaction().add(
                createAssociatedTokenAccountInstruction(
                    provider.wallet.publicKey, // payer
                    fundVault, // associatedToken
                    fundPda, // owner
                    mintToUse // mint
                )
            );
            await provider.sendAndConfirm(createAtax);
            console.log("✅ Fund Vault ATA Created.");
        } catch (err) {
            console.error("❌ Failed to create Fund Vault ATA:", err);
            return;
        }
    } else {
        console.log("✅ Fund Vault ATA exists.");
    }

    // 4. Initialize Genesis Fund (if not already initialized)
    const fundInfo = await provider.connection.getAccountInfo(fundPda);
    if (!fundInfo) {
        console.log("⚠️ Genesis Fund not initialized. Initializing...");
        try {
            const initTx = await program.methods
                .initializeGenesisFund()
                .accounts({
                    authority: provider.wallet.publicKey,
                    fund: fundPda,
                    systemProgram: SystemProgram.programId,
                })
                .rpc();
            console.log("✅ Genesis Fund Initialized. Tx:", initTx);
        } catch (err) {
            console.error("❌ Failed to initialize Genesis Fund:", err);
            return;
        }
    } else {
        console.log("✅ Genesis Fund already initialized.");
    }

    // 5. Execute Ignition (Invest)
    try {
        const tx = await program.methods
            .investInfall(IGNITION_AMOUNT)
            .accounts({
                investor: provider.wallet.publicKey,
                fund: fundPda,
                investorRecord: investorRecordPda,
                investorTokenAccount: walletAta,
                fundVault: fundVault,
                tokenProgram: TOKEN_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        console.log("✅ IGNITION SUCCESSFUL");
        console.log("Tx Signature:", tx);
        console.log("The Basin is Open. Phase 0 Locked.");
    } catch (error) {
        console.error("❌ IGNITION FAILED:", error);
        console.log("Note: Ensure you have minted tokens to your wallet and created the Fund Vault ATA if it doesn't exist.");
    }
}

main();
