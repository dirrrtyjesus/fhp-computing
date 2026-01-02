'use client';

import { PublicKey } from '@solana/web3.js';

// Dynamically import to avoid SSR issues
let splToken: any;

if (typeof window !== 'undefined') {
  import('@solana/spl-token').then((module) => {
    splToken = module;
  });
}

export async function getAssociatedTokenAddressAsync(
  mint: PublicKey,
  owner: PublicKey,
  allowOwnerOffCurve = false,
  programId?: PublicKey
): Promise<PublicKey> {
  if (!splToken) {
    splToken = await import('@solana/spl-token');
  }
  return splToken.getAssociatedTokenAddress(
    mint,
    owner,
    allowOwnerOffCurve,
    programId
  );
}

export async function createAssociatedTokenAccountInstructionAsync(
  payer: PublicKey,
  associatedToken: PublicKey,
  owner: PublicKey,
  mint: PublicKey,
  programId?: PublicKey
) {
  if (!splToken) {
    splToken = await import('@solana/spl-token');
  }
  return splToken.createAssociatedTokenAccountInstruction(
    payer,
    associatedToken,
    owner,
    mint,
    programId
  );
}

export async function getToken2022ProgramId() {
  if (!splToken) {
    splToken = await import('@solana/spl-token');
  }
  return splToken.TOKEN_2022_PROGRAM_ID;
}
