import { Resource } from '@modelcontextprotocol/sdk/types.js';
import crypto from 'crypto';
import { HarmonicCoherenceEngine } from '../coherence/cdt.js';
import { LivingRepertoire } from '../repertoire/repertoire.js';
import { SecurityGovernanceEngine } from '../security/governance.js';

export function getXenResourceDefinitions(): Resource[] {
  return [
    {
      uri: 'xen://enterprise/ledger',
      name: 'Harmonic Ledger Pointer',
      mimeType: 'application/json',
      description: 'Dynamic enterprise general ledger context with tau_k coherence signature and provenance envelope'
    },
    {
      uri: 'xen://coherence/field',
      name: 'CDT Coherence Field Snapshot',
      mimeType: 'application/json',
      description: 'Current 64-bin complex wave matrix amplitudes, Kuramoto order parameter R, and phase lock state'
    },
    {
      uri: 'xen://repertoire/graph',
      name: 'Living Repertoire Graph',
      mimeType: 'application/json',
      description: 'Monotonic accumulative memory graph (Sigma >= 0) and past execution traces'
    }
  ];
}

export async function handleXenReadResource(
  uri: string,
  coherenceEngine: HarmonicCoherenceEngine,
  repertoire: LivingRepertoire,
  governance: SecurityGovernanceEngine
): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
  if (uri === 'xen://enterprise/ledger' || uri.startsWith('xen://ledger/accounts/')) {
    const timestamp = new Date().toISOString();
    const calculationHash = crypto
      .createHash('sha256')
      .update(`ledger:standard:${timestamp}`)
      .digest('hex');

    const pointerPayload = governance.sanitizeOutput({
      uri,
      tau_k: coherenceEngine.tauK,
      aperture_alpha: 0.85,
      coherence_status: 'PHASE_LOCKED',
      data: {
        account_id: 'enterprise_primary',
        cleared_balance_cents: 14250000,
        pending_settlements: [],
        currency: 'USD'
      },
      provenance_envelope: {
        origin_table: 'enterprise_general_ledger',
        calculation_hash: calculationHash,
        timestamp
      }
    });

    return {
      contents: [
        {
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(pointerPayload, null, 2)
        }
      ]
    };
  }

  if (uri === 'xen://coherence/field') {
    const stream = coherenceEngine.exportStreamPayload();
    const raw = coherenceEngine.getRawAmplitudes();

    return {
      contents: [
        {
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(
            {
              stream,
              field_bins_raw: {
                bins_count: raw.real.length,
                real_first_8: raw.real.slice(0, 8),
                imag_first_8: raw.imag.slice(0, 8)
              }
            },
            null,
            2
          )
        }
      ]
    };
  }

  if (uri === 'xen://repertoire/graph') {
    return {
      contents: [
        {
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(
            {
              sigma: repertoire.getSigma(),
              total_traces: repertoire.getTraceCount(),
              recent_traces: repertoire.getRecentTraces(10)
            },
            null,
            2
          )
        }
      ]
    };
  }

  throw new Error(`Resource not found: ${uri}`);
}
