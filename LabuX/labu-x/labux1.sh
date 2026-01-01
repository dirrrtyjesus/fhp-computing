#!/bin/bash
# LabuX1.sh - Deploy LabuX to X1 Network

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
echo "   Balance: $BALANCE XNT"

if [ "$BALANCE" = "0 SOL" ]; then
    echo "   ERROR: Need XNT tokens for deployment!"
    echo "   Get testnet XNT from X1 faucet"
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
