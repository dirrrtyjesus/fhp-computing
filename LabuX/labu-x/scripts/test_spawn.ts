import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, SystemProgram, Keypair } from "@solana/web3.js";
import {
    getAssociatedTokenAddressSync,
    createAssociatedTokenAccountInstruction,
    TOKEN_2022_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
} from "@solana/spl-token";

const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");

async function main() {
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    const idl = require("../target/idl/labux.json");
    const programId = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");
    const program = new Program(idl, provider);

    const authority = provider.wallet.publicKey;

    // Sector: pad "DeFi" to 16 bytes
    const sectorStr = "DeFi";
    const sector = Buffer.alloc(16, 0);
    sector.write(sectorStr);

    const fundingGoal = new anchor.BN(10_000_000_000); // 10,000 TGF
    const coherenceMass = new anchor.BN(500);

    console.log("=== Test Spawn with Fees ===");
    console.log("Authority:", authority.toBase58());
    console.log("Sector:", sectorStr);
    console.log("Funding Goal:", fundingGoal.toString());

    // Use a deterministic "creator" so the PDA is predictable
    const creator = Keypair.generate();
    console.log("Creator:", creator.publicKey.toBase58());

    // Derive PDAs
    const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("genesis_fund")],
        programId
    );
    const [childPto] = PublicKey.findProgramAddressSync(
        [Buffer.from("child_pto"), creator.publicKey.toBuffer(), sector],
        programId
    );

    const fundVault = getAssociatedTokenAddressSync(TGF_MINT, fundPda, true, TOKEN_2022_PROGRAM_ID);
    const protocolFeeVault = new PublicKey("ibSDt4dsPu4ZTF2U4gisQrWFa9iWmBpFCs4cPiGmsfP");

    // Create child vault ATA for the creator
    const childVault = getAssociatedTokenAddressSync(TGF_MINT, creator.publicKey, true, TOKEN_2022_PROGRAM_ID);

    console.log("Fund PDA:", fundPda.toBase58());
    console.log("Child PTO PDA:", childPto.toBase58());
    console.log("Child Vault ATA:", childVault.toBase58());

    // Create child vault ATA first
    const createAtaTx = new anchor.web3.Transaction().add(
        createAssociatedTokenAccountInstruction(
            authority,
            childVault,
            creator.publicKey,
            TGF_MINT,
            TOKEN_2022_PROGRAM_ID,
            ASSOCIATED_TOKEN_PROGRAM_ID,
        )
    );
    const ataSignature = await provider.sendAndConfirm(createAtaTx);
    console.log("Child Vault ATA created:", ataSignature);

    // Read fund state to calculate expected seed capital
    const fundInfo = await provider.connection.getAccountInfo(fundPda);
    const allocPool = fundInfo!.data.readBigUInt64LE(48);
    console.log("\nAllocation Pool:", allocPool.toString());

    // cap_a = fundingGoal * 38.2% = 10000 * 0.382 = 3820 TGF
    // cap_b = allocPool / 10
    // seed = min(cap_a, cap_b)
    const capA = BigInt(fundingGoal.toString()) * BigInt(381966011) / BigInt(1000000000);
    const capB = allocPool / BigInt(10);
    const seedCapital = capA < capB ? capA : capB;
    const fee = seedCapital * BigInt(50) / BigInt(10000);
    const netSeed = seedCapital - fee;

    console.log("Cap A (38.2% of goal):", capA.toString());
    console.log("Cap B (10% of pool):", capB.toString());
    console.log("Seed Capital:", seedCapital.toString());
    console.log("Expected Fee (0.5%):", fee.toString());
    console.log("Expected Net Seed:", netSeed.toString());

    // Balances before
    const [vaultBefore, feeBefore] = await Promise.all([
        provider.connection.getTokenAccountBalance(fundVault),
        provider.connection.getTokenAccountBalance(protocolFeeVault),
    ]);

    console.log("\n--- Before ---");
    console.log("Fund Vault TGF:", vaultBefore.value.uiAmountString);
    console.log("Fee Vault TGF:", feeBefore.value.uiAmountString);

    // Execute spawn
    try {
        const tx = await program.methods
            .spawnChildPto(
                Array.from(sector),
                fundingGoal,
                coherenceMass,
            )
            .accounts({
                authority: authority,
                fund: fundPda,
                childPto: childPto,
                creator: creator.publicKey,
                fundVault: fundVault,
                childVault: childVault,
                protocolFeeVault: protocolFeeVault,
                mint: TGF_MINT,
                tokenProgram: TOKEN_2022_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        console.log("\nTx:", tx);
        await provider.connection.confirmTransaction(tx, "confirmed");

        // Balances after
        const [vaultAfter, feeAfter, childAfter] = await Promise.all([
            provider.connection.getTokenAccountBalance(fundVault),
            provider.connection.getTokenAccountBalance(protocolFeeVault),
            provider.connection.getTokenAccountBalance(childVault),
        ]);

        console.log("\n--- After ---");
        console.log("Fund Vault TGF:", vaultAfter.value.uiAmountString);
        console.log("Fee Vault TGF:", feeAfter.value.uiAmountString);
        console.log("Child Vault TGF:", childAfter.value.uiAmountString);

        const vaultDelta = BigInt(vaultBefore.value.amount) - BigInt(vaultAfter.value.amount);
        const feeDelta = BigInt(feeAfter.value.amount) - BigInt(feeBefore.value.amount);
        const childDelta = BigInt(childAfter.value.amount);

        console.log("\n--- Actual Deltas ---");
        console.log("Fund Vault debited:", vaultDelta.toString());
        console.log("Fee Vault credited:", feeDelta.toString());
        console.log("Child Vault credited:", childDelta.toString());
        console.log("Fee + Child = Total:", (feeDelta + childDelta).toString());
        console.log("Fee routed correctly:", feeDelta.toString() === fee.toString());
        console.log("Net seed correct:", childDelta.toString() === netSeed.toString());

    } catch (error) {
        console.error("\nSpawn failed:", error);
        process.exit(1);
    }
}

main().then(() => process.exit(0));
