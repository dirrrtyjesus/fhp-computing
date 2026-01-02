'use client';

import React, { useMemo } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { clusterApiUrl } from '@solana/web3.js';

require('@solana/wallet-adapter-react-ui/styles.css');

export function WalletContextProvider({ children }: { children: React.ReactNode }) {
  // Use custom RPC endpoint or fallback to public
  // For production, use Helius, QuickNode, or other paid RPC
  const endpoint = useMemo(() => {
    // Check for custom RPC in env
    if (process.env.NEXT_PUBLIC_RPC_ENDPOINT) {
      return process.env.NEXT_PUBLIC_RPC_ENDPOINT;
    }
    // Fallback to public endpoint (has rate limits)
    return 'https://api.mainnet-beta.solana.com';
  }, []);

  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
      new SolflareWalletAdapter(),
    ],
    []
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect={false}>
        <WalletModalProvider>{children}</WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}
