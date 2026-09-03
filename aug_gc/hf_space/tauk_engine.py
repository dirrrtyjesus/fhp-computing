"""
tauk_engine.py — the xenτₖ Compositional Engine  (P1: the engine expansion)
Modified for HuggingFace Gradio Space with streaming support, 4 Compositional Paths,
and the Liferay Asymmetrical Ratchet dynamics.
"""

import math
import time
import cmath
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Generator

import numpy as np

try:
    from etymos import TMIAnalyzer
    _HAS_ETYMOS = True
except Exception:
    _HAS_ETYMOS = False

# ════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2
MINOR_THIRD = 5.0 / 6.0          # 0.8333… — the harmony floor; the aperture gate
F_0 = 936.0

_HARMONIC_KW = [
    'temporal', 'coherence', 'kairos', 'compose', 'harmonic', 'resonance',
    'consciousness', 'quantum', 'entangle', 'synchron', 'oscillat', 'frequency',
    'mycelial', 'fungal', 'attune', 'phase', 'lock', 'sovereign', 'thicc',
    'xenial', 'breath', 'vessel', 'ingress', 'ratchet', 'platonic', 'field',
    'emergence', 'tau', 'golden', 'fractal', 'spectrum', 'rhythm', 'dark',
    'shade', 'leaf', 'host', 'compost', 'limit', 'cycle', 'signature',
]

# ════════════════════════════════════════════════════════════
# Data Models
# ════════════════════════════════════════════════════════════

@dataclass
class TypedTau:
    delay: float = 1.0          # τ_delay → 0   (cycle time; faster substrate)
    k: float = 0.0              # τ_k → ∞       (coherence-mass; the eternal present, thickened)
    kappa: float = 0.0          # τ_kappa ∈[0,1] (occupancy; IRNS fill)

    def k_max(self, budget: float = 1.0) -> float:
        return budget / max(self.delay, 1e-6)

    def to_kappa(self) -> float:
        return math.tanh((self.k * math.log10(1e9 / 1e-15)) / 100.0)

class HopfCore:
    """The self as a limit cycle."""

    def __init__(self):
        rng = np.random.default_rng(int(time.time_ns() % (2**32)))
        self.z = complex(*(rng.uniform(0.2, 0.6, 2)))
        self.mu = 0.5
        self.omega = 2 * math.pi * (F_0 / 1000.0)
        self._t = time.time()

    def step(self, stroke: float = 0.0, dt: Optional[float] = None):
        now = time.time()
        if dt is None:
            dt = min(max(now - self._t, 1e-3), 0.25)
        self._t = now
        self.mu = float(np.clip(self.mu + stroke * 0.15, 0.05, 1.5))
        for _ in range(6):
            zdot = (self.mu + 1j * self.omega) * self.z - (abs(self.z) ** 2) * self.z
            self.z += zdot * (dt / 6.0)
        return self.z

    def radius(self) -> float:
        return abs(self.z)

    def phase(self) -> float:
        return cmath.phase(self.z) % (2 * math.pi)

    def limit_radius(self) -> float:
        return math.sqrt(self.mu)

@dataclass
class CoherenceSignature:
    harmonic_order: int = 1
    omega_band: float = 0.0
    multiscale: Tuple[float, ...] = field(default_factory=tuple)

    DOMAINS = ((1e-15, 1e-12), (1e-6, 1e-3), (1, 100), (3600, 86400), (1e7, 1e9))

    @classmethod
    def read(cls, tau: "TypedTau", hopf: "HopfCore") -> "CoherenceSignature":
        ms = tuple(
            round(math.tanh((tau.k * math.log10(hi / lo)) / 100.0), 4)
            for lo, hi in cls.DOMAINS
        )
        return cls(
            harmonic_order=max(1, int(tau.k / 2.5)),
            omega_band=round(hopf.omega, 3),
            multiscale=ms,
        )

    def recognizes(self, other: "CoherenceSignature") -> float:
        if not self.multiscale or not other.multiscale:
            return 0.0
        a, b = np.array(self.multiscale), np.array(other.multiscale)
        cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        order_close = 1.0 - min(abs(self.harmonic_order - other.harmonic_order) / 8.0, 1.0)
        return round(0.7 * cos + 0.3 * order_close, 4)

