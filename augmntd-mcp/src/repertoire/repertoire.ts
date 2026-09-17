import crypto from 'crypto';

export interface RepertoireTrace {
  id: string;
  action: string;
  agentId: string;
  parameters: Record<string, any>;
  status: 'COMMITTED' | 'DRIFTED' | 'CANCELLED' | 'SIMULATED';
  inducedComplexity: number;
  tauSignature: number;
  timestamp: string;
  calculationHash: string;
}

export class LivingRepertoire {
  private traces: RepertoireTrace[] = [];
  private sigma: number = 0; // Monotonic accumulative complexity Sigma >= 0

  constructor() {
    // Initial genesis trace
    this.recordTrace({
      action: 'genesis_phase_init',
      agentId: 'system_tauk_engine',
      parameters: { status: 'PHASE_LOCKED' },
      status: 'COMMITTED',
      inducedComplexity: 1.618034,
      tauSignature: 1.618034
    });
  }

  /**
   * Records a trace into the Living Repertoire Graph.
   * R(t+1) = R(t) \oplus_\tau \iota(t), \Sigma = \sum |\iota(t)| \ge 0
   */
  public recordTrace(data: {
    action: string;
    agentId: string;
    parameters: Record<string, any>;
    status: 'COMMITTED' | 'DRIFTED' | 'CANCELLED' | 'SIMULATED';
    inducedComplexity: number;
    tauSignature: number;
  }): RepertoireTrace {
    const timestamp = new Date().toISOString();
    const calculationHash = crypto
      .createHash('sha256')
      .update(`${data.action}:${data.agentId}:${JSON.stringify(data.parameters)}:${timestamp}`)
      .digest('hex');

    const trace: RepertoireTrace = {
      id: crypto.randomUUID(),
      action: data.action,
      agentId: data.agentId,
      parameters: data.parameters,
      status: data.status,
      inducedComplexity: data.inducedComplexity,
      tauSignature: data.tauSignature,
      timestamp,
      calculationHash
    };

    this.traces.push(trace);
    this.sigma += Math.abs(data.inducedComplexity);
    return trace;
  }

  /**
   * Historical Replay Simulator:
   * Evaluates proposed execution policies against past trace graphs at zero DB cost.
   */
  public simulate(proposedAction: string, parameters: Record<string, any>): {
    allowed: boolean;
    projectedRiskScore: number;
    similarTracesCount: number;
    nearestOutcome: string;
    repertoireSigma: number;
  } {
    const matches = this.traces.filter((t) => t.action === proposedAction);
    const cancelledCount = matches.filter((t) => t.status === 'CANCELLED' || t.status === 'DRIFTED').length;
    const committedCount = matches.filter((t) => t.status === 'COMMITTED').length;

    const total = matches.length;
    let projectedRisk = 0.1;

    if (total > 0) {
      projectedRisk = (cancelledCount + 0.1) / (total + 1.0);
    }

    return {
      allowed: projectedRisk < 0.75,
      projectedRiskScore: Number(projectedRisk.toFixed(4)),
      similarTracesCount: total,
      nearestOutcome: committedCount >= cancelledCount ? 'STABLE' : 'UNSTABLE_DRIFT',
      repertoireSigma: Number(this.sigma.toFixed(4))
    };
  }

  public getTraceCount(): number {
    return this.traces.length;
  }

  public getSigma(): number {
    return Number(this.sigma.toFixed(4));
  }

  public getRecentTraces(limit: number = 10): RepertoireTrace[] {
    return this.traces.slice(-limit);
  }
}
