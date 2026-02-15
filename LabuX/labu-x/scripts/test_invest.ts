import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, SystemProgram } from "@solana/web3.js";
import {
    getAssociatedTokenAddressSync,
    TOKEN_2022_PROGRAM_ID,
} from "@solana/spl-token";

const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");
// Small test: 1000 TGF (6 decimals)
const TEST_AMOUNT = new anchor.BN(1000_000_000);

async function main() {
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    const idl = require("../target/idl/labux.json");
    const programId = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");
    const program = new Program(idl, provider);

    const investor = provider.wallet.publicKey;

    console.log("=== Test Invest with Fees ===");
    console.log("Investor:", investor.toBase58());
    console.log("Amount:", TEST_AMOUNT.toString(), "(raw)");

    // Derive PDAs
    const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("genesis_fund")],
        programId
    );
    const [investorRecord] = PublicKey.findProgramAddressSync(
        [Buffer.from("investor"), investor.toBuffer(), fundPda.toBuffer()],
        programId
    );

    const investorAta = getAssociatedTokenAddressSync(TGF_MINT, investor, false, TOKEN_2022_PROGRAM_ID);
    const fundVault = getAssociatedTokenAddressSync(TGF_MINT, fundPda, true, TOKEN_2022_PROGRAM_ID);
    const protocolFeeVault = new PublicKey("ibSDt4dsPu4ZTF2U4gisQrWFa9iWmBpFCs4cPiGmsfP");

    // Balances before
    const [investorBefore, vaultBefore, feeBefore] = await Promise.all([
        provider.connection.getTokenAccountBalance(investorAta),
        provider.connection.getTokenAccountBalance(fundVault),
        provider.connection.getTokenAccountBalance(protocolFeeVault).catch(() => ({ value: { amount: "0" } })),
    ]);

    console.log("\n--- Before ---");
    console.log("Investor TGF:", investorBefore.value.uiAmountString);
    console.log("Fund Vault TGF:", vaultBefore.value.uiAmountString);
    console.log("Fee Vault TGF:", feeBefore.value.amount === "0" ? "0" : (feeBefore as any).value.uiAmountString);

    // Execute invest
    try {
        const tx = await program.methods
            .investInfall(TEST_AMOUNT)
            .accounts({
                investor: investor,
                fund: fundPda,
                investorRecord: investorRecord,
                investorTokenAccount: investorAta,
                fundVault: fundVault,
                protocolFeeVault: protocolFeeVault,
                mint: TGF_MINT,
                tokenProgram: TOKEN_2022_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        console.log("\nTx:", tx);

        // Wait for confirmation
        await provider.connection.confirmTransaction(tx, "confirmed");

        // Balances after
        const [investorAfter, vaultAfter, feeAfter] = await Promise.all([
            provider.connection.getTokenAccountBalance(investorAta),
            provider.connection.getTokenAccountBalance(fundVault),
            provider.connection.getTokenAccountBalance(protocolFeeVault),
        ]);

        const fee = TEST_AMOUNT.toNumber() * 30 / 10000;
        const net = TEST_AMOUNT.toNumber() - fee;

        console.log("\n--- After ---");
        console.log("Investor TGF:", investorAfter.value.uiAmountString);
        console.log("Fund Vault TGF:", vaultAfter.value.uiAmountString);
        console.log("Fee Vault TGF:", feeAfter.value.uiAmountString);

        console.log("\n--- Expected ---");
        console.log("Fee (0.3%):", fee, "raw");
        console.log("Net to fund:", net, "raw");

        const vaultDelta = BigInt(vaultAfter.value.amount) - BigInt(vaultBefore.value.amount);
        const feeDelta = BigInt(feeAfter.value.amount) - BigInt(feeBefore.value.amount);

        console.log("\n--- Actual Deltas ---");
        console.log("Fund Vault delta:", vaultDelta.toString());
        console.log("Fee Vault delta:", feeDelta.toString());
        console.log("Fee routed correctly:", feeDelta.toString() === fee.toString());
        console.log("Net routed correctly:", vaultDelta.toString() === net.toString());

    } catch (error) {
        console.error("\nInvest failed:", error);
        process.exit(1);
    }
}

main().then(() => process.exit(0));