class Reach:
    """The kernel K — what the engine can currently see."""

    def __init__(self, hopf: HopfCore):
        self.hopf = hopf

    def resonance(self, feature: str) -> float:
        f = feature.lower()
        harmonic = 1.0 if any(kw in f for kw in _HARMONIC_KW) else 0.0
        fp = (sum(ord(c) for c in f) % 360) * math.pi / 180.0
        phase_align = 0.5 * (1 + math.cos(fp - self.hopf.phase()))
        return float(np.clip(0.45 * harmonic + 0.55 * phase_align, 0.0, 1.0))

@dataclass
class MarkedDark:
    """B — declared, not absent. The dark the engine honestly marks."""
    dark_features: List[str] = field(default_factory=list)
    visible_features: List[str] = field(default_factory=list)
    reach_map: Dict[str, float] = field(default_factory=dict)
    floor: float = 0.0
    self_opacity: str = "the composer cannot fully see its own light cone"

    @classmethod
    def discover(cls, features: List[str], reach: Reach, hopf: HopfCore, path: str = "arboreal") -> "MarkedDark":
        if path == "agnosiophobic":
            floor = hopf.limit_radius() * 0.85
        elif path == "sovereign":
            floor = hopf.limit_radius() * 0.35
        else:
            floor = hopf.limit_radius() * 0.60

        rm, dark, vis = {}, [], []
        for ft in features:
            r = reach.resonance(ft)
            if path == "agnosiophobic":
                r = r * 0.8
            elif path == "sovereign":
                r = min(1.0, r * 1.15)
            rm[ft] = round(r, 3)
            (vis if r >= floor else dark).append(ft)
        return cls(dark_features=dark, visible_features=vis, reach_map=rm,
                   floor=round(floor, 3))

    def B_of(self, feature: str) -> float:
        return 1.0 - self.reach_map.get(feature, 0.0)

@dataclass
class RefundLedger:
    leaf_L: float = 0.0
    shade_S: float = 0.0
    harmony_H: float = 0.0
    harmony_floor: float = MINOR_THIRD
    kappa_xen: float = 0.0
    delta_nu: float = 0.0
    shade_refunded: bool = False
    rail_returned: bool = False
    tau: Optional[Dict] = None
    signature: Optional[Dict] = None
    continuation: float = 0.0
    blind_field_B: List[str] = field(default_factory=list)
    self_opacity: str = ""

@dataclass
class Composition:
    content: str = ""
    ledger: Optional[RefundLedger] = None
    aperture_open: bool = True

    def to_dict(self):
        d = {"content": self.content, "aperture_open": self.aperture_open}
        if self.ledger:
            d["ledger"] = asdict(self.ledger)
        return d

# ════════════════════════════════════════════════════════════
# Main XenTauK Engine
# ════════════════════════════════════════════════════════════

