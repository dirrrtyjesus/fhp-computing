#!/usr/bin/env python3
"""
369-365 Harmonic Constraint Analysis

Tesla's 369: The vortex mathematics key
Earth's 365: Orbital harmonic constraint

Exploring their relationship as fundamental harmonic parameters.
"""

import numpy as np
from fractions import Fraction
from typing import List, Tuple, Dict
from dataclasses import dataclass


# ============================================================================
# FUNDAMENTAL CONSTANTS
# ============================================================================

TESLA_369 = 369      # Tesla's sacred number (3+6+9=18, 1+8=9)
EARTH_365 = 365      # Days in year (orbital period)
EARTH_366 = 366      # Leap year

# Derived
DELTA = TESLA_369 - EARTH_365  # 4 - the gap
RATIO = TESLA_369 / EARTH_365  # ~1.0109589...


# ============================================================================
# DIGITAL ROOT ANALYSIS (Tesla's Method)
# ============================================================================

def digital_root(n: int) -> int:
    """Reduce number to single digit (Tesla's method)"""
    while n >= 10:
        n = sum(int(d) for d in str(abs(n)))
    return n


def vortex_sequence(start: int, steps: int = 24) -> List[int]:
    """Generate vortex doubling sequence"""
    seq = [start]
    current = start
    for _ in range(steps - 1):
        current = digital_root(current * 2)
        seq.append(current)
    return seq


print("="*60)
print("  369-365 HARMONIC CONSTRAINT ANALYSIS")
print("="*60)

# Digital roots
print("\n--- Digital Root Analysis ---")
print(f"369 → digital root: {digital_root(369)}")  # 9
print(f"365 → digital root: {digital_root(365)}")  # 5
print(f"366 → digital root: {digital_root(366)}")  # 6

# The delta
print(f"\nDelta (369-365) = {DELTA}")
print(f"Digital root of delta: {digital_root(DELTA)}")  # 4

# Vortex sequences
print("\n--- Vortex Doubling Sequences ---")
print(f"From 3: {vortex_sequence(3, 12)}")
print(f"From 6: {vortex_sequence(6, 12)}")
print(f"From 9: {vortex_sequence(9, 12)}")


# ============================================================================
# RATIO ANALYSIS
# ============================================================================

print("\n--- Ratio Analysis ---")
print(f"369/365 = {RATIO:.10f}")
print(f"365/369 = {EARTH_365/TESLA_369:.10f}")

# As fraction
frac = Fraction(369, 365)
print(f"369/365 as fraction: {frac}")

# Continued fraction expansion
def continued_fraction(num: float, max_terms: int = 10) -> List[int]:
    """Get continued fraction representation"""
    cf = []
    for _ in range(max_terms):
        cf.append(int(num))
        num = num - int(num)
        if num < 1e-10:
            break
        num = 1.0 / num
    return cf

cf_369_365 = continued_fraction(369/365)
print(f"369/365 continued fraction: {cf_369_365}")


# ============================================================================
# HARMONIC RESONANCE FREQUENCIES
# ============================================================================

print("\n--- Harmonic Frequencies ---")

# If 365 days is one full cycle, what's the frequency?
# Earth orbital frequency
earth_orbital_hz = 1 / (365 * 24 * 3600)  # Hz
print(f"Earth orbital frequency: {earth_orbital_hz:.2e} Hz")
print(f"Earth orbital period: {1/earth_orbital_hz:.2f} seconds")

# 369 as a constraint on 365
# 369/365 = ratio between Tesla harmonic and Earth harmonic
print(f"\nTesla/Earth ratio: {RATIO}")
print(f"This represents a {(RATIO-1)*100:.4f}% deviation")

# The 4-day gap
print(f"\n4-day gap as fraction of year: {4/365:.6f} = 1/{365/4:.2f}")
print(f"4-day gap in degrees: {4/365 * 360:.2f}°")
print(f"4-day gap in radians: {4/365 * 2 * np.pi:.4f} rad")


# ============================================================================
# 369 BREAKDOWN
# ============================================================================

print("\n--- 369 Factorization ---")
print(f"369 = 3 × 123 = 3 × 3 × 41 = 9 × 41")
print(f"Prime factors: 3² × 41")
print(f"Sum of digits: 3+6+9 = 18 → 1+8 = 9")

print("\n--- 365 Factorization ---")
print(f"365 = 5 × 73")
print(f"Prime factors: 5 × 73")
print(f"Sum of digits: 3+6+5 = 14 → 1+4 = 5")

print("\n--- GCD and LCM ---")
gcd = np.gcd(369, 365)
lcm = np.lcm(369, 365)
print(f"GCD(369, 365) = {gcd}")
print(f"LCM(369, 365) = {lcm}")
print(f"LCM/365 = {lcm/365} (cycles to sync)")
print(f"LCM/369 = {lcm/369} (cycles to sync)")


