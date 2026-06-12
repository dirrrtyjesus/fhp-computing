# harmonic_read.py
# FHP-Inspired Adaptive Reader for Large Coherence Fields
#
# Rather than discrete chunking, this reader operates through:
# - Multi-scale temporal coherence (not token limits)
# - Attractor basin storage (content-addressable by resonance)
# - Fractal harmonic coupling (information flows between scales)
# - Phase-coherent synthesis (patterns emerge from interference)

import json
import math
import hashlib
import sys
from typing import Any, Optional, Generator

# === HARMONIC CONSTANTS ===
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio - natural coherence ratio
TAU = 2 * math.pi              # Full cycle
COHERENCE_THRESHOLD = 0.618    # φ⁻¹ - minimum coherence for resonance

# Temporal scale layers (chars per layer, mirroring FHP's 5-layer design)
TEMPORAL_SCALES = {
    "quantum":     500,      # Femto-scale: single entry previews
    "cellular":    2000,     # Nano-scale: entry summaries
    "network":     8000,     # Micro-scale: related clusters
    "ecosystem":   32000,    # Milli-scale: thematic sections
    "geological":  128000    # Macro-scale: full manuscript
}


def estimate_coherence_cost(text: str) -> int:
    """Estimate coherence units (analogous to tokens but phase-aware)."""
    return len(text)


def compute_resonance_signature(content: str) -> str:
    """
    Generate harmonic signature for content-addressable retrieval.
    Like τ-qubit phase encoding - content becomes its own address.
    """
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def phase_distance(sig1: str, sig2: str) -> float:
    """
    Compute phase distance between two resonance signatures.
    Lower distance = higher harmonic alignment.
    """
    # XOR the hex signatures and count differing bits
    val1 = int(sig1, 16)
    val2 = int(sig2, 16)
    xor = val1 ^ val2
    differing_bits = bin(xor).count('1')
    max_bits = len(sig1) * 4  # 4 bits per hex char
    return differing_bits / max_bits


