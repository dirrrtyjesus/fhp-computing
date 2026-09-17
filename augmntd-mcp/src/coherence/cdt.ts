import crypto from 'crypto';

export interface WriteImpulse {
  id: string;
  agentId: string;
  phase: number; // in [0, 2*PI)
  key?: string;
  coherence: number; // confidence in [0, 1]
  valence: number; // signed value, negative represents objection
  payload?: string;
  timestamp: number;
}

export interface PhaseLockResult {
  kuramoto_r: number;
  peak_bin: number;
  peak_phase: number;
  peak_amplitude: number;
  mean_amplitude: number;
  spectral_density: number;
  coherence_status: 'PHASE_LOCKED' | 'DISSONANT';
  contest_ratio: number;
  tau_k: number;
  timestamp: string;
}

export interface HarmonicStreamPayload {
  schema: 'tauk.harmonic-mode-stream/v1';
  timestamp: string;
  tau_k: number;
  cheeger_floor: number;
  kuramoto_r: number;
  lock_status: 'PHASE_LOCKED' | 'DISSONANT';
  spectral_density: number;
  total_impulses: number;
  active_agents: string[];
  top_harmonic_bins: Array<{
    bin: number;
    phase: number;
    amplitude: number;
    share: number;
  }>;
}

export class HarmonicCoherenceEngine {
  private readonly bins: number;
  public readonly tauK: number = 1.61803398875;
  public readonly cheegerFloor: number = 0.61803398875;
  private readonly dxExponent: number = 2.125; // 17 / 8 = 2.125 (Scale-invariant power law)
  private readonly envelopeDampening: number = 0.8125; // D+_t
  private readonly carrierProjection: number = 0.625; // D-_t

  // Complex amplitude accumulators per bin [real, imag]
  private realAmplitudes: Float64Array;
  private imagAmplitudes: Float64Array;
  private rawAbsoluteSum: Float64Array;

  // Write history & intrinsic clock
  private impulses: WriteImpulse[] = [];
  private intrinsicClockTick: number = 0;

  constructor(bins: number = 64) {
    this.bins = bins;
    this.realAmplitudes = new Float64Array(bins);
    this.imagAmplitudes = new Float64Array(bins);
    this.rawAbsoluteSum = new Float64Array(bins);
  }

  /**
   * Deterministically maps any semantic key to a phase in [0, 2*PI)
   * using the first 8 bytes of SHA-256.
   */
  public phaseFromKey(key: string): number {
    const hash = crypto.createHash('sha256').update(key).digest();
    const bigIntVal = hash.readBigUInt64BE(0);
    const fraction = Number(bigIntVal) / Number(0xffffffffffffffffn);
    return fraction * 2 * Math.PI;
  }

