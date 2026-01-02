import type { Metadata } from 'next';
import './globals.css';
import { WalletContextProvider } from './providers/WalletProvider';

export const metadata: Metadata = {
  title: 'Genesis Fund - Temporal Attractor',
  description: 'The Supermassive Temporal Attractor (PTO²)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <WalletContextProvider>{children}</WalletContextProvider>
      </body>
    </html>
  );
}