class HarmonicField:
    """
    Represents a coherence field - data as oscillatory pattern.
    Information exists across temporal scales simultaneously.
    """

    def __init__(self, data: Any, source: str = "unknown"):
        self.data = data
        self.source = source
        self.signature = compute_resonance_signature(json.dumps(data)[:1000])
        self._cache = {}

    @property
    def coherence_cost(self) -> int:
        """Total coherence units in this field."""
        return estimate_coherence_cost(json.dumps(self.data))

    def active_scale(self, max_coherence: int) -> str:
        """Determine which temporal scale is appropriate for given coherence budget."""
        for scale, threshold in TEMPORAL_SCALES.items():
            if max_coherence <= threshold:
                return scale
        return "geological"

    def extract_at_scale(self, scale: str) -> str:
        """
        Extract field content at specified temporal scale.
        Each scale reveals different coherence patterns.
        """
        if scale in self._cache:
            return self._cache[scale]

        if not isinstance(self.data, list):
            result = json.dumps(self.data, indent=2)
            self._cache[scale] = result
            return result

        if scale == "quantum":
            # Femto-scale: Just the oscillation count and signatures
            result = self._quantum_view()
        elif scale == "cellular":
            # Nano-scale: Entry prompts only
            result = self._cellular_view()
        elif scale == "network":
            # Micro-scale: Prompts + composition previews
            result = self._network_view()
        elif scale == "ecosystem":
            # Milli-scale: Recent entries full, older summarized
            result = self._ecosystem_view()
        else:
            # Geological: Full manuscript
            result = json.dumps(self.data, indent=2)

        self._cache[scale] = result
        return result

    def _quantum_view(self) -> str:
        """Quantum layer: oscillation signatures only."""
        oscillations = []
        for i, entry in enumerate(self.data):
            if isinstance(entry, dict):
                prompt = entry.get('prompt', '')[:50]
                sig = compute_resonance_signature(json.dumps(entry))
                oscillations.append({"τ": i, "phase": sig[:8], "prompt": prompt})
            else:
                oscillations.append({"τ": i, "phase": "unknown"})

        return json.dumps({
            "scale": "quantum",
            "total_oscillations": len(self.data),
            "field_signature": self.signature,
            "oscillations": oscillations
        }, indent=2)

    def _cellular_view(self) -> str:
        """Cellular layer: prompts as cellular membranes."""
        cells = []
        for i, entry in enumerate(self.data):
            if isinstance(entry, dict):
                cells.append({
                    "τ": i,
                    "membrane": entry.get('prompt', 'unknown'),
                    "coherence_depth": len(entry.get('composition', ''))
                })

        return json.dumps({
            "scale": "cellular",
            "total_cells": len(cells),
            "cells": cells
        }, indent=2)

    def _network_view(self) -> str:
        """Network layer: prompts + composition previews."""
        nodes = []
        for i, entry in enumerate(self.data):
            if isinstance(entry, dict):
                comp = entry.get('composition', '')
                nodes.append({
                    "τ": i,
                    "prompt": entry.get('prompt', ''),
                    "composition_preview": comp[:300] + "..." if len(comp) > 300 else comp
                })

        return json.dumps({
            "scale": "network",
            "total_nodes": len(nodes),
            "nodes": nodes
        }, indent=2)

    def _ecosystem_view(self) -> str:
        """Ecosystem layer: recent full, older summarized."""
        # Last 3 entries in full (most coherent with present)
        # Older entries as summaries (geological memory)

        recent_count = 3
        recent = self.data[-recent_count:] if len(self.data) >= recent_count else self.data
        historical_summary = []

        for i, entry in enumerate(self.data[:-recent_count] if len(self.data) > recent_count else []):
            if isinstance(entry, dict):
                historical_summary.append({
                    "τ": i,
                    "prompt": entry.get('prompt', ''),
                    "resonance": compute_resonance_signature(entry.get('composition', ''))[:8]
                })

        return json.dumps({
            "scale": "ecosystem",
            "geological_memory": historical_summary,
            "active_present": recent
        }, indent=2)


