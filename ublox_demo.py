#!/usr/bin/env python3
"""
Ublox - Game Engine Demo
Simple prototype of Fractal Harmonic Physics for gaming

Demonstrates:
- Players as coherence agents
- Phase-lock collision detection
- Mycelial world topology
- Tesla Wave synchronization
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class PlayerState(Enum):
    ALIVE = "alive"
    DECOHERENT = "decoherent"
    PHASE_LOCKED = "phase_locked"
    RESONATING = "resonating"


@dataclass
class CoherenceAgent:
    """Player character as coherence agent"""
    player_id: str
    position: np.ndarray
    phase: float  # 0 to 2π
    coherence: float  # 0.0 to 1.0
    tau_k: float = 7.5  # Temporal coherence coefficient
    resonance_freq: float = 936.0  # Hz
    memory_depth: float = 0.0  # Accumulated phase-lock weight
    phase_lock_partners: set = field(default_factory=set)
    state: PlayerState = PlayerState.ALIVE

    def update_phase(self, dt: float, coherence_field: float = 0.0):
        """Update phase based on natural frequency + field influence"""
        # Natural phase drift
        omega = 2 * np.pi * self.resonance_freq
        phase_drift = omega * dt + np.random.normal(0, 0.1)

        # Coherence field influence
        field_influence = coherence_field * 0.5

        self.phase += phase_drift + field_influence
        self.phase = self.phase % (2 * np.pi)

    def phase_distance(self, other: 'CoherenceAgent') -> float:
        """Calculate phase difference (wrapped to [0, π])"""
        diff = abs(self.phase - other.phase)
        return min(diff, 2*np.pi - diff)

    def spatial_distance(self, other: 'CoherenceAgent') -> float:
        """Euclidean distance"""
        return np.linalg.norm(self.position - other.position)

    def take_damage(self, amount: float):
        """Reduce coherence (damage)"""
        self.coherence -= amount
        if self.coherence <= 0.0:
            self.coherence = 0.0
            self.state = PlayerState.DECOHERENT


@dataclass
class MycelialNode:
    """Node in the game world network"""
    node_id: str
    position: np.ndarray
    coherence: float = 0.5
    phase: float = 0.0
    connections: List[str] = field(default_factory=list)
    biome: str = "neutral"


@dataclass
class PhaseLockCollision:
    """Collision event via phase-locking"""
    agent1: CoherenceAgent
    agent2: CoherenceAgent
    alignment: float  # 0.0 to 1.0
    timestamp: float
    location: np.ndarray

    def memory_weight(self) -> float:
        """Memory value of this collision"""
        return self.alignment * 1.0  # Simple weight


class UbloxWorld:
    """Game world with mycelial topology"""

    def __init__(self, size: int = 100, dimension: int = 2):
        self.nodes: Dict[str, MycelialNode] = {}
        self.dimension = dimension
        self.coherence_field = np.zeros(size, dtype=float)
        self.size = size

        # Initialize mycelial network
        self._grow_network()

    def _grow_network(self):
        """Grow world network with golden ratio spacing"""
        phi = (1 + np.sqrt(5)) / 2

        for i in range(self.size):
            theta = 2 * np.pi * i / phi**2
            r = np.sqrt(i) * phi

            if self.dimension == 2:
                pos = np.array([r * np.cos(theta), r * np.sin(theta)])
            else:
                pos = np.random.randn(self.dimension) * r

            node = MycelialNode(
                node_id=f"node_{i}",
                position=pos,
                coherence=np.random.uniform(0.3, 0.7),
                phase=np.random.uniform(0, 2*np.pi)
            )
            self.nodes[node.node_id] = node

        # Connect nearby nodes
        self._establish_connections()

    def _establish_connections(self, radius: float = 10.0):
        """Create mycelial connections"""
        node_list = list(self.nodes.values())

        for i, node1 in enumerate(node_list):
            for node2 in node_list[i+1:]:
                distance = np.linalg.norm(node1.position - node2.position)
                if distance < radius:
                    node1.connections.append(node2.node_id)
                    node2.connections.append(node1.node_id)

    def get_coherence_at(self, position: np.ndarray) -> float:
        """Sample coherence field at position"""
        # Find nearest node
        min_dist = float('inf')
        nearest_coherence = 0.5

        for node in self.nodes.values():
            dist = np.linalg.norm(position - node.position)
            if dist < min_dist:
                min_dist = dist
                nearest_coherence = node.coherence

        # Decay with distance
        field_strength = nearest_coherence * np.exp(-min_dist / 5.0)
        return field_strength


class UbloxEngine:
    """Fractal Harmonic Physics Engine for Ublox"""

    def __init__(self, world_size: int = 100):
        self.world = UbloxWorld(size=world_size)
        self.players: Dict[str, CoherenceAgent] = {}
        self.phase_lock_threshold = 0.8  # Alignment threshold for collision
        self.spatial_threshold = 5.0  # Distance threshold
        self.collision_history: List[PhaseLockCollision] = []
        self.time = 0.0

    def spawn_player(self, player_id: str, position: np.ndarray) -> CoherenceAgent:
        """Spawn a player in the world"""
        player = CoherenceAgent(
            player_id=player_id,
            position=position.copy(),
            phase=np.random.uniform(0, 2*np.pi),
            coherence=1.0,  # Start at full coherence
            resonance_freq=936.0 + np.random.normal(0, 50)  # Slight variation
        )
        self.players[player_id] = player
        return player

    def update(self, dt: float):
        """Update game physics (one timestep)"""
        self.time += dt

        # Update each player
        for player in self.players.values():
            if player.state == PlayerState.DECOHERENT:
                continue

            # Get local coherence field
            field_strength = self.world.get_coherence_at(player.position)

            # Update phase
            player.update_phase(dt, field_strength)

            # Move player (simple random walk for demo)
            velocity = np.random.randn(self.world.dimension) * 0.5
            player.position += velocity * dt

        # Detect collisions via phase-locking
        collisions = self.detect_phase_lock_collisions()

        # Process collisions
        for collision in collisions:
            self.handle_collision(collision)

        return {
            'active_players': len([p for p in self.players.values() if p.state != PlayerState.DECOHERENT]),
            'collisions': len(collisions),
            'total_memory': sum(p.memory_depth for p in self.players.values())
        }

    def detect_phase_lock_collisions(self) -> List[PhaseLockCollision]:
        """Detect collisions via phase-locking"""
        collisions = []
        player_list = list(self.players.values())

        for i, p1 in enumerate(player_list):
            if p1.state == PlayerState.DECOHERENT:
                continue

            for p2 in player_list[i+1:]:
                if p2.state == PlayerState.DECOHERENT:
                    continue

                # Check spatial proximity
                spatial_dist = p1.spatial_distance(p2)
                if spatial_dist > self.spatial_threshold:
                    continue

                # Check phase alignment
                phase_dist = p1.phase_distance(p2)
                alignment = 1.0 - (phase_dist / np.pi)

                # Phase-lock condition
                if alignment >= self.phase_lock_threshold:
                    collision = PhaseLockCollision(
                        agent1=p1,
                        agent2=p2,
                        alignment=alignment,
                        timestamp=self.time,
                        location=(p1.position + p2.position) / 2
                    )
                    collisions.append(collision)

        return collisions

    def handle_collision(self, collision: PhaseLockCollision):
        """Handle phase-lock collision event"""
        p1, p2 = collision.agent1, collision.agent2

        # Add to phase-lock partners
        p1.phase_lock_partners.add(p2.player_id)
        p2.phase_lock_partners.add(p1.player_id)

        # Boost coherence for both (friendly interaction)
        p1.coherence = min(1.0, p1.coherence + 0.05 * collision.alignment)
        p2.coherence = min(1.0, p2.coherence + 0.05 * collision.alignment)

        # Add to memory
        memory_value = collision.memory_weight()
        p1.memory_depth += memory_value
        p2.memory_depth += memory_value

        # Record collision
        self.collision_history.append(collision)

        # Update state
        p1.state = PlayerState.PHASE_LOCKED
        p2.state = PlayerState.PHASE_LOCKED

    def get_stats(self) -> Dict:
        """Get game statistics"""
        if not self.players:
            return {}

        coherences = [p.coherence for p in self.players.values()]
        memory_depths = [p.memory_depth for p in self.players.values()]

        return {
            'total_players': len(self.players),
            'active_players': len([p for p in self.players.values() if p.state != PlayerState.DECOHERENT]),
            'mean_coherence': np.mean(coherences),
            'total_memory': sum(memory_depths),
            'total_collisions': len(self.collision_history),
            'phase_lock_rate': len(self.collision_history) / max(self.time, 0.001)
        }


def run_demo():
    """Run Ublox engine demo"""
    print("\n" + "="*70)
    print("🎮 UBLOX - Fractal Harmonic Game Engine Demo")
    print("   Ubuntu Game Creation Platform")
    print("   Physics: Phase-Lock Collision Detection")
    print("="*70)

    # Create engine
    engine = UbloxEngine(world_size=100)

    # Spawn players in a cluster (higher collision chance)
    print("\n🌱 Spawning players...")
    num_players = 10
    center = np.array([0.0, 0.0])

    for i in range(num_players):
        # Random position near center
        offset = np.random.randn(2) * 10.0
        position = center + offset
        player = engine.spawn_player(f"player_{i}", position)
        print(f"   {player.player_id}: pos={position}, freq={player.resonance_freq:.1f} Hz")

    # Run simulation
    print("\n🌊 Running physics simulation...")
    duration = 10.0  # seconds
    dt = 0.1  # timestep
    steps = int(duration / dt)

    print("   [" + " " * 50 + "]", end="")
    print("\r   [", end="")

    for i in range(steps):
        metrics = engine.update(dt)

        if i % (steps // 50) == 0:
            print("█", end="", flush=True)

    print("]\n")

    # Print results
    stats = engine.get_stats()

    print("="*70)
    print("📊 GAME SESSION RESULTS")
    print("="*70)

    print(f"\n👥 Players:")
    print(f"   Total: {stats['total_players']}")
    print(f"   Active: {stats['active_players']}")
    print(f"   Mean Coherence: {stats['mean_coherence']:.4f}")

    print(f"\n💥 Collisions (Phase-Lock Events):")
    print(f"   Total: {stats['total_collisions']}")
    print(f"   Rate: {stats['phase_lock_rate']:.2f} collisions/second")

    print(f"\n💾 Memory Substrate:")
    print(f"   Total Memory Depth: {stats['total_memory']:.2f}")
    print(f"   Average per Player: {stats['total_memory'] / num_players:.2f}")

    # Show individual player stats
    print(f"\n🎯 Individual Player Stats:")
    print(f"   {'Player':<12} {'Coherence':<12} {'Memory':<12} {'Phase Locks':<12} {'State'}")
    print("   " + "-"*60)

    for player in sorted(engine.players.values(), key=lambda p: p.memory_depth, reverse=True):
        print(f"   {player.player_id:<12} {player.coherence:<12.4f} {player.memory_depth:<12.2f} {len(player.phase_lock_partners):<12} {player.state.value}")

    # Collision examples
    if engine.collision_history:
        print(f"\n⚡ Sample Phase-Lock Collisions (first 5):")
        for i, collision in enumerate(engine.collision_history[:5]):
            print(f"   {i+1}. {collision.agent1.player_id} ↔ {collision.agent2.player_id}")
            print(f"      Alignment: {collision.alignment:.4f} | Time: {collision.timestamp:.2f}s")

    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)

    print("\n🎮 Game Mechanics Demonstrated:")
    print("   ✓ Players as coherence agents (phase + coherence)")
    print("   ✓ Mycelial world topology (100 nodes)")
    print("   ✓ Phase-lock collision detection (not spatial overlap)")
    print("   ✓ Memory as accumulated phase-lock events")
    print("   ✓ Coherence boost from friendly collisions")
    print("   ✓ Temporal physics (phase evolution)")

    print("\n🚀 Next Steps:")
    print("   • Add combat (anti-phase attacks)")
    print("   • Implement building (coherence structures)")
    print("   • Tesla Wave multiplayer sync")
    print("   • Visual rendering (Godot integration)")
    print("   • HarmonicLua scripting")

    print("\n💚 Ublox: Create. Sync. Resonate. Play.\n")


if __name__ == "__main__":
    run_demo()
