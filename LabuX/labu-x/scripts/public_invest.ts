/**
 * Public Genesis Fund Investment Script
 *
 * Usage:
 *   npx ts-node scripts/public_invest.ts <WALLET_PATH> <AMOUNT_TGF>
 *
 * Example:
 *   npx ts-node scripts/public_invest.ts ~/.config/solana/id.json 50000
 */

import * as anchor from "@coral-xyz/anchor";
import { Program, AnchorProvider, Wallet } from "@coral-xyz/anchor";
import { Connection, PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import {
  getAssociatedTokenAddress,
  TOKEN_2022_PROGRAM_ID,
  createAssociatedTokenAccountInstruction,
} from "@solana/spl-token";
import fs from "fs";
import path from "path";

// Program and Mint Constants
const PROGRAM_ID = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");
const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");
const RPC_ENDPOINT = process.env.RPC_ENDPOINT || "https://api.mainnet-beta.solana.com";

async function investInGenesisFund(walletPath: string, amountTGF: number) {
  console.log("🌌 Genesis Fund Investment Script");
  console.log("=====================================");

  // Load wallet
  const walletKeypair = Keypair.fromSecretKey(
    new Uint8Array(JSON.parse(fs.readFileSync(walletPath, "utf-8")))
  );
  console.log(`📍 Investor: ${walletKeypair.publicKey.toString()}`);

  // Setup connection
  const connection = new Connection(RPC_ENDPOINT, "confirmed");
  const wallet = new Wallet(walletKeypair);
  const provider = new AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });

  // Load IDL
  const idlPath = path.join(__dirname, "../target/idl/labux.json");
  const idl = JSON.parse(fs.readFileSync(idlPath, "utf-8"));
  const program = new Program(idl, provider);

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

  // Get token accounts
  const fundVault = await getAssociatedTokenAddress(
    TGF_MINT,
    fundPda,
    true,
    TOKEN_2022_PROGRAM_ID
  );

  const investorTokenAccount = await getAssociatedTokenAddress(
    TGF_MINT,
    walletKeypair.publicKey,
    false,
    TOKEN_2022_PROGRAM_ID
  );

  // Check balances
  try {
    const balance = await connection.getTokenAccountBalance(investorTokenAccount);
    const balanceTGF = balance.value.uiAmount || 0;
    console.log(`💎 Your $TGF Balance: ${balanceTGF.toLocaleString()}`);

    if (balanceTGF < amountTGF) {
      console.error(`❌ Insufficient balance. You need ${amountTGF} $TGF but have ${balanceTGF}`);
      process.exit(1);
    }
  } catch (e) {
    console.error("❌ No $TGF tokens found in your wallet");
    process.exit(1);
  }

  // Check if fund vault exists, create if needed
  const vaultInfo = await connection.getAccountInfo(fundVault);
  if (!vaultInfo) {
    console.log("⚙️  Creating fund vault...");
    const createVaultIx = createAssociatedTokenAccountInstruction(
      walletKeypair.publicKey,
      fundVault,
      fundPda,
      TGF_MINT,
      TOKEN_2022_PROGRAM_ID
    );
    const tx = new anchor.web3.Transaction().add(createVaultIx);
    const sig = await provider.sendAndConfirm(tx);
    console.log(`✅ Vault created: ${sig}`);
  }

  // Execute investment
  console.log(`\n🚀 Investing ${amountTGF.toLocaleString()} $TGF...`);
  const investAmount = new anchor.BN(amountTGF * 1_000_000);

  const tx = await program.methods
    .investInfall(investAmount)
    .accounts({
      investor: walletKeypair.publicKey,
      fund: fundPda,
      investorRecord: investorRecordPda,
      investorTokenAccount: investorTokenAccount,
      fundVault: fundVault,
      mint: TGF_MINT,
      tokenProgram: TOKEN_2022_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    })
    .rpc();

  console.log("\n✅ TEMPORAL INFALL SUCCESSFUL!");
  console.log("=====================================");
  console.log(`📊 Investment: ${amountTGF.toLocaleString()} $TGF`);
  console.log(`🏛️  Core Treasury (61.8%): ${(amountTGF * 0.618).toFixed(2)} $TGF`);
  console.log(`🌊 Allocation Pool (38.2%): ${(amountTGF * 0.382).toFixed(2)} $TGF`);
  console.log(`\n🔗 Transaction: https://solscan.io/tx/${tx}`);
  console.log("\n🌌 You are now phase-locked in the Genesis Fund!");
}

// Main
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log("Usage: npx ts-node scripts/public_invest.ts <WALLET_PATH> <AMOUNT_TGF>");
  console.log("\nExample:");
  console.log("  npx ts-node scripts/public_invest.ts ~/.config/solana/id.json 50000");
  console.log("\nEnvironment:");
  console.log("  RPC_ENDPOINT - Custom RPC (optional, defaults to public mainnet)");
  process.exit(1);
}

const walletPath = args[0];
const amountTGF = parseFloat(args[1]);

if (isNaN(amountTGF) || amountTGF <= 0) {
  console.error("❌ Amount must be a positive number");
  process.exit(1);
}

investInGenesisFund(walletPath, amountTGF)
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Investment failed:", error);
    process.exit(1);
  });