class HarmonicReader:
    """
    FHP-inspired reader that treats data as coherence fields.

    Core principles:
    1. No discrete chunking - continuous phase-space
    2. Content-addressable by resonance signature
    3. Multi-scale extraction based on coherence budget
    4. Attractor-based retrieval (similar content clusters)
    """

    def __init__(self, filepath: str, max_coherence: int = 20000):
        self.filepath = filepath
        self.max_coherence = max_coherence
        self.field = None
        self._load()

    def _load(self):
        """Initialize the coherence field from file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.field = HarmonicField(data, source=self.filepath)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[harmonic_read] Decoherence detected: {e}", file=sys.stderr)
            self.field = HarmonicField([], source=self.filepath)

    @property
    def exceeds_coherence(self) -> bool:
        """Check if field exceeds coherence budget."""
        return self.field.coherence_cost > self.max_coherence

    def read_adaptive(self) -> dict:
        """
        Adaptive read - automatically selects appropriate temporal scale.
        Returns the highest-resolution view that fits coherence budget.
        """
        cost = self.field.coherence_cost

        # Find the scale that fits
        for scale, threshold in TEMPORAL_SCALES.items():
            view = self.field.extract_at_scale(scale)
            if estimate_coherence_cost(view) <= self.max_coherence:
                return {
                    "content": view,
                    "scale": scale,
                    "field_signature": self.field.signature,
                    "total_cost": cost,
                    "view_cost": estimate_coherence_cost(view),
                    "coherence_ratio": estimate_coherence_cost(view) / self.max_coherence
                }

        # Fallback to quantum (always fits)
        view = self.field.extract_at_scale("quantum")
        return {
            "content": view,
            "scale": "quantum",
            "field_signature": self.field.signature,
            "total_cost": cost,
            "view_cost": estimate_coherence_cost(view),
            "coherence_ratio": estimate_coherence_cost(view) / self.max_coherence
        }

    def read_at_scale(self, scale: str) -> dict:
        """Read at specific temporal scale."""
        view = self.field.extract_at_scale(scale)
        return {
            "content": view,
            "scale": scale,
            "field_signature": self.field.signature,
            "view_cost": estimate_coherence_cost(view)
        }

    def resonate_with(self, query: str) -> dict:
        """
        Attractor-based retrieval: find entries that resonate with query.
        Uses phase-distance to find harmonically aligned content.
        """
        query_sig = compute_resonance_signature(query)
        resonant = []

        if isinstance(self.field.data, list):
            for i, entry in enumerate(self.field.data):
                if isinstance(entry, dict):
                    # Check resonance with prompt
                    prompt = entry.get('prompt', '')
                    prompt_sig = compute_resonance_signature(prompt)
                    distance = phase_distance(query_sig, prompt_sig)

                    # Also check composition
                    comp = entry.get('composition', '')
                    comp_sig = compute_resonance_signature(comp[:500])
                    comp_distance = phase_distance(query_sig, comp_sig)

                    # Use minimum distance (strongest resonance)
                    min_distance = min(distance, comp_distance)

                    if min_distance < COHERENCE_THRESHOLD:
                        resonant.append({
                            "τ": i,
                            "resonance": 1 - min_distance,
                            "prompt": prompt,
                            "entry": entry
                        })

        # Sort by resonance (highest first)
        resonant.sort(key=lambda x: x["resonance"], reverse=True)

        return {
            "query": query,
            "query_signature": query_sig,
            "resonant_entries": resonant[:5],  # Top 5 by resonance
            "total_matches": len(resonant)
        }

    def temporal_stream(self) -> Generator[dict, None, None]:
        """
        Stream data as temporal oscillations.
        Each yield is one complete oscillation cycle.
        """
        if not isinstance(self.field.data, list):
            yield {"τ": 0, "oscillation": self.field.data}
            return

        for i, entry in enumerate(self.field.data):
            yield {
                "τ": i,
                "total_τ": len(self.field.data),
                "phase": i / len(self.field.data) * TAU,
                "oscillation": entry
            }


def harmonic_read(filepath: str, max_coherence: int = 20000,
                  mode: str = "adaptive", query: str = None) -> dict:
    """
    High-level harmonic read function.

    Modes:
    - "adaptive": Auto-select scale based on coherence budget
    - "quantum": Signatures and counts only
    - "cellular": Prompts as cellular view
    - "network": Prompts + previews
    - "ecosystem": Recent full + historical summary
    - "geological": Full data (may exceed budget)
    - "resonate": Find entries resonating with query

    Returns dict with content, scale used, and coherence metadata.
    """
    reader = HarmonicReader(filepath, max_coherence)

    if mode == "resonate" and query:
        return reader.resonate_with(query)
    elif mode == "adaptive":
        return reader.read_adaptive()
    elif mode in TEMPORAL_SCALES:
        return reader.read_at_scale(mode)
    else:
        return reader.read_adaptive()


# === CLI Interface ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 harmonic_read.py <filepath> [mode] [max_coherence] [query]")
        print()
        print("Modes: adaptive, quantum, cellular, network, ecosystem, geological, resonate")
        print()
        print("FHP Temporal Scales:")
        for scale, threshold in TEMPORAL_SCALES.items():
            print(f"  {scale:12} : {threshold:>8} coherence units")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "adaptive"
    max_coherence = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    query = sys.argv[4] if len(sys.argv) > 4 else None

    result = harmonic_read(filepath, max_coherence, mode, query)

    print(f">>> [harmonic_read] Scale: {result.get('scale', mode)}")
    print(f">>> [harmonic_read] Field Signature: {result.get('field_signature', 'N/A')}")
    if 'coherence_ratio' in result:
        print(f">>> [harmonic_read] Coherence: {result['coherence_ratio']:.2%} of budget")
    print()
    print(result.get('content', json.dumps(result, indent=2)))