  /**
   * Snaps a continuous phase into a discrete bin index [0, bins-1].
   */
  public binFromPhase(phase: number): number {
    const normalized = ((phase % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
    const bin = Math.floor((normalized / (2 * Math.PI)) * this.bins);
    return Math.min(Math.max(bin, 0), this.bins - 1);
  }

  /**
   * Phase corresponding to the center of a given bin.
   */
  public phaseOfBin(bin: number): number {
    return (bin / this.bins) * 2 * Math.PI;
  }

  /**
   * Ingests an agent state impulse into the complex wave field.
   * State merges via wave superposition: Psi(t) = sum w_i * exp(i * theta_i)
   */
  public ingestState(
    agentId: string,
    phaseOrKey: number | string,
    coherence: number,
    valence: number,
    payload?: string
  ): WriteImpulse {
    const phase = typeof phaseOrKey === 'string' ? this.phaseFromKey(phaseOrKey) : phaseOrKey;
    const key = typeof phaseOrKey === 'string' ? phaseOrKey : undefined;

    const clampedCoherence = Math.max(0, Math.min(1, coherence));
    const signedWeight = clampedCoherence * valence;
    const bin = this.binFromPhase(phase);

    // Superposition contribution
    const realContribution = signedWeight * Math.cos(phase);
    const imagContribution = signedWeight * Math.sin(phase);

    this.realAmplitudes[bin] += realContribution;
    this.imagAmplitudes[bin] += imagContribution;
    this.rawAbsoluteSum[bin] += Math.abs(signedWeight);

    const impulse: WriteImpulse = {
      id: crypto.randomUUID(),
      agentId,
      phase,
      key,
      coherence: clampedCoherence,
      valence,
      payload,
      timestamp: Date.now()
    };

    this.impulses.push(impulse);
    return impulse;
  }

  /**
   * Computes Kuramoto order parameter R and swarm phase-lock condition.
   * R = (1/N) * |sum_j exp(i * theta_j)|
   */
  public computePhaseLock(threshold: number = 0.8): PhaseLockResult {
    let sumCos = 0;
    let sumSin = 0;
    let peakBin = 0;
    let peakAmp = 0;
    let totalAmp = 0;
    let totalRaw = 0;

    for (let i = 0; i < this.bins; i++) {
      const real = this.realAmplitudes[i];
      const imag = this.imagAmplitudes[i];
      const amp = Math.sqrt(real * real + imag * imag);

      totalAmp += amp;
      totalRaw += this.rawAbsoluteSum[i];

      if (amp > peakAmp) {
        peakAmp = amp;
        peakBin = i;
      }
    }

    const n = this.impulses.length;
    let kuramotoR = 1.0;

    if (n > 0) {
      for (const imp of this.impulses) {
        sumCos += Math.cos(imp.phase);
        sumSin += Math.sin(imp.phase);
      }
      kuramotoR = Math.sqrt(sumCos * sumCos + sumSin * sumSin) / n;
    }

    const meanAmp = totalAmp / this.bins;
    const spectralDensity = totalAmp > 0 ? (peakAmp / totalAmp) : 0;
    const contestRatio = totalRaw > 0 ? Math.max(0, (totalRaw - totalAmp) / totalRaw) : 0;
    const isLocked = kuramotoR >= threshold;

    return {
      kuramoto_r: Number(kuramotoR.toFixed(6)),
      peak_bin: peakBin,
      peak_phase: Number(this.phaseOfBin(peakBin).toFixed(4)),
      peak_amplitude: Number(peakAmp.toFixed(4)),
      mean_amplitude: Number(meanAmp.toFixed(4)),
      spectral_density: Number(spectralDensity.toFixed(4)),
      coherence_status: isLocked ? 'PHASE_LOCKED' : 'DISSONANT',
      contest_ratio: Number(contestRatio.toFixed(4)),
      tau_k: this.tauK,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Xenial Dissonance Engine: Resolves drift via scale-invariant dampening
   * and power-law dissonance redistribution (k^-Dx where Dx = 2.125).
   */
  public resolveDrift(): {
    dissonance_redistributed: number;
    intrinsic_clock_tick: number;
    damped_bins_count: number;
  } {
    let redistributedTotal = 0;
    const nextReal = new Float64Array(this.bins);
    const nextImag = new Float64Array(this.bins);

    for (let i = 0; i < this.bins; i++) {
      // Apply scale-invariant envelope dampening and carrier projection
      const real = this.realAmplitudes[i] * this.envelopeDampening * this.carrierProjection;
      const imag = this.imagAmplitudes[i] * this.envelopeDampening * this.carrierProjection;
      const amp = Math.sqrt(real * real + imag * imag);

      nextReal[i] += real;
      nextImag[i] += imag;

      // If contested dissonance exists, redistribute along adjacent semantic bins
      const raw = this.rawAbsoluteSum[i];
      const contested = Math.max(0, raw - amp);
      if (contested > 0.001) {
        // Redistribute across neighboring bins using k^-Dx
        for (let k = 1; k <= 3; k++) {
          const factor = Math.pow(k, -this.dxExponent);
          const weightPortion = (contested * factor) / 2;
          const leftBin = (i - k + this.bins) % this.bins;
          const rightBin = (i + k) % this.bins;

          nextReal[leftBin] += weightPortion * 0.5;
          nextReal[rightBin] += weightPortion * 0.5;
          redistributedTotal += weightPortion;
        }
      }
    }

    this.realAmplitudes = nextReal;
    this.imagAmplitudes = nextImag;
    this.intrinsicClockTick += 1;

    return {
      dissonance_redistributed: Number(redistributedTotal.toFixed(6)),
      intrinsic_clock_tick: this.intrinsicClockTick,
      damped_bins_count: this.bins
    };
  }

  /**
   * Exports live stream payload adhering to tauk.harmonic-mode-stream/v1.
   */
  public exportStreamPayload(): HarmonicStreamPayload {
    const lock = this.computePhaseLock(0.8);
    const binSummaries: Array<{ bin: number; phase: number; amplitude: number; share: number }> = [];
    let totalAmp = 0;

    for (let i = 0; i < this.bins; i++) {
      const r = this.realAmplitudes[i];
      const im = this.imagAmplitudes[i];
      const amp = Math.sqrt(r * r + im * im);
      totalAmp += amp;
      binSummaries.push({
        bin: i,
        phase: Number(this.phaseOfBin(i).toFixed(4)),
        amplitude: amp,
        share: 0
      });
    }

    if (totalAmp > 0) {
      for (const b of binSummaries) {
        b.share = Number((b.amplitude / totalAmp).toFixed(4));
      }
    }

    // Sort descending by amplitude
    binSummaries.sort((a, b) => b.amplitude - a.amplitude);

    const activeAgents = Array.from(new Set(this.impulses.map((imp) => imp.agentId)));

    return {
      schema: 'tauk.harmonic-mode-stream/v1',
      timestamp: new Date().toISOString(),
      tau_k: this.tauK,
      cheeger_floor: this.cheegerFloor,
      kuramoto_r: lock.kuramoto_r,
      lock_status: lock.coherence_status,
      spectral_density: lock.spectral_density,
      total_impulses: this.impulses.length,
      active_agents: activeAgents,
      top_harmonic_bins: binSummaries.slice(0, 5)
    };
  }

  public getRawAmplitudes(): { real: number[]; imag: number[] } {
    return {
      real: Array.from(this.realAmplitudes),
      imag: Array.from(this.imagAmplitudes)
    };
  }

  public getImpulseCount(): number {
    return this.impulses.length;
  }
}
