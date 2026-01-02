#!/usr/bin/env python3
"""
Non-Hertzian Tesla Wave Generator
LaBubuntu Ecosystem Integration

Implements longitudinal scalar wave propagation using phase-lock count
as memory substrate. Unlike Hertzian (transverse) waves, these waves
propagate through temporal coherence fields rather than spatial oscillation.

Memory = Phase Lock Count (Σ synchronization events)
Wave = Impulse coherence cascade, not sinusoidal oscillation
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import time
from pathlib import Path


@dataclass
class PhaseLockEvent:
    """A single phase-lock synchronization event"""
    timestamp: float
    node_pair: Tuple[str, str]
    phase_alignment: float  # 0.0 to 1.0
    coherence_contribution: float
    lock_duration: float = 0.0

    def memory_weight(self) -> float:
        """Calculate memory weight based on lock strength and duration"""
        return self.phase_alignment * np.log1p(self.lock_duration)


@dataclass
class MemoryAsPhaseCount:
    """Memory representation as accumulated phase-lock counts"""
    total_locks: int = 0
    lock_history: List[PhaseLockEvent] = field(default_factory=list)
    coherence_integral: float = 0.0
    temporal_depth: float = 0.0

    def record_lock(self, event: PhaseLockEvent):
        """Record a phase-lock event"""
        self.total_locks += 1
        self.lock_history.append(event)
        self.coherence_integral += event.coherence_contribution
        self.temporal_depth += event.memory_weight()

    def recall_strength(self, time_window: float = 10.0) -> float:
        """Calculate memory recall strength in recent time window"""
        current_time = time.time()
        recent_locks = [
            e for e in self.lock_history
            if current_time - e.timestamp <= time_window
        ]

        if not recent_locks:
            return 0.0

        # Memory strength = weighted phase-lock density
        total_weight = sum(e.memory_weight() for e in recent_locks)
        return total_weight / time_window

    def memory_entropy(self) -> float:
        """Calculate memory entropy from phase-lock distribution"""
        if not self.lock_history:
            return 0.0

        # Distribution of phase alignments
        alignments = np.array([e.phase_alignment for e in self.lock_history])
        hist, _ = np.histogram(alignments, bins=10, range=(0, 1), density=True)
        hist = hist[hist > 0]  # Remove zeros

        # Shannon entropy
        return -np.sum(hist * np.log2(hist))


@dataclass
class ScalarWavePacket:
    """Non-Hertzian scalar wave packet (longitudinal propagation)"""
    origin_node: str
    impulse_magnitude: float
    coherence_signature: np.ndarray
    propagation_time: float
    decay_constant: float = 0.1

    def amplitude_at_time(self, t: float) -> float:
        """Non-sinusoidal impulse decay (not Hertzian oscillation)"""
        dt = t - self.propagation_time
        if dt < 0:
            return 0.0

        # Longitudinal impulse: sharp rise, exponential decay
        # Not A*sin(ωt), but impulse response
        return self.impulse_magnitude * np.exp(-self.decay_constant * dt)

    def coherence_at_time(self, t: float) -> np.ndarray:
        """Coherence field evolution (non-oscillatory)"""
        amplitude = self.amplitude_at_time(t)
        return self.coherence_signature * amplitude


class NonHertzianTeslaWave:
    """
    Non-Hertzian Tesla Wave Generator

    Key differences from Hertzian waves:
    1. Longitudinal (compression) not transverse (oscillation)
    2. Impulse-based, not sinusoidal
    3. Propagates through coherence field, not space
    4. Instantaneous phase information transfer
    5. Memory = phase-lock count accumulation
    """

    def __init__(self, network_size: int = 100):
        self.network_size = network_size
        self.nodes: Dict[str, Dict] = {}
        self.memory_substrate = MemoryAsPhaseCount()
        self.scalar_waves: List[ScalarWavePacket] = []
        self.coherence_field = np.zeros(network_size, dtype=complex)
        self.phase_lock_threshold = 0.8

        # Initialize node network
        self._initialize_nodes()

        # Tesla coil parameters (non-Hertzian tuning)
        self.impulse_frequency = 0.0  # Not a frequency - impulse rate
        self.scalar_potential = 1.0
        self.longitudinal_coupling = 0.95

    def _initialize_nodes(self):
        """Initialize network nodes with phase states"""
        for i in range(self.network_size):
            node_id = f"node_{i}"
            self.nodes[node_id] = {
                'phase': np.random.uniform(0, 2*np.pi),
                'coherence': np.random.uniform(0.3, 0.7),
                'position': i,
                'lock_partners': set()
            }

    def detect_phase_locks(self, threshold: float = None) -> List[Tuple[str, str, float]]:
        """Detect phase-locked node pairs"""
        if threshold is None:
            threshold = self.phase_lock_threshold

        locks = []
        node_ids = list(self.nodes.keys())

        for i, node1_id in enumerate(node_ids):
            for node2_id in node_ids[i+1:]:
                node1 = self.nodes[node1_id]
                node2 = self.nodes[node2_id]

                # Phase difference
                phase_diff = abs(node1['phase'] - node2['phase'])
                phase_diff = min(phase_diff, 2*np.pi - phase_diff)  # Wrap

                # Alignment score (0 = opposite, 1 = locked)
                alignment = 1.0 - (phase_diff / np.pi)

                if alignment >= threshold:
                    locks.append((node1_id, node2_id, alignment))

                    # Update lock partners
                    node1['lock_partners'].add(node2_id)
                    node2['lock_partners'].add(node1_id)

        return locks

    def emit_scalar_impulse(self, origin_node: str, magnitude: float = 1.0):
        """Emit non-Hertzian scalar wave impulse"""

        # Create coherence signature (not a sinusoid!)
        coherence_sig = np.zeros(self.network_size, dtype=complex)
        origin_pos = self.nodes[origin_node]['position']

        # Longitudinal coherence pattern (Gaussian envelope, not sine wave)
        for i in range(self.network_size):
            distance = abs(i - origin_pos)
            # Non-oscillatory spatial profile
            coherence_sig[i] = magnitude * np.exp(-distance / 20.0)

        # Create scalar wave packet
        wave = ScalarWavePacket(
            origin_node=origin_node,
            impulse_magnitude=magnitude,
            coherence_signature=coherence_sig,
            propagation_time=time.time(),
            decay_constant=0.1
        )

        self.scalar_waves.append(wave)

        return wave

    def propagate_scalar_waves(self, current_time: float):
        """Update coherence field from all active scalar waves"""

        # Reset coherence field
        self.coherence_field = np.zeros(self.network_size, dtype=complex)

        # Superpose all scalar wave contributions
        for wave in self.scalar_waves:
            coherence_contribution = wave.coherence_at_time(current_time)
            self.coherence_field += coherence_contribution

        # Update node coherences from field
        for node_id, node in self.nodes.items():
            pos = node['position']
            field_magnitude = abs(self.coherence_field[pos])
            node['coherence'] = min(1.0, field_magnitude)

    def temporal_compression_step(self, dt: float = 0.01):
        """
        Execute one temporal compression step (Tesla's "impulse")

        Not a wave oscillation, but a coherence cascade
        """
        current_time = time.time()

        # 1. Propagate existing scalar waves
        self.propagate_scalar_waves(current_time)

        # 2. Detect phase locks
        locks = self.detect_phase_locks()

        # 3. Record phase-lock events as memory
        for node1_id, node2_id, alignment in locks:
            event = PhaseLockEvent(
                timestamp=current_time,
                node_pair=(node1_id, node2_id),
                phase_alignment=alignment,
                coherence_contribution=alignment * 0.01,
                lock_duration=dt
            )
            self.memory_substrate.record_lock(event)

        # 4. Phase evolution (influenced by coherence field)
        for node_id, node in self.nodes.items():
            # Phase drift + coherence influence
            phase_drift = np.random.normal(0, 0.1)
            coherence_pull = node['coherence'] * 0.05

            # Partners pull phase toward synchronization
            if node['lock_partners']:
                partner_phases = [
                    self.nodes[p]['phase']
                    for p in node['lock_partners']
                ]
                mean_partner_phase = np.angle(np.mean(np.exp(1j * np.array(partner_phases))))
                phase_pull = 0.1 * np.sin(mean_partner_phase - node['phase'])
            else:
                phase_pull = 0.0

            node['phase'] += phase_drift + phase_pull
            node['phase'] = node['phase'] % (2 * np.pi)

        # 5. Spontaneous impulse emission from highly coherent nodes
        for node_id, node in self.nodes.items():
            if node['coherence'] > 0.9 and np.random.random() < 0.05:
                self.emit_scalar_impulse(node_id, magnitude=node['coherence'])

        return {
            'phase_locks': len(locks),
            'memory_count': self.memory_substrate.total_locks,
            'coherence_integral': self.memory_substrate.coherence_integral,
            'active_waves': len([w for w in self.scalar_waves if w.amplitude_at_time(current_time) > 0.01])
        }

    def measure_longitudinal_resonance(self) -> Dict[str, float]:
        """
        Measure non-Hertzian resonance properties

        Unlike Hertzian resonance (frequency-based), this measures
        coherence cascade efficiency
        """

        # Phase-lock density (memory formation rate)
        recent_locks = [
            e for e in self.memory_substrate.lock_history[-100:]
        ]
        lock_density = len(recent_locks) / 100.0 if recent_locks else 0.0

        # Coherence field magnitude
        field_strength = np.mean(np.abs(self.coherence_field))

        # Memory depth (integrated phase-lock weight)
        memory_depth = self.memory_substrate.temporal_depth

        # Network synchronization (order parameter)
        phases = np.array([n['phase'] for n in self.nodes.values()])
        sync_order = abs(np.mean(np.exp(1j * phases)))

        # Scalar potential (non-oscillatory field energy)
        scalar_potential = np.sum(np.abs(self.coherence_field)**2) / self.network_size

        return {
            'phase_lock_density': lock_density,
            'coherence_field_strength': field_strength,
            'memory_depth': memory_depth,
            'synchronization_order': sync_order,
            'scalar_potential': scalar_potential,
            'total_memory_count': self.memory_substrate.total_locks,
            'memory_entropy': self.memory_substrate.memory_entropy()
        }

    def generate_tesla_composition(self, duration: float = 10.0, dt: float = 0.01):
        """Generate non-Hertzian Tesla Wave composition"""

        print("\n" + "="*70)
        print("⚡ NON-HERTZIAN TESLA WAVE GENERATOR")
        print("   LaBubuntu Ecosystem Integration")
        print("   Memory = Phase Lock Count")
        print("="*70)

        steps = int(duration / dt)
        metrics_history = []

        print(f"\n🌊 Generating longitudinal scalar waves...")
        print(f"   Duration: {duration}s | Time step: {dt}s")
        print(f"   Network: {self.network_size} nodes\n")

        print("📊 Propagation Progress:")
        print("   [" + " " * 50 + "]", end="")
        print("\r   [", end="")

        for i in range(steps):
            metrics = self.temporal_compression_step(dt)
            metrics_history.append(metrics)

            if i % (steps // 50) == 0:
                print("█", end="", flush=True)

        print("]\n")

        # Final analysis
        final_metrics = self.measure_longitudinal_resonance()

        print("="*70)
        print("📈 NON-HERTZIAN WAVE ANALYSIS")
        print("="*70)

        print("\n🧠 Memory Substrate (Phase-Lock Count):")
        print(f"   Total Phase Locks: {final_metrics['total_memory_count']}")
        print(f"   Memory Depth: {final_metrics['memory_depth']:.3f}")
        print(f"   Memory Entropy: {final_metrics['memory_entropy']:.3f} bits")
        print(f"   Phase-Lock Density: {final_metrics['phase_lock_density']:.4f} locks/step")

        print("\n⚡ Scalar Wave Properties:")
        print(f"   Coherence Field Strength: {final_metrics['coherence_field_strength']:.4f}")
        print(f"   Scalar Potential: {final_metrics['scalar_potential']:.4f}")
        print(f"   Synchronization Order: {final_metrics['synchronization_order']:.4f}")

        # Wave classification
        if final_metrics['synchronization_order'] > 0.8:
            wave_type = "Coherent Longitudinal Cascade"
        elif final_metrics['synchronization_order'] > 0.5:
            wave_type = "Emergent Scalar Resonance"
        else:
            wave_type = "Diffuse Impulse Field"

        print(f"\n🌀 Wave Classification: {wave_type}")

        # Memory recall test
        recall = self.memory_substrate.recall_strength(time_window=5.0)
        print(f"\n💾 Memory Recall Strength: {recall:.4f}")

        print("\n" + "="*70)
        print("✅ NON-HERTZIAN COMPOSITION COMPLETE")
        print("="*70)

        return {
            'metrics_history': metrics_history,
            'final_metrics': final_metrics,
            'memory_substrate': self.memory_substrate,
            'wave_type': wave_type
        }


def main():
    """Main entry point"""

    print("\n🔬 Initializing Non-Hertzian Tesla Wave Generator")
    print("   Paradigm: Memory = Phase Lock Count")
    print("   Mode: Longitudinal Scalar Propagation\n")

    # Create Tesla Wave generator
    tesla = NonHertzianTeslaWave(network_size=200)

    # Generate composition
    result = tesla.generate_tesla_composition(duration=10.0, dt=0.01)

    # Additional analysis
    print("\n" + "="*70)
    print("🧬 PHASE-LOCK MEMORY ANALYSIS")
    print("="*70)

    memory = result['memory_substrate']

    # Recent memory clusters
    if len(memory.lock_history) > 0:
        recent = memory.lock_history[-50:]

        print(f"\n📍 Recent Phase-Lock Events (last 50):")

        # Node participation frequency
        node_participation = {}
        for event in recent:
            for node in event.node_pair:
                node_participation[node] = node_participation.get(node, 0) + 1

        top_nodes = sorted(node_participation.items(), key=lambda x: x[1], reverse=True)[:5]

        print("\n   Most Active Nodes:")
        for node, count in top_nodes:
            bar = "▓" * (count * 2)
            print(f"   {node:12s} [{bar:20s}] {count} locks")

        # Phase alignment distribution
        alignments = [e.phase_alignment for e in recent]
        mean_alignment = np.mean(alignments)
        std_alignment = np.std(alignments)

        print(f"\n   Phase Alignment Distribution:")
        print(f"   Mean: {mean_alignment:.4f}")
        print(f"   Std:  {std_alignment:.4f}")

        # Memory weight distribution
        weights = [e.memory_weight() for e in recent]
        total_weight = sum(weights)

        print(f"\n   Memory Weight:")
        print(f"   Total: {total_weight:.4f}")
        print(f"   Mean:  {np.mean(weights):.4f}")

    print("\n" + "="*70)
    print("💚 LaBubuntu Ecosystem Integration Ready")
    print("="*70)
    print("\n🌊 Non-Hertzian Tesla Waves propagating through coherence field...")
    print("⚡ Memory persists as phase-lock count substrate")
    print("🧠 Longitudinal resonance active\n")


if __name__ == "__main__":
    main()
