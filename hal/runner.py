#!/usr/bin/env python3
"""
Ћ-HAL Coherence Test Runner & Kuramoto Simulator
=================================================
Executes Ћ-HAL assembly files (*.hal) by parsing directives and opcodes,
simulating the 64 τ-qubit Kuramoto oscillator lattice, executing
error-mitigation macros (Џ), and verifying phase-lock order parameter R.

Complies with Ћ-HAL Compiler Specification v1.0-Alpha.
"""

import math
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class HALEnvironment:
    tau_k: float = 1.0
    fundamental_hz: float = 936e6
    num_qubits: int = 64
    phases: np.ndarray = None
    omega: np.ndarray = None
    order_parameter_history: List[float] = None
    grounded: bool = False
    step_log: List[str] = None


class HALInterpreter:
    def __init__(self, filename: str):
        self.path = Path(filename)
        self.env = HALEnvironment(step_log=[], order_parameter_history=[])
        self.grid_dim = 8  # 8x8 = 64

    def parse_and_run(self) -> Dict[str, float]:
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        code = self.path.read_text(encoding="utf-8")
        lines = code.splitlines()

        print("=" * 68)
        print("  Ћ-HAL · COHERENCE TEST RUNNER & LATTICE EMULATOR")
        print(f"  Target Script: {self.path.name}")
        print("=" * 68)

        for line_idx, line in enumerate(lines, 1):
            raw = line.split(";", 1)[0].strip()
            if not raw:
                continue

            # Parse Directives
            if raw.startswith(".ТАУ_К") or raw.startswith(".tau_k"):
                val = float(raw.split()[1])
                self.env.tau_k = val
                self.env.step_log.append(f"Directive .ТАУ_К = {val:.2f}")

            elif raw.startswith(".ФУНДАМЕНТАЛ") or raw.startswith(".fundamental"):
                val = float(raw.split()[1].replace("е", "e"))
                self.env.fundamental_hz = val
                self.env.step_log.append(f"Directive .ФУНДАМЕНТАЛ = {val/1e6:.1f} MHz")

            elif ".ТАУ_КУБИТИ" in raw or ".tau_qubits" in raw:
                match = re.search(r"(\d+)", raw.split(":", 1)[1] if ":" in raw else raw)
                if match:
                    n = int(match.group(1))
                    self.env.num_qubits = n
                    self.grid_dim = int(math.isqrt(n))
                    self.env.step_log.append(f"Allocation: {n} τ-qubits ({self.grid_dim}x{self.grid_dim} lattice)")

            # Parse Opcodes / Steps
            elif "ИНИЦ_КОХЕРЕНЦИЈА" in raw or "INIT_COHERENCE" in raw:
                self._init_coherence()

            elif "ХАРМОНИЈА_МИКС" in raw or "HARMONIC_MIX" in raw:
                self._harmonic_mix()

            elif raw.strip().startswith("Џ") or "FRICTION_COLLAPSE" in raw:
                self._friction_collapse()

            elif "СИНХ_ФАЗА" in raw or "SYNC_PHASE" in raw:
                self._sync_phase()

        return self._evaluate_final_state()

    def _init_coherence(self):
        N = self.env.num_qubits
        np.random.seed(42)  # Deterministic seed for repeatable test verification
        # Initial disordered phase distribution
        self.env.phases = np.random.uniform(0, 2 * np.pi, N)
        # Natural intrinsic frequencies around fundamental
        self.env.omega = 0.6 + np.random.uniform(0, 0.9, N)
        r0 = self._calc_order_parameter()
        self.env.order_parameter_history.append(r0)
        self.env.step_log.append(f"ИНИЦ_КОХЕРЕНЦИЈА: {N} channels initialized (Initial R = {r0:.4f})")

    def _harmonic_mix(self):
        N = self.env.num_qubits
        # Apply harmonic modulation based on golden ratio and fundamental
        phi_ratio = (1 + math.sqrt(5)) / 2
        harmonic_multipliers = np.array([phi_ratio ** ((i % 5) - 2) for i in range(N)])
        self.env.omega = self.env.omega * harmonic_multipliers
        r = self._calc_order_parameter()
        self.env.order_parameter_history.append(r)
        self.env.step_log.append(f"ХАРМОНИЈА_МИКС: Golden-ratio harmonic expansion applied (R = {r:.4f})")

    def _friction_collapse(self):
        # Џ - Macro: Grounding and friction collapse
        self.env.grounded = True
        dt = 0.05
        # Pull phases strongly toward zero-phase symmetry plane
        dtheta = 1.8 * np.sin(0.0 - self.env.phases)
        self.env.phases = (self.env.phases + dtheta * dt * 2.0) % (2 * np.pi)
        r = self._calc_order_parameter()
        self.env.order_parameter_history.append(r)
        self.env.step_log.append(f"Џ (FRICTION_COLLAPSE): Grounded noise floor. Phase friction cleared (R = {r:.4f})")

    def _sync_phase(self, steps: int = 40):
        total = self.env.num_qubits
        N = self.grid_dim
        is_2d = (N * N == total)
        K = 2.5  # Max coupling
        dt = 0.05
        phases = self.env.phases.copy()

        for step in range(steps):
            new_phases = phases.copy()
            if is_2d:
                grid = phases.reshape((N, N))
                for r in range(N):
                    for c in range(N):
                        sum_diff = 0.0
                        cnt = 0
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < N and 0 <= nc < N:
                                sum_diff += math.sin(grid[nr, nc] - grid[r, c])
                                cnt += 1
                        idx = r * N + c
                        dtheta = self.env.omega[idx] + (K / cnt) * sum_diff
                        if self.env.grounded:
                            dtheta += 1.8 * math.sin(0.0 - grid[r, c])
                        new_phases[idx] += dtheta * dt
            else:
                # 1D Ring Topology
                for i in range(total):
                    left = (i - 1) % total
                    right = (i + 1) % total
                    sum_diff = math.sin(phases[left] - phases[i]) + math.sin(phases[right] - phases[i])
                    dtheta = self.env.omega[i] + (K / 2.0) * sum_diff
                    if self.env.grounded:
                        dtheta += 1.8 * math.sin(0.0 - phases[i])
                    new_phases[i] += dtheta * dt

            phases = new_phases % (2 * np.pi)
            self.env.phases = phases.copy()
            r_val = self._calc_order_parameter()
            self.env.order_parameter_history.append(r_val)

        topology = f"{N}x{N} 2D lattice" if is_2d else f"{total}-qubit 1D ring"
        self.env.step_log.append(f"СИНХ_ФАЗА: Kuramoto synchronization completed on {topology} ({steps} iters, R = {r_val:.4f})")

    def _calc_order_parameter(self) -> float:
        phases = self.env.phases
        sx = np.sum(np.cos(phases))
        sy = np.sum(np.sin(phases))
        return float(np.sqrt(sx * sx + sy * sy) / len(phases))

    def _evaluate_final_state(self) -> Dict[str, float]:
        final_r = self._calc_order_parameter()
        tau_effective = self.env.tau_k * final_r

        print("\n--- EXECUTION TRACE ---")
        for log in self.env.step_log:
            print(f"  [✓] {log}")

        print("\n--- COHERENCE PHASE DISTRIBUTION ---")
        bins = 16
        hist, _ = np.histogram(self.env.phases, bins=bins, range=(0, 2 * np.pi))
        max_h = max(hist) if max(hist) > 0 else 1
        for b_idx in range(bins):
            bar_len = int((hist[b_idx] / max_h) * 25)
            bar = "█" * bar_len + "░" * (25 - bar_len)
            rad_start = b_idx * (2 * math.pi / bins)
            print(f"  bin {b_idx:02d} [{rad_start:4.2f} rad]: [{bar}] {hist[b_idx]:2d} qubits")

        regime = (
            "SOVEREIGN (Levitation)" if final_r >= 0.95
            else "KAIROTIC (Phase-Locked)" if final_r >= 0.80
            else "EMERGENT" if final_r >= 0.50
            else "DISPERSIVE"
        )

        print("\n--- COHERENCE TEST METRICS ---")
        print(f"  Final Order Parameter (R) : {final_r:.5f}  ({final_r*100:.1f}% synchronized)")
        print(f"  Baseline Temporal Mass (τₖ): {self.env.tau_k:.2f}")
        print(f"  Effective τₖ (τₖ · R)       : {tau_effective:.2f}")
        print(f"  Resonant Fundamental      : {self.env.fundamental_hz/1e6:.1f} MHz")
        print(f"  Lattice Dimensions        : {self.grid_dim}x{self.grid_dim} ({self.env.num_qubits} qubits)")
        print(f"  Operating Regime          : 🜏 {regime} 🜏")
        print("=" * 68)

        if final_r >= 0.90:
            print("  >>> STATUS: PASSED (System Phase-Lock Achieved) <<<")
        else:
            print("  >>> STATUS: DECOHERENT <<<")
        print("=" * 68)

        return {
            "order_parameter_R": final_r,
            "tau_k": self.env.tau_k,
            "tau_effective": tau_effective,
            "passed": final_r >= 0.90,
        }


def main():
    test_file = Path(__file__).parent / "examples" / "coherence_test.hal"
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])

    interpreter = HALInterpreter(str(test_file))
    results = interpreter.parse_and_run()
    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
