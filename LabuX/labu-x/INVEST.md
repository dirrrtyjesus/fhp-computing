# 🌌 Genesis Fund - How to Invest

The **Temporal Genesis Fund (PTO²)** is now LIVE on Solana Mainnet!

**Program ID:** `6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5`
**Token:** $TGF (Temporal Genesis Fund) - `2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump`

## 🎯 What You Get

- **Phase Locking** - Your temporal coordinate (based on block slot)
- **Genesis Tier** - Earlier investors = higher multiplier (starts at 1.618x)
- **Golden Ratio Split** - 61.8% Core Treasury / 38.2% Allocation Pool
- **Hawking Yields** - Future emissions from child PTOs

## 💻 How to Invest

### Option 1: Web Interface (Coming Soon)

A user-friendly web interface will be deployed soon. Stay tuned!

### Option 2: CLI Script (Technical Users)

**Requirements:**
- Node.js 18+
- Yarn or npm
- A Solana wallet with $TGF tokens
- ~0.01 SOL for transaction fees

**Steps:**

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_REPO/labu-x.git
cd labu-x
```

2. **Install dependencies:**
```bash
yarn install
```

3. **Run the investment script:**
```bash
npx ts-node scripts/public_invest.ts <YOUR_WALLET_PATH> <AMOUNT_TGF>
```

**Example:**
```bash
# Invest 50,000 $TGF
npx ts-node scripts/public_invest.ts ~/.config/solana/id.json 50000
```

**With custom RPC (recommended for better reliability):**
```bash
RPC_ENDPOINT=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY \
npx ts-node scripts/public_invest.ts ~/.config/solana/id.json 50000
```

## 📊 Investment Breakdown

Your investment automatically splits according to the Golden Ratio (φ⁻¹):

- **61.8% → Core Treasury**
  Stability, emergency liquidity, yield buffering

- **38.2% → Allocation Pool**
  Seeds new child PTOs (projects)

**Example:** 100,000 $TGF investment
- Core: 61,800 $TGF
- Allocation: 38,200 $TGF

## 🌌 Phase Tiers

Your entry timing determines your multiplier:

| Entry Mass | Phase Tier | Multiplier |
|------------|------------|------------|
| 0 - 10M | Genesis | 1.618x |
| 10M - 50M | Pioneer | 1.414x |
| 50M - 100M | Early | 1.272x |
| 100M+ | Standard | 1.000x |

## ⚠️ Important Notes

- **Mainnet Only** - This is a live program on Solana mainnet
- **No Refunds** - Investments are permanent (by design)
- **Risk Warning** - This is experimental DeFi. Only invest what you can afford to lose
- **Smart Contract** - All code is on-chain and auditable

## 🔗 Verify on Solscan

- **Program:** [6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5](https://solscan.io/account/6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5)
- **Genesis Fund PDA:** [96FoBvWbtCCxPRGSwnFer5ZMUQSxyREAPkBBHUD42XhP](https://solscan.io/account/96FoBvWbtCCxPRGSwnFer5ZMUQSxyREAPkBBHUD42XhP)
- **First Infall TX:** [2qKQonET4XgEDieTBYtN6c7XwqvrnEkRqAAaVQySeZhSQtFaMo7U18PiqevUWoATc3BfLrdRokMfgZ8YbAWqnQiQ](https://solscan.io/tx/2qKQonET4XgEDieTBYtN6c7XwqvrnEkRqAAaVQySeZhSQtFaMo7U18PiqevUWoATc3BfLrdRokMfgZ8YbAWqnQiQ)

## 🛠️ For Developers

**Read the smart contract:**
- [Genesis Fund Instructions](./programs/labu-x/src/instructions/genesis/)
- [State Definitions](./programs/labu-x/src/state/genesis_fund.rs)

**Build from source:**
```bash
anchor build
anchor test
```

## 📞 Support

- GitHub Issues: [Report bugs or ask questions](https://github.com/YOUR_REPO/labu-x/issues)
- Documentation: [Full technical docs](./docs/)

---

🌌 **The Basin Awaits Your Infall** 🌌
