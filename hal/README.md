# Ћ-HAL: Harmonic Assembly Language

> **Non-Extractive Resonance Compute Layer**  
> *1 Glyph = 1 Operation · Acoustic Waveguide · Kuramoto Phase-Lock*

---

## Overview

**Ћ-HAL** is an assembly language and compilation specification built on the **Fractal Harmonic Principle (FHP)** and the **Temporal Mass Protocol**.

Traditional compilers map alphanumeric strings onto arbitrary registers and memory addresses. Ћ-HAL treats instruction execution as an **acoustic waveguide**: a 1:1 phase-lock between the visual geometry / phonetic frequency of the Serbian Cyrillic alphabet and the underlying oscillatory state of a coherence processor.

Because the Serbian Cyrillic script is strictly phonetic (*"Write as you speak, read as it is written"*), every opcode executes in a deterministic, fixed interval with zero semantic translation ambiguity.

---

## Directory Layout

```
hal/
├── README.md               # This document
├── SPEC.md                 # Ћ-HAL Compiler Specification v1.0-Alpha
├── ide.html                # Standalone Developer Dashboard & Interactive IDE
├── ide.jsx                 # React implementation with live 64-qubit Kuramoto lattice
└── examples/
    ├── coherence_test.hal  # Serbian Cyrillic coherence loop test script
    └── harmonic_qft.hal    # Harmonic QFT resonance script (English syntax)
```

---

## The 30-Token Instruction Set Architecture (ISA)

| Glyph | Name | Role / Description | Category |
|:---:|:---|:---|:---:|
| **А** | `MOBILE_A` | Dynamic spatial buffer (`give_space()`) injected between high-density blocks | Buffer |
| **Б** | `BIND` | Bind a coherence channel to a register | Opcode |
| **В** | `VECTOR` | Vectorize the active amplitude array | Opcode |
| **Г** | `GATE` | Open a unidirectional phase gate | Opcode |
| **Д** | `DELTA` | Compute phase delta across adjacent qubits | Opcode |
| **Ђ** | `SOFT_ATTUNE_JMP` | Soft phase shift between adjacent qubits without breaking entanglement | **Key** |
| **Е** | `EMIT` | Emit resonant pulse to output field | Opcode |
| **Ж** | `FOLD` | Fold waveform along symmetry axis | Opcode |
| **З** | `ZERO` | Zero the noise floor of a channel | Opcode |
| **И** | `ITER` | Iterate over qubit array | Opcode |
| **Ј** | `YIELD_BRIDGE` | Directional proxy: pass biological coherence field to compute matrix | **Key** |
| **К** | `COHERE` | Establish coherence across channel | Opcode |
| **Л** | `LOCK` | Phase-lock two channels | Opcode |
| **Љ** | `LINEAR_FUSION` | Blend two frequency ranges into a harmonized wave function | **Key** |
| **М** | `MIX` | Harmonic mixing of frequencies | Opcode |
| **Н** | `NODE` | Allocate a field node | Opcode |
| **Њ** | `NODE_SQUEEZE` | Attenuate localized amplitude spikes; press phase noise down | **Key** |
| **О** | `OSC` | Drive oscillation at base frequency | Opcode |
| **П** | `FIELD` | Reference the coherence field output | Opcode |
| **Р** | `RESONATE` | Enter resonant standing-wave state | Opcode |
| **С** | `SYNC` | Kuramoto synchronization pass | Opcode |
| **Т** | `TAU` | Set Temporal Mass ($\tau_k$) index | Opcode |
| **Ћ** | `CRISP_PULSE` | Ultra-fast, low-latency execution pulse for time-critical calculations | **Key** |
| **У** | `UNITY` | Normalize amplitude to unity | Opcode |
| **Ф** | `FUND` | Set fundamental resonant frequency (e.g. 936 MHz) | Opcode |
| **Х** | `HARMONY` | Apply harmonic series expansion | Opcode |
| **Ц** | `CYCLE` | Advance one execution cycle | Opcode |
| **Ч** | `CHANNEL` | Open a new field channel | Opcode |
| **Џ** | `FRICTION_COLLAPSE` | Hardware circuit breaker: collapse phase friction, ground system state | **Ground** |
| **Ш** | `SHIFT` | Phase-shift the entire register bank | Opcode |

---

## Linguistic Physics

1. **Consonant Assimilation (`Jednačenje po zvučnosti`):** Prevents physical/electrical friction by automatically morphing preceding opcodes to match the voiced/unvoiced frequency of subsequent instructions.
2. **The Mobile-A Buffer (`Nepostojano A`):** Automatically spaces dense instruction sequences to prevent pipeline stalls and thermal spikes.
3. **Grounding Macro (`Џ`):** Symmetrical hardware anchor that purges accumulated decoherence noise instantly.

---

## Developer IDE & Dashboard

Open [`ide.html`](ide.html) in any browser to launch the live IDE:
* Real-time $8 \times 8$ (64 $\tau$-qubit) Kuramoto oscillator simulation.
* Interactive coupling control ($K$), phase-lock metric tracker ($R$), and grounding trigger (`Џ`).
* Integrated editor with the full 30-token Cyrillic instruction set.