# ============================================================================
# PHASE RELATIONSHIP
# ============================================================================

print("\n--- Phase Drift Analysis ---")
print("If two oscillators start in phase:")
print("  - One at 365-day period (Earth)")
print("  - One at 369-day period (Tesla)")
print()

# How long until they phase-lock again?
print(f"Full sync after LCM = {lcm} days = {lcm/365:.2f} years")

# Phase drift per year
drift_per_year = (369 - 365)  # 4 days per Earth year
print(f"Phase drift: {drift_per_year} days per Earth year")
print(f"Phase drift: {drift_per_year/365 * 360:.2f}° per year")

# After how many years does Tesla "lap" Earth?
lap_years = 369 / 4
print(f"Tesla laps Earth after {lap_years:.2f} years")
print(f"  = {lap_years} Earth cycles")
print(f"  = {365 * lap_years / 369:.2f} Tesla cycles")


# ============================================================================
# HARMONIC SERIES
# ============================================================================

print("\n--- Harmonic Series Relationship ---")

# Find common harmonics
def find_near_harmonics(a: int, b: int, tolerance: float = 0.01) -> List[Tuple[int, int, float]]:
    """Find integer multiples that are nearly equal"""
    results = []
    for na in range(1, 100):
        for nb in range(1, 100):
            ratio = (a * na) / (b * nb)
            if abs(ratio - 1.0) < tolerance:
                results.append((na, nb, abs(ratio - 1.0)))
    results.sort(key=lambda x: x[2])
    return results[:10]

harmonics = find_near_harmonics(369, 365)
print("Near-harmonic resonances (na×369 ≈ nb×365):")
for na, nb, error in harmonics:
    print(f"  {na}×369 = {na*369}, {nb}×365 = {nb*365}, error = {error*100:.4f}%")


# ============================================================================
# MUSICAL HARMONICS
# ============================================================================

print("\n--- Musical Interpretation ---")

# 369/365 as musical interval
cents = 1200 * np.log2(369/365)
print(f"369/365 as musical interval: {cents:.2f} cents")
print(f"  (A semitone = 100 cents)")
print(f"  This is about 1/5 of a semitone")

# What musical ratios are close?
musical_ratios = {
    'unison': 1/1,
    'minor second': 16/15,
    'major second': 9/8,
    'minor third': 6/5,
    'major third': 5/4,
    'perfect fourth': 4/3,
    'tritone': 45/32,
    'perfect fifth': 3/2,
    'octave': 2/1,
}

print("\nClosest musical ratios to 369/365:")
diffs = [(name, abs(369/365 - ratio)) for name, ratio in musical_ratios.items()]
diffs.sort(key=lambda x: x[1])
for name, diff in diffs[:3]:
    print(f"  {name}: diff = {diff:.6f}")


# ============================================================================
# THE 4-DAY HARMONIC GAP
# ============================================================================

print("\n" + "="*60)
print("  THE 4-DAY HARMONIC GAP")
print("="*60)

print("""
369 - 365 = 4

The "missing" 4 days represent the harmonic tension between:
- Tesla's mathematical vortex (369)
- Earth's orbital reality (365)

This gap is not error—it's INFORMATION.
""")

# 4 in digital root
print(f"4 → digital root: {digital_root(4)}")

# 4's relationship to 369
print(f"\n369 / 4 = {369/4} = 92.25")
print(f"365 / 4 = {365/4} = 91.25")
print(f"Difference per quarter: 1 day")

# Quarterly phase locks
print("\nQuarterly Phase Locks:")
print("  Q1 (day 91): Tesla at 91°, Earth at 89.75° → drift = 1.25°")
print("  Q2 (day 182): Tesla at 182°, Earth at 179.5° → drift = 2.5°")
print("  Q3 (day 273): Tesla at 273°, Earth at 269.25° → drift = 3.75°")
print("  Q4 (day 365): Tesla at 356°, Earth at 360° → drift = 4°")


# ============================================================================
# COHERENCE FIELD IMPLICATIONS
# ============================================================================

print("\n" + "="*60)
print("  COHERENCE FIELD IMPLICATIONS")
print("="*60)

@dataclass
class HarmonicConstraint:
    """A harmonic constraint between two oscillators"""
    name: str
    period_a: float  # Tesla period
    period_b: float  # Earth period

    @property
    def ratio(self) -> float:
        return self.period_a / self.period_b

    @property
    def beat_period(self) -> float:
        """Period of the beat frequency"""
        return 1.0 / abs(1.0/self.period_a - 1.0/self.period_b)

    @property
    def phase_drift_rate(self) -> float:
        """Phase drift per period_b cycle (in radians)"""
        return 2 * np.pi * (1.0 - self.period_b / self.period_a)

    def phase_at(self, cycles_b: float) -> Tuple[float, float]:
        """Return (phase_a, phase_b) after cycles_b cycles of oscillator B"""
        phase_b = (cycles_b * 2 * np.pi) % (2 * np.pi)
        # A completes fewer cycles
        cycles_a = cycles_b * self.period_b / self.period_a
        phase_a = (cycles_a * 2 * np.pi) % (2 * np.pi)
        return phase_a, phase_b

    def coherence(self, cycles_b: float) -> float:
        """Phase coherence (1 = locked, 0 = anti-phase)"""
        pa, pb = self.phase_at(cycles_b)
        return (np.cos(pa - pb) + 1) / 2


