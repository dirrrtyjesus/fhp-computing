import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY } from "@solana/web3.js";
import { TOKEN_2022_PROGRAM_ID } from "@solana/spl-token";

const TGF_MINT = new PublicKey("2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump");

async function main() {
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    const idl = require("../target/idl/labux.json");
    const programId = new PublicKey("6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5");
    const program = new Program(idl, provider);

    console.log("=== Genesis Fund Migration ===");
    console.log("RPC:", provider.connection.rpcEndpoint);
    console.log("Authority:", provider.wallet.publicKey.toBase58());
    console.log("Program:", programId.toBase58());

    // Derive PDAs
    const [genesisFund] = PublicKey.findProgramAddressSync(
        [Buffer.from("genesis_fund")],
        programId
    );

    const [protocolFeeVault] = PublicKey.findProgramAddressSync(
        [Buffer.from("protocol_treasury"), genesisFund.toBuffer()],
        programId
    );

    console.log("Genesis Fund PDA:", genesisFund.toBase58());
    console.log("Protocol Fee Vault PDA:", protocolFeeVault.toBase58());
    console.log("TGF Mint:", TGF_MINT.toBase58());

    // Verify genesis fund exists
    const fundInfo = await provider.connection.getAccountInfo(genesisFund);
    if (!fundInfo) {
        console.error("Genesis Fund not found on chain!");
        process.exit(1);
    }
    console.log("Genesis Fund exists:", fundInfo.data.length, "bytes, owner:", fundInfo.owner.toBase58());

    // Execute migration
    try {
        const tx = await program.methods
            .migrateGenesisFund()
            .accounts({
                authority: provider.wallet.publicKey,
                genesisFund: genesisFund,
                protocolFeeVault: protocolFeeVault,
                mint: TGF_MINT,
                systemProgram: SystemProgram.programId,
                tokenProgram: TOKEN_2022_PROGRAM_ID,
                rent: SYSVAR_RENT_PUBKEY,
            })
            .rpc();

        console.log("\nMigration successful!");
        console.log("Tx:", tx);

        // Verify
        const updatedFund = await provider.connection.getAccountInfo(genesisFund);
        console.log("New data length:", updatedFund?.data.length, "bytes");
    } catch (error) {
        console.error("Migration failed:", error);
        process.exit(1);
    }
}

main().then(() => process.exit(0));
