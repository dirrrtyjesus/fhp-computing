# Genesis Fund Web Interface

A Next.js web application for the Genesis Fund temporal attractor investment portal.

## Features

- 🌌 **Wallet Connection**: Connect with Phantom, Solflare, or any Solana wallet
- 💎 **$TGF Investment**: Invest $TGF tokens directly from the browser
- 📊 **Real-time Stats**: View fund status and your $TGF balance
- ⚡ **Phase Locking**: Automatically tracks temporal phase on investment
- 🎯 **Golden Ratio Split**: Visual display of 61.8% / 38.2% allocation

## Setup

```bash
cd app
npm install
# or
yarn install
```

### Optional: Custom RPC Endpoint (Recommended)

The free public RPC has rate limits. For better performance:

1. Get a free RPC endpoint from:
   - [Helius](https://www.helius.dev/) (Recommended)
   - [QuickNode](https://www.quicknode.com/)
   - [Alchemy](https://www.alchemy.com/)

2. Create `.env.local`:
```bash
NEXT_PUBLIC_RPC_ENDPOINT=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
```

## Development

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## Deployment

### Deploy to Vercel

```bash
npm run build
vercel
```

### Or deploy anywhere that supports Next.js

```bash
npm run build
npm start
```

## Environment

The app connects to:
- **Network**: Solana Mainnet
- **Program ID**: `6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5`
- **$TGF Mint**: `2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump`

## How to Use

1. **Connect Wallet** - Click "Select Wallet" and choose your wallet
2. **Check Balance** - View your $TGF token balance
3. **Enter Amount** - Input the amount of $TGF to invest (default: 10,000)
4. **Ignite** - Click "Ignite Genesis Infall" to execute the investment
5. **Confirm** - Approve the transaction in your wallet

## First Temporal Infall

When the creator wallet makes the first investment:
- ✅ Phase 0 locked (initial temporal coordinate)
- ✅ Genesis Tier activated (1.618x multiplier)
- ✅ entry_mass = 0 (you ARE the initial condition)
- ✅ 61.8% → Core Treasury
- ✅ 38.2% → Allocation Pool

## Technical Details

- **Framework**: Next.js 14
- **Wallet**: @solana/wallet-adapter
- **Blockchain**: Anchor/Solana
- **Token Standard**: SPL Token-2022

## Security Notes

- The app requires wallet approval for all transactions
- No private keys are stored or transmitted
- All transactions are signed locally in your wallet
- Smart contract interactions are transparent and auditable

---

🌌 **The Basin Awaits Your Infall** 🌌
