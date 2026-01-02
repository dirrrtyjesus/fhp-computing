import { Keypair } from "@solana/web3.js";
import bs58 from "bs58";
import * as fs from "fs";

// This script converts private keys from various formats to Solana keypair JSON

async function main() {
    const privateKeyInput = process.argv[2];
    const outputPath = process.argv[3] || "wallet.json";

    if (!privateKeyInput) {
        console.log("Usage: npx ts-node scripts/convert_private_key.ts <private-key> [output-path]");
        console.log("\nSupported formats:");
        console.log("  - Base58 string (most common from wallets)");
        console.log("  - Hex string (0x... or without 0x)");
        console.log("  - Array [1,2,3,...]");
        console.log("\nExample:");
        console.log("  npx ts-node scripts/convert_private_key.ts 5Kj3n... pump-creator.json");
        process.exit(1);
    }

    let keypair: Keypair;

    try {
        // Try to parse as Base58 (most common format)
        if (privateKeyInput.length > 80 && privateKeyInput.length < 90 && !privateKeyInput.startsWith('[')) {
            console.log("📝 Detected Base58 format");
            const decoded = bs58.decode(privateKeyInput);
            keypair = Keypair.fromSecretKey(decoded);
        }
        // Try to parse as hex
        else if (privateKeyInput.startsWith('0x') || (privateKeyInput.length === 128 && !privateKeyInput.includes(','))) {
            console.log("📝 Detected Hex format");
            const hex = privateKeyInput.replace('0x', '');
            const bytes = Buffer.from(hex, 'hex');
            keypair = Keypair.fromSecretKey(bytes);
        }
        // Try to parse as array
        else if (privateKeyInput.startsWith('[')) {
            console.log("📝 Detected Array format");
            const array = JSON.parse(privateKeyInput);
            keypair = Keypair.fromSecretKey(new Uint8Array(array));
        }
        // Unknown format
        else {
            console.error("❌ Unknown private key format");
            console.log("\nTip: Most wallet exports use Base58 format (a long string like: 5Kj3nB...)");
            process.exit(1);
        }

        // Convert to array format for Solana CLI
        const secretArray = Array.from(keypair.secretKey);

        // Save to file
        fs.writeFileSync(outputPath, JSON.stringify(secretArray));

        console.log("✅ Keypair converted successfully!");
        console.log("📍 Public Key:", keypair.publicKey.toBase58());
        console.log("💾 Saved to:", outputPath);
        console.log("\n🚀 Now you can use:");
        console.log(`   npx ts-node scripts/invest_from_wallet.ts ${outputPath}`);

    } catch (error: any) {
        console.error("❌ Failed to parse private key:", error.message);
        console.log("\nMake sure your private key is in one of these formats:");
        console.log("  - Base58: 5Kj3nB7qE9mY...");
        console.log("  - Hex: 0x1a2b3c...");
        console.log("  - Array: [26,43,60,...]");
        process.exit(1);
    }
}

main();
