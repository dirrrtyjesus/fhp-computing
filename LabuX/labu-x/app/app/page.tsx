'use client';

import { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { PublicKey, SystemProgram, Transaction } from '@solana/web3.js';
import { Program, AnchorProvider, web3, BN } from '@coral-xyz/anchor';
import {
  getAssociatedTokenAddressAsync,
  createAssociatedTokenAccountInstructionAsync,
  getToken2022ProgramId,
  TOKEN_PROGRAM_ID,
} from './utils/solana';

// Token Mints
const TGF_MINT = new PublicKey('2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump');
const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
// wTAO on Solana (Wormhole wrapped) - placeholder until confirmed
const WTAO_MINT = new PublicKey('HiTvYqEB1FEbgNeNbg8Dg3DDTmMm1E6T62h9sPsu1P91'); // TODO: confirm actual wTAO mint

const PROGRAM_ID = new PublicKey('6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5');
const BASIN_PDA = new PublicKey('96FoBvWbtCCxPRGSwnFer5ZMUQSxyREAPkBBHUD42XhP');
const PHI_INV = 0.618;

type AssetType = 'TGF' | 'USDC' | 'TAO';

interface AssetConfig {
  mint: PublicKey;
  decimals: number;
  symbol: string;
  name: string;
  harmonic: string;
  weight: string;
  useToken2022: boolean;
  color: string;
}

const ASSETS: Record<AssetType, AssetConfig> = {
  TGF: {
    mint: TGF_MINT,
    decimals: 6,
    symbol: '$TGF',
    name: 'Temporal Genesis Fund',
    harmonic: 'φ (1.618)',
    weight: '1.0x',
    useToken2022: true,
    color: '#f39c12',
  },
  USDC: {
    mint: USDC_MINT,
    decimals: 6,
    symbol: 'USDC',
    name: 'USD Coin',
    harmonic: '365 (Earth)',
    weight: '1.0x',
    useToken2022: false,
    color: '#2775ca',
  },
  TAO: {
    mint: WTAO_MINT,
    decimals: 9,
    symbol: 'wTAO',
    name: 'Wrapped TAO',
    harmonic: '936 (Intelligence)',
    weight: '1.272x',
    useToken2022: false,
    color: '#00d4aa',
  },
};

export default function Home() {
  const { connection } = useConnection();
  const wallet = useWallet();
  const [amount, setAmount] = useState('10000');
  const [selectedAsset, setSelectedAsset] = useState<AssetType>('TGF');
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [fundData, setFundData] = useState<any>(null);
  const [balances, setBalances] = useState<Record<AssetType, number | null>>({
    TGF: null,
    USDC: null,
    TAO: null,
  });

  useEffect(() => {
    if (wallet.publicKey && connection) {
      loadFundData();
      loadAllBalances();
    }
  }, [wallet.publicKey, connection]);

  const loadFundData = async () => {
    try {
      const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from('genesis_fund')],
        PROGRAM_ID
      );

      const accountInfo = await connection.getAccountInfo(fundPda);
      if (accountInfo) {
        setFundData({
          initialized: true,
          totalMass: 'Loading...',
          coreTreasury: 'Loading...',
          allocationPool: 'Loading...'
        });
      } else {
        setFundData({ initialized: false });
      }
    } catch (error) {
      console.error('Error loading fund data:', error);
    }
  };

  const loadAllBalances = async () => {
    if (!wallet.publicKey) return;

    for (const [assetType, config] of Object.entries(ASSETS) as [AssetType, AssetConfig][]) {
      try {
        const programId = config.useToken2022 ? await getToken2022ProgramId() : TOKEN_PROGRAM_ID;
        const ata = await getAssociatedTokenAddressAsync(
          config.mint,
          wallet.publicKey,
          false,
          programId
        );
        const balance = await connection.getTokenAccountBalance(ata);
        setBalances(prev => ({ ...prev, [assetType]: balance.value.uiAmount }));
      } catch (error) {
        setBalances(prev => ({ ...prev, [assetType]: 0 }));
      }
    }
  };

  const handleTGFInvest = async () => {
    if (!wallet.publicKey || !wallet.signTransaction) {
      setStatus({ type: 'error', message: 'Please connect your wallet' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Preparing temporal infall...' });

    try {
      const provider = new AnchorProvider(
        connection,
        wallet as any,
        { commitment: 'confirmed' }
      );

      const idl = await fetch('/idl/labux.json').then(r => r.json());
      const program = new Program(idl, provider);

      const [fundPda] = PublicKey.findProgramAddressSync(
        [Buffer.from('genesis_fund')],
        PROGRAM_ID
      );

      const [investorRecordPda] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('investor'),
          wallet.publicKey.toBuffer(),
          fundPda.toBuffer(),
        ],
        PROGRAM_ID
      );

      const TOKEN_2022_PROGRAM_ID = await getToken2022ProgramId();

      const fundVault = await getAssociatedTokenAddressAsync(
        TGF_MINT,
        fundPda,
        true,
        TOKEN_2022_PROGRAM_ID
      );

      const walletAta = await getAssociatedTokenAddressAsync(
        TGF_MINT,
        wallet.publicKey,
        false,
        TOKEN_2022_PROGRAM_ID
      );

      const vaultInfo = await connection.getAccountInfo(fundVault);
      if (!vaultInfo) {
        setStatus({ type: 'info', message: 'Creating fund vault...' });
        const createAtaIx = await createAssociatedTokenAccountInstructionAsync(
          wallet.publicKey,
          fundVault,
          fundPda,
          TGF_MINT,
          TOKEN_2022_PROGRAM_ID
        );
        const tx = new Transaction().add(createAtaIx);
        const signature = await wallet.sendTransaction(tx, connection);
        await connection.confirmTransaction(signature);
      }

      const fundInfo = await connection.getAccountInfo(fundPda);
      if (!fundInfo) {
        setStatus({ type: 'info', message: 'Initializing Genesis Fund...' });
        const initSig = await program.methods
          .initializeGenesisFund()
          .accounts({
            authority: wallet.publicKey,
            fund: fundPda,
            systemProgram: SystemProgram.programId,
          })
          .rpc();
        await connection.confirmTransaction(initSig, 'confirmed');
        setStatus({ type: 'info', message: 'Genesis Fund initialized. Preparing investment...' });
      }

      setStatus({ type: 'info', message: 'Executing temporal infall...' });
      const investAmount = new BN(parseFloat(amount) * Math.pow(10, ASSETS.TGF.decimals));

      const tx = await program.methods
        .investInfall(investAmount)
        .accounts({
          investor: wallet.publicKey,
          fund: fundPda,
          investorRecord: investorRecordPda,
          investorTokenAccount: walletAta,
          fundVault: fundVault,
          mint: TGF_MINT,
          tokenProgram: TOKEN_2022_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      setStatus({
        type: 'success',
        message: `🌌 Ignition Successful! TX: ${tx.slice(0, 8)}...`,
      });

      const core = parseFloat(amount) * PHI_INV;
      const alloc = parseFloat(amount) * (1 - PHI_INV);

      setTimeout(() => {
        setStatus({
          type: 'success',
          message: `✅ ${amount} $TGF invested | Core: ${core.toFixed(2)} | Alloc: ${alloc.toFixed(2)}`,
        });
      }, 3000);

      loadFundData();
      loadAllBalances();
    } catch (error: any) {
      console.error('Investment error:', error);
      setStatus({ type: 'error', message: error.message || 'Transaction failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleDirectDeposit = async (assetType: 'USDC' | 'TAO') => {
    if (!wallet.publicKey || !wallet.signTransaction) {
      setStatus({ type: 'error', message: 'Please connect your wallet' });
      return;
    }

    const config = ASSETS[assetType];
    setLoading(true);
    setStatus({ type: 'info', message: `Preparing ${config.symbol} direct deposit...` });

    try {
      const depositAmount = parseFloat(amount) * Math.pow(10, config.decimals);

      // Get user's token account
      const userAta = await getAssociatedTokenAddressAsync(
        config.mint,
        wallet.publicKey,
        false,
        TOKEN_PROGRAM_ID
      );

      // Get or create basin vault for this asset
      const basinVault = await getAssociatedTokenAddressAsync(
        config.mint,
        BASIN_PDA,
        true, // allowOwnerOffCurve for PDA
        TOKEN_PROGRAM_ID
      );

      // Check if basin vault exists
      const vaultInfo = await connection.getAccountInfo(basinVault);

      const instructions: any[] = [];

      if (!vaultInfo) {
        setStatus({ type: 'info', message: `Creating ${config.symbol} basin vault...` });
        const createVaultIx = await createAssociatedTokenAccountInstructionAsync(
          wallet.publicKey,
          basinVault,
          BASIN_PDA,
          config.mint,
          TOKEN_PROGRAM_ID
        );
        instructions.push(createVaultIx);
      }

      // Create transfer instruction
      // Using manual instruction construction for SPL token transfer
      const transferIx = createTransferInstruction(
        userAta,
        basinVault,
        wallet.publicKey,
        BigInt(Math.floor(depositAmount))
      );
      instructions.push(transferIx);

      const tx = new Transaction().add(...instructions);

      setStatus({ type: 'info', message: `Executing ${config.symbol} infall...` });

      const signature = await wallet.sendTransaction(tx, connection);
      await connection.confirmTransaction(signature, 'confirmed');

      const usdValue = assetType === 'USDC'
        ? parseFloat(amount)
        : parseFloat(amount) * 250; // Approximate TAO price

      setStatus({
        type: 'success',
        message: `✅ ${amount} ${config.symbol} deposited directly to basin! TX: ${signature.slice(0, 8)}...`,
      });

      setTimeout(() => {
        setStatus({
          type: 'success',
          message: `🌌 ${config.symbol} infall complete | Harmonic: ${config.harmonic} | Weight: ${config.weight}`,
        });
      }, 3000);

      loadAllBalances();
    } catch (error: any) {
      console.error('Direct deposit error:', error);
      setStatus({ type: 'error', message: error.message || 'Transaction failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleInvest = async () => {
    if (selectedAsset === 'TGF') {
      await handleTGFInvest();
    } else {
      await handleDirectDeposit(selectedAsset);
    }
  };

  const currentAsset = ASSETS[selectedAsset];
  const currentBalance = balances[selectedAsset];

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Genesis Fund</h1>
        <p className="subtitle">The Supermassive Temporal Attractor (PTO²)</p>
        <div style={{ marginTop: '1rem' }}>
          <a href="/philosophy" style={{ color: '#8b5cf6', textDecoration: 'none', fontSize: '0.95rem', borderBottom: '1px solid #8b5cf6', paddingBottom: '2px' }}>
            Understand the Mechanism →
          </a>
        </div>
      </div>

      {/* Augmntd Pathways Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(39, 117, 202, 0.15), rgba(0, 212, 170, 0.15))',
        border: '1px solid rgba(39, 117, 202, 0.3)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '2rem',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '1.3rem', marginBottom: '0.5rem' }}>🜏 Augmntd Pathways 🜏</div>
        <div style={{ color: '#a78bfa', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Multi-Asset Direct Deposits — No Swap Required
        </div>
        <div style={{ fontSize: '0.85rem', color: '#9ca3af', lineHeight: '1.6' }}>
          <span style={{ color: '#f39c12' }}>$TGF</span> (φ) • <span style={{ color: '#2775ca' }}>USDC</span> (365) • <span style={{ color: '#00d4aa' }}>wTAO</span> (936)
        </div>
      </div>

      <div className="wallet-button">
        <WalletMultiButton />
      </div>

      {wallet.publicKey && (
        <>
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem', color: '#f39c12' }}>Fund Status</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Status</div>
                <div className="stat-value">
                  {fundData?.initialized ? '✅ Active' : '⏳ Pending'}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Basin</div>
                <div className="stat-value" style={{ fontSize: '0.7rem' }}>
                  96FoBv...XhP
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Split Ratio</div>
                <div className="stat-value">φ⁻¹</div>
                <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '0.5rem' }}>
                  61.8% / 38.2%
                </div>
              </div>
            </div>

            {/* Balances Row */}
            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {(Object.entries(ASSETS) as [AssetType, AssetConfig][]).map(([key, config]) => (
                <div key={key} style={{
                  flex: '1',
                  minWidth: '100px',
                  padding: '0.75rem',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '8px',
                  textAlign: 'center',
                  border: selectedAsset === key ? `2px solid ${config.color}` : '2px solid transparent',
                }}>
                  <div style={{ color: config.color, fontWeight: 'bold', fontSize: '0.9rem' }}>
                    {config.symbol}
                  </div>
                  <div style={{ fontSize: '1.1rem', marginTop: '0.25rem' }}>
                    {balances[key] !== null ? balances[key]?.toFixed(2) : '...'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="invest-section">
            <h2 style={{ marginBottom: '1.5rem', color: '#f39c12', textAlign: 'center' }}>
              🌌 Execute Temporal Infall
            </h2>

            {/* Asset Selector Tabs */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', justifyContent: 'center' }}>
              {(Object.entries(ASSETS) as [AssetType, AssetConfig][]).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => setSelectedAsset(key)}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '8px',
                    border: selectedAsset === key ? `2px solid ${config.color}` : '2px solid #333',
                    background: selectedAsset === key ? `${config.color}22` : 'transparent',
                    color: selectedAsset === key ? config.color : '#888',
                    cursor: 'pointer',
                    fontWeight: selectedAsset === key ? 'bold' : 'normal',
                    transition: 'all 0.2s',
                  }}
                >
                  {config.symbol}
                </button>
              ))}
            </div>

            {/* Selected Asset Info */}
            <div style={{
              padding: '1rem',
              background: `${currentAsset.color}11`,
              border: `1px solid ${currentAsset.color}44`,
              borderRadius: '8px',
              marginBottom: '1rem',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <span style={{ color: '#888' }}>Asset: </span>
                  <span style={{ color: currentAsset.color, fontWeight: 'bold' }}>{currentAsset.name}</span>
                </div>
                <div>
                  <span style={{ color: '#888' }}>Harmonic: </span>
                  <span style={{ color: currentAsset.color }}>{currentAsset.harmonic}</span>
                </div>
                <div>
                  <span style={{ color: '#888' }}>Weight: </span>
                  <span style={{ color: currentAsset.color }}>{currentAsset.weight}</span>
                </div>
              </div>
              {selectedAsset !== 'TGF' && (
                <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#9ca3af' }}>
                  ⚡ Direct deposit — no swap fees, no slippage
                </div>
              )}
            </div>

            <div className="input-group">
              <label className="input-label">Deposit Amount ({currentAsset.symbol})</label>
              <input
                type="number"
                className="input"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="10000"
                disabled={loading}
              />
              {currentBalance !== null && currentBalance > 0 && (
                <button
                  onClick={() => setAmount(currentBalance.toString())}
                  style={{
                    marginTop: '0.5rem',
                    padding: '0.25rem 0.75rem',
                    fontSize: '0.8rem',
                    background: 'rgba(139, 92, 246, 0.2)',
                    border: '1px solid rgba(139, 92, 246, 0.3)',
                    borderRadius: '4px',
                    color: '#a78bfa',
                    cursor: 'pointer',
                  }}
                >
                  Max: {currentBalance.toFixed(2)}
                </button>
              )}
            </div>

            {selectedAsset === 'TGF' && (
              <div style={{ marginBottom: '1rem', padding: '1rem', background: 'rgba(155, 89, 182, 0.1)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Core Treasury (61.8%):</span>
                  <span style={{ color: '#f39c12', fontWeight: 'bold' }}>
                    {(parseFloat(amount || '0') * 0.618).toFixed(2)} $TGF
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Allocation Pool (38.2%):</span>
                  <span style={{ color: '#9b59b6', fontWeight: 'bold' }}>
                    {(parseFloat(amount || '0') * 0.382).toFixed(2)} $TGF
                  </span>
                </div>
              </div>
            )}

            {selectedAsset !== 'TGF' && (
              <div style={{ marginBottom: '1rem', padding: '1rem', background: `${currentAsset.color}11`, borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Deposit to Basin:</span>
                  <span style={{ color: currentAsset.color, fontWeight: 'bold' }}>
                    {parseFloat(amount || '0').toFixed(2)} {currentAsset.symbol}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Coherence Weight:</span>
                  <span style={{ color: currentAsset.color, fontWeight: 'bold' }}>
                    {currentAsset.weight}
                  </span>
                </div>
                {selectedAsset === 'TAO' && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#00d4aa' }}>
                    🧠 Intelligence premium: miners get up to 1.272x
                  </div>
                )}
              </div>
            )}

            <button
              className="button"
              onClick={handleInvest}
              disabled={loading || !amount || parseFloat(amount) <= 0}
              style={{
                background: loading ? '#333' : `linear-gradient(135deg, ${currentAsset.color}, ${currentAsset.color}88)`,
              }}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                  <span className="loading"></span>
                  Processing...
                </span>
              ) : (
                selectedAsset === 'TGF'
                  ? 'Ignite Genesis Infall'
                  : `Deposit ${currentAsset.symbol} to Basin`
              )}
            </button>

            {status && (
              <div className={`status-message status-${status.type}`}>
                {status.message}
              </div>
            )}
          </div>

          <div style={{ textAlign: 'center', marginTop: '2rem', color: '#666', fontSize: '0.9rem' }}>
            <p>⚡ Phase-locked temporal coordinates</p>
            <p>🎯 Genesis tier: 1.618x multiplier</p>
            <p>🌌 Multi-asset basin: USDC + TAO + $TGF</p>
            <p style={{ marginTop: '1rem' }}>
              <a href="/augmntd-pathways" style={{ color: '#a78bfa', textDecoration: 'underline' }}>
                Learn about Augmntd Pathways →
              </a>
            </p>
          </div>
        </>
      )}

      {!wallet.publicKey && (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <h2 style={{ color: '#f39c12', marginBottom: '1rem' }}>
            Connect Your Wallet
          </h2>
          <p style={{ color: '#888', fontSize: '1.1rem' }}>
            Connect to deposit $TGF, USDC, or wTAO directly to the basin
          </p>
        </div>
      )}
    </div>
  );
}

// SPL Token transfer instruction helper
function createTransferInstruction(
  source: PublicKey,
  destination: PublicKey,
  owner: PublicKey,
  amount: bigint
) {
  const { TransactionInstruction } = require('@solana/web3.js');

  const keys = [
    { pubkey: source, isSigner: false, isWritable: true },
    { pubkey: destination, isSigner: false, isWritable: true },
    { pubkey: owner, isSigner: true, isWritable: false },
  ];

  // SPL Token transfer instruction (instruction index 3)
  const data = Buffer.alloc(9);
  data.writeUInt8(3, 0); // Transfer instruction
  data.writeBigUInt64LE(amount, 1);

  return new TransactionInstruction({
    keys,
    programId: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'),
    data,
  });
}