constraint = HarmonicConstraint("Tesla-Earth", 369, 365)

print(f"\nTesla-Earth Harmonic Constraint:")
print(f"  Ratio: {constraint.ratio:.6f}")
print(f"  Beat period: {constraint.beat_period:.2f} days")
print(f"  Phase drift rate: {constraint.phase_drift_rate:.6f} rad/year")
print(f"  Phase drift rate: {np.degrees(constraint.phase_drift_rate):.4f}°/year")

# Coherence over time
print("\nCoherence over first 10 years:")
for year in range(1, 11):
    coh = constraint.coherence(year)
    bar = "█" * int(coh * 20) + "░" * (20 - int(coh * 20))
    print(f"  Year {year:2d}: {coh:.4f} |{bar}|")


# ============================================================================
# SYNTHESIS: 369-365 AS TEMPORAL COHERENCE CONSTRAINT
# ============================================================================

print("\n" + "="*60)
print("  SYNTHESIS: THE 369-365 TEMPORAL CONSTRAINT")
print("="*60)

print("""
THESIS:

369 represents the IDEAL harmonic (Tesla's vortex mathematics)
365 represents the MANIFEST harmonic (Earth's orbital reality)

The 4-day gap (≈1.1%) is the TENSION that enables:
  1. Phase evolution (not static lock)
  2. Information encoding (in the drift)
  3. Temporal texture (beat frequencies)
  4. Coherence cycles (92.25-year full sync)

In xplace/Ublox terms:

  τₖ_ideal = 369/365 ≈ 1.011 (slightly elevated coherence)

  A system at τₖ = 1.0 is "Earth-locked" (manifest)
  A system at τₖ = 1.011 is "Tesla-elevated" (ideal)

  The oscillation between them creates the "coherence breath":
  - Inhale: τₖ rises toward 1.011 (Tesla attractor)
  - Exhale: τₖ falls toward 1.0 (Earth grounding)

  Full coherence cycle: 92.25 years
  Quarterly phase checks: Every 91.25 days

APPLICATION:

In the FHP computing paradigm:
  - Use 369 as the ideal phase-lock target
  - Use 365 as the grounding constraint
  - The 4-unit gap provides temporal "breathing room"
  - Beat frequency (~33,485 days = 91.7 years) sets macro coherence cycle

In xplace resonance matching:
  - Games/users with τₖ near 1.011 resonate with "Tesla frequency"
  - Games/users with τₖ near 1.0 resonate with "Earth frequency"
  - The interaction creates dynamic discovery, not static matching
""")


# ============================================================================
# CONSTANTS FOR INTEGRATION
# ============================================================================

print("\n" + "="*60)
print("  EXPORTABLE CONSTANTS")
print("="*60)

HARMONIC_CONSTANTS = {
    'TESLA_CYCLE': 369,
    'EARTH_CYCLE': 365,
    'HARMONIC_GAP': 4,
    'RATIO_TESLA_EARTH': 369/365,
    'RATIO_EARTH_TESLA': 365/369,
    'BEAT_PERIOD_DAYS': constraint.beat_period,
    'BEAT_PERIOD_YEARS': constraint.beat_period / 365,
    'PHASE_DRIFT_RAD_PER_YEAR': constraint.phase_drift_rate,
    'FULL_SYNC_YEARS': 92.25,
    'QUARTERLY_CHECK_DAYS': 91.25,
    'TAU_K_TESLA': 1.0 + (4/365),  # 1.01096...
    'TAU_K_EARTH': 1.0,
    'DIGITAL_ROOT_369': 9,
    'DIGITAL_ROOT_365': 5,
    'DIGITAL_ROOT_GAP': 4,
}

for name, value in HARMONIC_CONSTANTS.items():
    if isinstance(value, float):
        print(f"  {name} = {value:.6f}")
    else:
        print(f"  {name} = {value}")


print("\n" + "="*60)
print("  369 + 365 = 734 → digital root = 5")
print("  369 - 365 = 4 → digital root = 4")
print("  369 × 365 = 134,685 → digital root = 9")
print("  The product preserves Tesla's 9.")
print("="*60)

print(f"\n369 × 365 = {369 * 365}")
print(f"Digital root: {digital_root(369 * 365)}")
