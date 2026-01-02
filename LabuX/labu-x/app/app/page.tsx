'use client';

import { useState, useEffect } from 'react';
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { PublicKey, SystemProgram, Transaction } from '@solana/web3.js';
import { Program, AnchorProvider, web3, BN } from '@coral-xyz/anchor';
import {
  getAssociatedTokenAddressAsync,
  createAssociatedTokenAccountInstructionAsync,
  getToken2022ProgramId
} from './utils/solana';

const TGF_MINT = new PublicKey('2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump');
const PROGRAM_ID = new PublicKey('6rivJsodwyZj7JbeJNeLD4F7K4tzxMq9mkEDkRxge7u5');
const PHI_INV = 0.618;

export default function Home() {
  const { connection } = useConnection();
  const wallet = useWallet();
  const [amount, setAmount] = useState('10000');
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [fundData, setFundData] = useState<any>(null);
  const [tgfBalance, setTgfBalance] = useState<number | null>(null);

  useEffect(() => {
    if (wallet.publicKey && connection) {
      loadFundData();
      loadTGFBalance();
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
        // Parse fund data (simplified - in production use IDL)
        const data = accountInfo.data;
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

  const loadTGFBalance = async () => {
    if (!wallet.publicKey) return;
    try {
      const TOKEN_2022_PROGRAM_ID = await getToken2022ProgramId();
      const ata = await getAssociatedTokenAddressAsync(
        TGF_MINT,
        wallet.publicKey,
        false,
        TOKEN_2022_PROGRAM_ID
      );
      const balance = await connection.getTokenAccountBalance(ata);
      setTgfBalance(balance.value.uiAmount);
    } catch (error) {
      setTgfBalance(0);
    }
  };

  const handleInvest = async () => {
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

      // Load IDL from local file
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

      // Check if fund vault exists
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

      // Check if fund is initialized
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

        // CRITICAL: Wait for confirmation before proceeding
        await connection.confirmTransaction(initSig, 'confirmed');
        setStatus({ type: 'info', message: 'Genesis Fund initialized. Preparing investment...' });
      }

      // Execute investment
      setStatus({ type: 'info', message: 'Executing temporal infall...' });
      const investAmount = new BN(parseFloat(amount) * 1_000_000);

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
        message: `🌌 Ignition Successful! Phase Locked. TX: ${tx.slice(0, 8)}...`,
      });

      // Calculate split
      const core = investAmount.toNumber() * PHI_INV;
      const alloc = investAmount.toNumber() * (1 - PHI_INV);

      setTimeout(() => {
        setStatus({
          type: 'success',
          message: `✅ ${amount} $TGF invested | Core: ${(core / 1_000_000).toFixed(2)} | Alloc: ${(alloc / 1_000_000).toFixed(2)}`,
        });
      }, 3000);

      loadFundData();
      loadTGFBalance();
    } catch (error: any) {
      console.error('Investment error:', error);
      setStatus({
        type: 'error',
        message: error.message || 'Transaction failed',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Genesis Fund</h1>
        <p className="subtitle">The Supermassive Temporal Attractor (PTO²)</p>
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
                <div className="stat-label">Your $TGF</div>
                <div className="stat-value">
                  {tgfBalance !== null ? tgfBalance.toFixed(2) : '...'}
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
          </div>

          <div className="invest-section">
            <h2 style={{ marginBottom: '1.5rem', color: '#f39c12', textAlign: 'center' }}>
              🌌 Execute Temporal Infall
            </h2>

            <div className="input-group">
              <label className="input-label">Investment Amount ($TGF)</label>
              <input
                type="number"
                className="input"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="10000"
                disabled={loading}
              />
            </div>

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

            <button
              className="button"
              onClick={handleInvest}
              disabled={loading || !amount || parseFloat(amount) <= 0}
            >
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                  <span className="loading"></span>
                  Processing...
                </span>
              ) : (
                'Ignite Genesis Infall'
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
            <p>🌌 First infall = Phase 0</p>
          </div>
        </>
      )}

      {!wallet.publicKey && (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <h2 style={{ color: '#f39c12', marginBottom: '1rem' }}>
            Connect Your Wallet
          </h2>
          <p style={{ color: '#888', fontSize: '1.1rem' }}>
            Connect the creator wallet to initiate the first temporal infall
          </p>
        </div>
      )}
    </div>
  );
}
