import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, SystemProgram, Keypair } from "@solana/web3.js";
import {
    getAssociatedTokenAddress,
    TOKEN_2022_PROGRAM_ID,
    createAssociatedTokenAccountInstruction,
} from "@solana/spl-token";
import * as fs from "fs";

// Config
const IGNITION_AMOUNT = new anchor.BN(10_000 * 1_000_000); // 10,000 TGF
const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");
const PROGRAM_ID = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");

async function main() {
    // Get wallet path from command line or env
    const walletPath = process.argv[2] || process.env.WALLET_PATH;
    if (!walletPath) {
        console.error("❌ Error: Wallet path required");
        console.log("Usage: npx ts-node scripts/invest_from_wallet.ts <path-to-wallet.json>");
        console.log("Or set WALLET_PATH environment variable");
        process.exit(1);
    }

    // Load wallet keypair
    console.log("📁 Loading wallet from:", walletPath);
    const walletKeypair = Keypair.fromSecretKey(
        new Uint8Array(JSON.parse(fs.readFileSync(walletPath, "utf-8")))
    );
    console.log("👤 Wallet Address:", walletKeypair.publicKey.toBase58());

    // Setup provider with custom wallet
    const connection = new anchor.web3.Connection(
        process.env.ANCHOR_PROVIDER_URL || "https://api.mainnet-beta.solana.com",
        "confirmed"
    );

    const wallet = new anchor.Wallet(walletKeypair);
    const provider = new anchor.AnchorProvider(connection, wallet, {
        commitment: "confirmed",
    });
    anchor.setProvider(provider);

    // Load program
    const idl = require("../target/idl/labux.json");
    const program = new Program(idl, provider);

    console.log("🚀 Starting Genesis Ignition from Custom Wallet...");
    console.log("RPC:", connection.rpcEndpoint);

    // Check SOL balance
    const balance = await connection.getBalance(walletKeypair.publicKey);
    console.log("💰 SOL Balance:", balance / 1e9, "SOL");
    if (balance < 0.1 * 1e9) {
        console.warn("⚠️  Low SOL balance. You may need more for transaction fees.");
    }

    // Derive PDAs
    const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("genesis_fund")],
        PROGRAM_ID
    );

    const [investorRecordPda] = PublicKey.findProgramAddressSync(
        [
            Buffer.from("investor"),
            walletKeypair.publicKey.toBuffer(),
            fundPda.toBuffer(),
        ],
        PROGRAM_ID
    );

    const fundVault = await getAssociatedTokenAddress(
        TGF_MINT,
        fundPda,
        true, // allowOwnerOffCurve
        TOKEN_2022_PROGRAM_ID
    );

    const walletAta = await getAssociatedTokenAddress(
        TGF_MINT,
        walletKeypair.publicKey,
        false,
        TOKEN_2022_PROGRAM_ID
    );

    console.log("📍 Fund PDA:", fundPda.toBase58());
    console.log("📍 Fund Vault:", fundVault.toBase58());
    console.log("📍 Investor Record:", investorRecordPda.toBase58());

    // Check TGF balance
    try {
        const tokenAccountInfo = await connection.getTokenAccountBalance(walletAta);
        const tgfBalance = tokenAccountInfo.value.uiAmount;
        console.log(`💎 $TGF Balance: ${tgfBalance} TGF`);

        if (!tgfBalance || tgfBalance < IGNITION_AMOUNT.toNumber() / 1_000_000) {
            console.error(`❌ Insufficient $TGF balance. Need at least ${IGNITION_AMOUNT.toNumber() / 1_000_000} TGF`);
            process.exit(1);
        }
    } catch (e) {
        console.error("❌ No $TGF token account found or balance check failed");
        console.error("Make sure you have $TGF tokens in this wallet");
        process.exit(1);
    }

    // Check if fund vault exists, create if needed
    const vaultInfo = await connection.getAccountInfo(fundVault);
    if (!vaultInfo) {
        console.log("⚠️  Fund Vault ATA not found. Creating...");
        const createAtaIx = createAssociatedTokenAccountInstruction(
            walletKeypair.publicKey, // payer
            fundVault, // ata
            fundPda, // owner
            TGF_MINT, // mint
            TOKEN_2022_PROGRAM_ID
        );
        const tx = new anchor.web3.Transaction().add(createAtaIx);
        const sig = await provider.sendAndConfirm(tx);
        console.log("✅ Fund Vault ATA Created:", sig);
    } else {
        console.log("✅ Fund Vault ATA exists");
    }

    // Initialize Genesis Fund if needed
    const fundInfo = await connection.getAccountInfo(fundPda);
    if (!fundInfo) {
        console.log("⚠️  Genesis Fund not initialized. Initializing...");
        try {
            const initTx = await program.methods
                .initializeGenesisFund()
                .accounts({
                    authority: walletKeypair.publicKey,
                    fund: fundPda,
                    systemProgram: SystemProgram.programId,
                })
                .rpc();
            console.log("✅ Genesis Fund Initialized:", initTx);
        } catch (err: any) {
            console.error("❌ Failed to initialize Genesis Fund:", err.message);
            process.exit(1);
        }
    } else {
        console.log("✅ Genesis Fund already initialized");
    }

    // Execute Investment
    console.log(`\n🌌 Executing Temporal Infall: ${IGNITION_AMOUNT.toNumber() / 1_000_000} $TGF`);
    try {
        const tx = await program.methods
            .investInfall(IGNITION_AMOUNT)
            .accounts({
                investor: walletKeypair.publicKey,
                fund: fundPda,
                investorRecord: investorRecordPda,
                investorTokenAccount: walletAta,
                fundVault: fundVault,
                mint: TGF_MINT,
                tokenProgram: TOKEN_2022_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        console.log("\n✅ IGNITION SUCCESSFUL!");
        console.log("📜 Transaction:", tx);
        console.log("🔗 Explorer:", `https://solscan.io/tx/${tx}`);
        console.log("\n🌌 The Basin is Open. Phase Locked.");
        console.log("⏰ You are now a Genesis Temporal Attractor.");
    } catch (error: any) {
        console.error("\n❌ IGNITION FAILED:", error.message);
        if (error.logs) {
            console.error("Program Logs:");
            error.logs.forEach((log: string) => console.error(log));
        }
        process.exit(1);
    }
}

main();