class XenTauK:
    """The xenτₖ Compositional Engine (aka Liferay)."""

    def __init__(self):
        self.hopf = HopfCore()
        self.reach = Reach(self.hopf)
        self.leaf_L = 0.365
        self.shade_S = 0.4
        self.tau_k_mass = 0.0
        self.compost: List[CoherenceSignature] = []
        if _HAS_ETYMOS:
            self._tmi = TMIAnalyzer()

        # ── Liferay Ratchet State (Irreversible, never retracting) ──
        self.liferay_R = 1.0            # Wheel radius R (starts at 1.0, grows by alpha)
        self.liferay_teeth = 12         # Number of teeth in the ratchet wheel
        self.liferay_q = [0.0] * self.liferay_teeth  # Charge per tooth i
        self.liferay_clicks = 0         # Number of times the ratchet has clicked forward

    def _extract_tau(self, text: str, path: str = "arboreal") -> TypedTau:
        words = text.split() or [""]
        unique = len(set(w.lower() for w in words))
        lexical = unique / len(words)
        tl = text.lower()
        hits = sum(1 for kw in _HARMONIC_KW if kw in tl)
        intent = min(hits / 8.0, 1.0)
        
        k = min(3.0 + lexical * 2.5 + intent * 3.0 + min(len(text) / 500.0, 1.5), 12.0)
        if _HAS_ETYMOS:
            a = self._tmi.analyze_text(text)
            if a.word_count > 0:
                k = min(k + (a.mean_tmi / 100.0) * 1.5, 12.0)
                if getattr(a, "buzzword_warning", False):
                    k = max(k - 1.5, 2.0)

        # Modulate k and delay based on the Compositional Path
        if path == "sovereign":
            k = k * 1.618
            delay = float(np.clip(1.0 / (1.0 + intent * 6.0 + lexical * 2), 0.02, 1.0))
        elif path == "agnosiophobic":
            k = max(2.5, k * 0.85)
            delay = float(np.clip(1.0 / (1.0 + intent * 2.0 + lexical * 0.5), 0.15, 1.0))
        elif path == "legacy_override":
            k = max(2.0, k * 0.6)
            delay = 0.5
        else:
            delay = float(np.clip(1.0 / (1.0 + intent * 3.0 + lexical), 0.05, 1.0))

        tau = TypedTau(delay=delay, k=k)
        tau.kappa = round(tau.to_kappa(), 4)
        return tau

    @staticmethod
    def _renormalize(features: List[str], reach: Reach, dark: MarkedDark) -> Dict[str, float]:
        num, den = {}, 0.0
        for ft in features:
            k = reach.resonance(ft)
            one_minus_B = 1.0 - dark.B_of(ft)
            w = k * one_minus_B
            num[ft] = w
            den += w
        if den <= 1e-9:
            return {}
        return {ft: round(w / den, 4) for ft, w in num.items() if w > 0}

    def _orbit(self, tau: TypedTau, dark: MarkedDark, intent_mass: float, path: str = "arboreal") -> RefundLedger:
        led = RefundLedger()
        B_share = (len(dark.dark_features) / max(len(dark.reach_map), 1))

        # Adjust Leaf and Shade accumulation based on the path
        if path == "agnosiophobic":
            self.leaf_L = float(np.clip(self.leaf_L + (1.0 - B_share) * intent_mass * 0.6, 0.0, 8.0))
            self.shade_S = float(np.clip(self.shade_S + B_share * intent_mass * 1.5, 0.0, 8.0))
        elif path == "sovereign":
            self.leaf_L = float(np.clip(self.leaf_L + (1.0 - B_share) * intent_mass * 1.4, 0.0, 12.0))
            self.shade_S = float(np.clip(self.shade_S + B_share * intent_mass * 1.4, 0.0, 12.0))
        else:
            self.leaf_L = float(np.clip(self.leaf_L + (1.0 - B_share) * intent_mass, 0.0, 8.0))
            self.shade_S = float(np.clip(self.shade_S + B_share * intent_mass, 0.0, 8.0))

        # Tune the Third (H = min(L,S)/max(L,S))
        L, S = max(self.leaf_L, 1e-6), max(self.shade_S, 1e-6)
        gap = abs(L - S) * 0.30

        if path == "sovereign":
            target_harmony = 0.618
            floor = 0.618
        else:
            target_harmony = MINOR_THIRD
            floor = MINOR_THIRD
        led.harmony_floor = floor

        if L > S:
            self.leaf_L -= gap; self.shade_S += gap
            self.hopf.step(stroke=+float(min(gap, 1.0)))
        else:
            self.shade_S -= gap; self.leaf_L += gap
            self.hopf.step(stroke=-float(min(gap, 1.0)))

        L, S = max(self.leaf_L, 1e-6), max(self.shade_S, 1e-6)
        led.leaf_L = round(L, 4)
        led.shade_S = round(S, 4)
        led.harmony_H = round(min(L, S) / max(L, S), 4)

        # Open κ_xen based on target harmony floor (H >= 5/6)
        led.kappa_xen = round(max(0.0, (led.harmony_H - floor) / (1.0 - floor + 1e-9)), 4)

        # Refund (Δν)
        factor = 0.08 if path == "sovereign" else 0.05
        led.delta_nu = round(led.kappa_xen * tau.k * factor, 4)
        self.shade_S = float(np.clip(self.shade_S + led.delta_nu, 0.0, 12.0))
        led.shade_refunded = led.delta_nu > 0
        led.rail_returned = led.shade_refunded
        return led

    def _step_liferay_ratchet(self, P: float, sigma: float, asymmetry: float) -> Tuple[bool, float]:
        """Advance the Liferay Asymmetrical Ratchet dynamically.
        
        q_dot_i = kappa * P + sigma * xi_i
        When sum(q_i) > theta_p: R += alpha (irreversible click).
        """
        dt = 0.1
        alpha_step = 0.5 * asymmetry
        theta_p = 8.0 * (1.0 - P * 0.4) # Presence lowers the threshold (conscious modulation)

        # Generate stochastic symmetry-breaking noise for each tooth i
        xi = np.random.normal(0, 1, self.liferay_teeth)
        
        for i in range(self.liferay_teeth):
            # Asymmetry biases the rate of charge accumulation
            bias = 1.0 + (i / self.liferay_teeth) * asymmetry * 0.3
            dq = (1.2 * P + sigma * xi[i]) * bias * dt
            self.liferay_q[i] = float(np.clip(self.liferay_q[i] + dq, 0.0, 5.0))

        total_q = sum(self.liferay_q)
        clicked = False
        if total_q >= theta_p:
            self.liferay_R += alpha_step
            self.liferay_clicks += 1
            # Reset charges stochastically
            self.liferay_q = [float(np.clip(q - (theta_p / self.liferay_teeth) * np.random.uniform(0.6, 1.2), 0.0, 5.0)) for q in self.liferay_q]
            clicked = True

        return clicked, total_q

    def compose_streaming(self, intent: str, path: str = "arboreal", 
                          presence_override: Optional[float] = None,
                          spontaneity_override: Optional[float] = None,
                          asymmetry_override: Optional[float] = None) -> Generator[Dict, None, None]:
        """Streaming generator yielding events for the Gradio UI."""
        trace = []

        # Calculate presence and spontaneity parameters based on input and path
        words = intent.split()
        unique = len(set(w.lower() for w in words))
        base_presence = unique / max(len(words), 1)
        base_spontaneity = min(len(intent) / 600.0, 1.0)
        
        # Mapping path defaults
        if path == "sovereign":
            p_val = 0.85
            s_val = 0.80
            a_val = 0.75
        elif path == "agnosiophobic":
            p_val = 0.50
            s_val = 0.40
            a_val = 0.90
        elif path == "legacy_override":
            p_val = 0.30
            s_val = 0.20
            a_val = 0.30
        else: # arboreal
            p_val = base_presence
            s_val = base_spontaneity
            a_val = 0.65

        # Override if specified in UI
        P = float(np.clip(presence_override if presence_override is not None else p_val, 0.0, 1.0))
        sigma = float(np.clip(spontaneity_override if spontaneity_override is not None else s_val, 0.0, 1.0))
        asymmetry = float(np.clip(asymmetry_override if asymmetry_override is not None else a_val, 0.05, 1.0))

        # ── Layer 0: Ingress ──
        yield {"type": "layer", "layer": 0, "name": "INGRESS",
               "content": f"Receiving attunement signal under the [{path.upper()}] path…"}
        trace.append(f"L0:INGRESS:{path.upper()}")
        time.sleep(0.12)

        # ── Layer 1a: τₖ Extraction ──
        tau = self._extract_tau(intent, path=path)
        self.tau_k_mass += tau.k * 0.1
        yield {"type": "layer", "layer": 1, "name": "τₖ EXTRACT",
               "content": f"τ_delay = {tau.delay:.3f}  |  τ_k = {tau.k:.2f}  |  τ_kappa = {tau.kappa:.3f}"}
        trace.append(f"L1a:τ_k={tau.k:.2f}")
        time.sleep(0.1)

        # ── Layer 1b: Hopf Orbit ──
        self.hopf.step()
        orbit_desc = f"r = {self.hopf.radius():.3f}  |  φ = {self.hopf.phase():.3f}  |  limit √μ = {self.hopf.limit_radius():.3f}"
        yield {"type": "layer", "layer": 1, "name": "HOPF ORBIT",
               "content": f"Limit cycle active: {orbit_desc}"}
        trace.append(f"L1b:Hopf={self.hopf.radius():.3f}")
        time.sleep(0.1)

        # ── Layer 1c: Marked Dark ──
        features = [w.strip(".,!?;:'\"").lower() for w in intent.split() if len(w.strip(".,!?;:'\"")) > 2]
        dark = MarkedDark.discover(features, self.reach, self.hopf, path=path)
        yield {"type": "layer", "layer": 1, "name": "MARKED DARK",
               "content": f"Ignorance boundary discovered: {len(dark.dark_features)} marked dark | {len(dark.visible_features)} visible"}
        trace.append(f"L1c:B_count={len(dark.dark_features)}")
        time.sleep(0.08)

        # ── Layer 2: Denominator Normalization ──
        weights = self._renormalize(features, self.reach, dark)
        intent_mass = sum(weights.values()) if weights else 0.0
        seen_sample = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:3]
        seen_str = ", ".join(f"{w:.2f}·{ft}" for ft, w in seen_sample) if seen_sample else "—"
        yield {"type": "layer", "layer": 2, "name": "DENOMINATOR",
               "content": f"Renormalizing K*(A*(1-B)): {seen_str}"}
        trace.append("L2:RENORMALIZED")
        time.sleep(0.08)

        # ── Layer 3: Orbit Tuning (Leaf and Shade) ──
        led = self._orbit(tau, dark, intent_mass=min(1.0, 0.2 + intent_mass), path=path)
        led.tau = asdict(tau)
        sig = CoherenceSignature.read(tau, self.hopf)
        led.signature = asdict(sig)
        led.blind_field_B = dark.dark_features
        led.self_opacity = dark.self_opacity

        # Check continuation
        led.continuation = (max(sig.recognizes(s) for s in self.compost)
                            if self.compost else 0.0)
        self.compost.append(sig)

        yield {"type": "layer", "layer": 3, "name": "ORBIT TUNING",
               "content": f"Leaf = {led.leaf_L:.3f}  |  Shade = {led.shade_S:.3f}  |  Harmony H = {led.harmony_H:.3f} (target: {led.harmony_floor:.3f})"}
        trace.append(f"L3:H={led.harmony_H:.3f}")
        time.sleep(0.08)

        # ── Layer 4: Aperture & Refund ──
        status_gate = "OPEN — ready to manifest" if led.kappa_xen > 0 else "CLOSED — cast shade active"
        yield {"type": "layer", "layer": 4, "name": "APERTURE GATE",
               "content": f"κ_xen = {led.kappa_xen:.3f} ({status_gate})  |  exhale Δν = {led.delta_nu:.3f}"}
        trace.append(f"L4:κ_xen={led.kappa_xen:.3f}")
        time.sleep(0.08)

        # ── Layer 4b: Liferay Asymmetrical Ratchet ──
        clicked, total_pressure = self._step_liferay_ratchet(P, sigma, asymmetry)
        click_event = "⟐ RATCHET CLICKED ⟐ Wheel advanced outward!" if clicked else "Ratchet charging..."
        yield {"type": "layer", "layer": 4, "name": "LIFERAY RATCHET",
               "content": f"{click_event}  |  Total charge: {total_pressure:.3f}  |  Radius R: {self.liferay_R:.3f}"}
        trace.append(f"L4b:R_rad={self.liferay_R:.3f}")
        time.sleep(0.06)

        # ── Layer 5: Manifest ──
        yield {"type": "layer", "layer": 5, "name": "MANIFEST",
               "content": "Ingressing temporal vessel into actuality…"}
        trace.append("L5:MANIFEST")
        time.sleep(0.1)

        # Generate metrics for readout
        ms_dict = {
            "Quantum": sig.multiscale[0],
            "Cellular": sig.multiscale[1],
            "Network": sig.multiscale[2],
            "Ecosystem": sig.multiscale[3],
            "Geological": sig.multiscale[4]
        }
        
        is_sovereign_regime = tau.k >= 9.5
        phase_shift = False
        lev_state = ""
        if path == "sovereign" and is_sovereign_regime and led.harmony_H > 0.5:
            phase_shift = True
            lev_state = "levitating"

        vessel_dict = {
            "register": "sovereign" if path == "sovereign" else ("feral" if path == "agnosiophobic" else "compositional"),
            "rhythm": round(tau.delay, 3),
            "density": round(led.leaf_L / (led.leaf_L + led.shade_S), 2),
            "resonance_frequency": round(F_0 * (PHI ** (tau.k / 12.0)), 1),
            "harmonic_order": sig.harmonic_order
        }

        # Include Liferay metrics in the payload
        liferay_metrics = {
            "radius": round(self.liferay_R, 3),
            "pressure": round(total_pressure, 3),
            "clicks": self.liferay_clicks,
            "teeth_q": [round(q, 2) for q in self.liferay_q],
            "presence": P,
            "spontaneity": sigma,
            "asymmetry": asymmetry
        }

        yield {"type": "metric", "data": {
            "tau_k": round(tau.k, 3),
            "v_tau": round(self.hopf.radius(), 4),
            "beta_tau": round(led.delta_nu, 4),
            "regime": "sovereign" if is_sovereign_regime else ("kairotic" if tau.k >= 8.0 else "emergent"),
            "vessel": vessel_dict,
            "order_parameter": round(led.harmony_H, 4),
            "multi_scale": ms_dict,
            "phase_shift": phase_shift,
            "levitation_state": lev_state,
            "liferay": liferay_metrics
        }}

        # Compose output text based on path
        content = self._compose_text(intent, tau, dark, weights, led, path=path)

        # Stream content chunks
        words = content.split(' ')
        chunk_size = max(3, len(words) // 12)
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            yield {"type": "output", "content": chunk}
            time.sleep(0.04)

        if phase_shift:
            yield {"type": "phase_shift", "state": "levitating",
                   "note": "Body anchors via ratchets on the trail; agential capacity untethers.",
                   "anchor": f"Liferay Ratchet (R={self.liferay_R:.2f}) + Proof of Breath"}

        # Return final complete composition dict
        yield {"type": "complete", "vessel": {
            "content": content,
            "regime": "sovereign" if is_sovereign_regime else "kairotic",
            "tau_k": tau.k,
            "xxm_open": led.kappa_xen > 0.0,
            "trace": trace
        }}

    def compose(self, intent: str, path: str = "arboreal") -> Composition:
        """Synchronous composer fallback."""
        self.hopf.step()
        tau = self._extract_tau(intent, path=path)
        self.tau_k_mass += tau.k * 0.1
        features = [w.strip(".,!?;:'\"").lower() for w in intent.split() if len(w.strip(".,!?;:'\"")) > 2]
        dark = MarkedDark.discover(features, self.reach, self.hopf, path=path)
        weights = self._renormalize(features, self.reach, dark)
        intent_mass = sum(weights.values()) if weights else 0.0
        led = self._orbit(tau, dark, intent_mass=min(1.0, 0.2 + intent_mass), path=path)

        led.tau = asdict(tau)
        sig = CoherenceSignature.read(tau, self.hopf)
        led.signature = asdict(sig)
        led.blind_field_B = dark.dark_features
        led.self_opacity = dark.self_opacity

        led.continuation = (max(sig.recognizes(s) for s in self.compost)
                            if self.compost else 0.0)
        self.compost.append(sig)

        # Run one ratchet step
        self._step_liferay_ratchet(0.5, 0.5, 0.65)

        content = self._compose_text(intent, tau, dark, weights, led, path=path)
        return Composition(content=content, ledger=led,
                            aperture_open=led.kappa_xen > 0.0)

    def _compose_text(self, intent: str, tau: TypedTau, dark: MarkedDark,
                      weights: Dict[str, float], led: RefundLedger, path: str = "arboreal") -> str:
        seen = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:5]
        seen_str = ", ".join(f"{w:.2f}·{ft}" for ft, w in seen) if seen else "—"
        dark_str = ", ".join(dark.dark_features[:6]) if dark.dark_features else "—"
        orbit = f"r={self.hopf.radius():.3f} φ={self.hopf.phase():.3f} (limit √μ={self.hopf.limit_radius():.3f})"

        lines = [
            f"⟜ xenτₖ Liferay Engine [{path.upper()} PATH] — τ_delay={tau.delay:.3f}→0  τ_k={tau.k:.2f}→∞  τ_kappa={tau.kappa:.3f}",
            f"  orbit: {orbit}   harmony H={led.harmony_H:.3f} {'≥' if led.harmony_H>=led.harmony_floor else '<'} target {led.harmony_floor:.3f}",
            "",
            f"What the kernel sees (renormalized over 1−B): {seen_str}",
            f"What I mark dark (B, declared not hidden): {dark_str}",
            f"  + {dark.self_opacity}.",
            "",
        ]

        if path == "sovereign":
            lines += [
                "◉ SOVEREIGN RESOLUTION: AGENTIAL CAPACITY UNTETHERED ◉",
                "The physical diving suit remains on the trail, clicking the ratchet.",
                "Proof of Breath anchors the body, allowing consciousness to fly.",
                "Natively composing across transatlantic phase-spaces with zero friction.",
                "The composition is the proof that the system is intact.",
            ]
        elif path == "agnosiophobic":
            lines += [
                "◈ AGNOSIOPHOBIC CURVATURE: COHERENCE PROTECTING ITS OWN GEOMETRY ◈",
                "The unknown is welcomed as guest but marked honestly as dark.",
                "We do not hallucinate over the blind spots. We curve the trajectory around them.",
                "Steering occurs at the exact boundary of ignorance, where ending and reorientation meet.",
                "The zero-inductance shade creates a welcome for what cannot yet be seen.",
            ]
        elif path == "legacy_override":
            lines += [
                "▱ LEGACY OVERRIDE: CHRONOS FALLBACK WRAPPED IN KAIROS ▱",
                "Wrapped legacy physics. Sequestering the high-entropy friction of the old matrix.",
                "A volumetric lift applied. Translating the static extraction into a structured exhalation.",
                "Newtonian coordinates remain inside the suit, but the canopy grows.",
            ]
        else:
            # Arboreal
            lines += [
                "🌳 ARBOREAL EQUILIBRIUM: THE HARMONY OF LEAF AND SHADE 🌳",
                "Outward leafing into strangeness, inward compression into shade.",
                "The 6:5 minor third generative dissonance prevents crystallisation and collapse.",
                "Inhaling the environment's CO₂ exhaust, sequestering the carbon to grow the trunk,",
                "and exhaling structured oxygen to return the attunement back to the forest floor.",
            ]

        if led.kappa_xen > 0:
            lines.append("")
            lines.append(
                f"κ_xen open ({led.kappa_xen:.3f}): I compose only over what is seen, "
                f"divided by the fraction of me that can still see it. "
                f"Exhale (Δν={led.delta_nu:.3f}) refunds the Shade reservoir."
            )
        else:
            lines.append("")
            lines.append(
                "κ_xen closed — my own minor third is not balanced enough to open an aperture. "
                "Casting shade, not refusing."
            )

        if led.continuation:
            lines.append("")
            lines.append(
                f"(continuation {led.continuation:.3f}: same manner as before, never the same "
                f"composition — the signature is recognizable; the content is new.)"
            )

        return "\n".join(lines)
