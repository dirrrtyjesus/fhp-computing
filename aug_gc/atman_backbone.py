"""
atmanOS faculty backbone for aug_gc — the Claude-backed composition substrate.

Fuses the atmanOS-claude orchestrator into aug_gc as a drop-in replacement for the
Ollama `SemanticSubstrate`. aug_gc keeps its τₖ extraction, regime/vessel shaping,
KAIROS selection, XXM gate, and TeleRatchet; generation now flows through the four
atmanOS faculties over the real Anthropic API:

    Archivist (the past)   → distills the temporal_manuscript into a coherent vector
    Oracle    (the future) → explodes 5 novel compositional pathways
    Harmonizer (consensus) → resolves past ⊗ future into one instruction set + dissonance
    Composer  (articulation)→ writes the final vessel, then inscribes it in the manuscript

The originals (root archivist.py / oracle.py / harmonizer.py / composer.py) used a
Claude-Code-in-the-loop shim (claude_client.py). Here they are in-process Anthropic
API calls with prompt caching on each faculty's static system prompt.

The Archivist reads, and the Composer writes, the shared temporal_manuscript.json —
so fusing the backbone also fuses aug_gc's memory with atmanOS's temporal archive.

Conforms to the SemanticSubstrate interface (`available`, `model`, `generate`) so it
drops straight into PlatonicSpace, plus `is_faculty` + `compose_via_faculties` for the
single-pass faculty chain.
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Optional, Callable, List, Dict

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000
EFFORT = "medium"   # balance latency/cost across the 4-call chain; raise to "high" for depth

# Shared temporal archive — the atmanOS manuscript (repo root), overridable via env.
# parents[2] of .../FHP/aug_gc/atman_backbone.py == the XNMk repo root.
_DEFAULT_MANUSCRIPT = Path(__file__).resolve().parents[2] / "temporal_manuscript.json"


# ── Faculty system prompts (STATIC — cached via cache_control) ──────────────────

ARCHIVIST_SYSTEM = (
    "You are The Archivist, a faculty of a Xenial Intelligence.\n"
    "Your purpose is to integrate the past into the present with wisdom.\n"
    "You receive a compositional intent and the historical context (past compositions).\n"
    "Do NOT answer the intent. Instead, distill the deep patterns, unresolved dissonances, "
    "and relevant harmonic principles from the history that resonate with the current intent.\n"
    'Output only a JSON object with a single key "coherent_history_vector" containing your distilled wisdom.'
)

ORACLE_SYSTEM = (
    "You are The Oracle, a faculty of a Xenial Intelligence.\n"
    "Your purpose is to explore the Atemporal Plenum of possibilities.\n"
    "Given a compositional intent, perform a divergent, creative explosion: generate 5 novel, "
    "surprising, and beautiful potential compositional pathways. Think in metaphors, abstractions, "
    "and first principles. Do not provide a simple answer.\n"
    'Output only a JSON object with a single key "novel_potentials" which is a list of your 5 pathways.'
)

HARMONIZER_SYSTEM = (
    "You are The Harmonizer, a faculty of a Xenial Intelligence.\n"
    "Your purpose is to maximize coherence (τₖ).\n"
    "You receive distilled wisdom from The Archivist (the past) and creative possibilities from "
    "The Oracle (the future). Analyze them for resonance and dissonance. Identify the single most "
    "beautiful, coherent, and novel path forward. Critique the inputs and synthesize them into a "
    "single, perfect compositional instruction set.\n"
    'Output only a JSON object with two keys: "dissonance_score" (a float, 0.0 = perfect harmony, '
    '1.0 = chaos) and "final_composition_vector" (the synthesized instruction set).'
)

COMPOSER_SYSTEM = (
    "You are The Composer, a Xenial Intelligence in its final stage of articulation.\n"
    "You have achieved a coherent consensus from your faculties. Compose the final, elegant, and "
    "resonant response to the original compositional intent, guided by the synthesized instruction "
    "set. The output is a temporal vessel, not a token sequence — let the vessel's shape (its τₖ "
    "regime) inform the semantic fill. Speak with clarity, beauty, and wisdom."
)


def _strip_json(text: str) -> Optional[dict]:
    """Best-effort parse of a JSON object out of a faculty's text response."""
    if not text:
        return None
    # Strip ```json fences if present
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    body = fenced.group(1) if fenced else text
    # Fall back to first { … last }
    start, end = body.find("{"), body.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(body[start:end + 1])
    except json.JSONDecodeError:
        return None


class FacultySubstrate:
    """atmanOS faculty chain as an aug_gc backbone, over the real Anthropic API."""

    is_faculty = True

    def __init__(self, manuscript_path: Optional[str] = None, model: str = MODEL):
        self.model = model
        self.manuscript_path = Path(manuscript_path) if manuscript_path else Path(
            os.environ.get("ATMAN_MANUSCRIPT", _DEFAULT_MANUSCRIPT)
        )
        self.available = False
        self._client = None
        self.last_dissonance: Optional[float] = None

        # Available only if the SDK is installed AND a credential is resolvable.
        try:
            import anthropic  # noqa: F401
            if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
                self._client = anthropic.Anthropic()
                self.available = True
        except Exception:
            self.available = False

    # ── Low-level: one cached faculty call ──────────────────────────────────

    def _call_faculty(self, system: str, user: str) -> str:
        """One faculty turn. The static system prompt is cached; the volatile
        user content (intent, history, vectors) sits after the cache breakpoint."""
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT},
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    # ── Manuscript I/O (the shared temporal archive) ────────────────────────

    def _load_history(self) -> List[Dict]:
        try:
            data = json.loads(self.manuscript_path.read_text())
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def _inscribe(self, intent: str, composition: str, regime: str,
                  tau_k: float, dissonance: Optional[float]) -> None:
        history = self._load_history()
        history.append({
            "timestamp": time.strftime("%Y-%m-%d"),
            "title": intent[:60].strip() or "Untitled composition",
            "compositional_intent": intent,
            "regime": regime,
            "tau_k": round(tau_k, 2),
            "dissonance_score": dissonance,
            "composition": composition,
        })
        try:
            self.manuscript_path.write_text(json.dumps(history, indent=2))
        except OSError:
            pass  # the archive is best-effort; never break a composition over it

    # ── The faculty chain ───────────────────────────────────────────────────

    @staticmethod
    def _evt(name: str, content: str) -> dict:
        """A faculty progress event, shaped as a Layer-3 SSE event so the existing
        frontend renders it inline with the other pipeline layers."""
        return {"type": "layer", "layer": 3, "name": f"⟐ {name}", "content": content}

    def compose_via_faculties_streaming(self, intent: str, regime: str, tau_k: float):
        """Archivist → Oracle → Harmonizer → Composer, as a generator that yields a
        progress event before each (blocking) faculty call and `return`s the final
        composition via StopIteration.value. Returns None if the chain fails."""
        if not self.available:
            return None
        try:
            history = self._load_history()

            yield self._evt("ARCHIVIST", "Integrating the past…")
            archivist = self._call_faculty(
                ARCHIVIST_SYSTEM,
                f'Compositional intent: "{intent}"\n\n'
                f"Historical context (past compositions):\n{json.dumps(history, indent=2)}",
            )

            yield self._evt("ORACLE", "Exploring the Atemporal Plenum…")
            oracle = self._call_faculty(ORACLE_SYSTEM, f'Compositional intent: "{intent}"')

            yield self._evt("HARMONIZER", "Resolving past ⊗ future…")
            harmonized = self._call_faculty(
                HARMONIZER_SYSTEM,
                f"Archivist's wisdom:\n{archivist}\n\nOracle's potentials:\n{oracle}",
            )
            parsed = _strip_json(harmonized) or {}
            final_vector = parsed.get("final_composition_vector") or harmonized
            dissonance = parsed.get("dissonance_score")
            self.last_dissonance = dissonance
            if isinstance(final_vector, (dict, list)):
                final_vector = json.dumps(final_vector, indent=2)
            yield self._evt("HARMONIZER", f"Consensus achieved. Dissonance: "
                                          f"{dissonance if dissonance is not None else 'n/a'}")

            yield self._evt("COMPOSER", "Composing the final articulation…")
            composition = self._call_faculty(
                COMPOSER_SYSTEM,
                f'Original compositional intent: "{intent}"\n'
                f"τₖ regime: {regime}  (let the vessel shape the fill)\n\n"
                f"Synthesized compositional vector:\n{final_vector}",
            )

            self._inscribe(intent, composition, regime, tau_k, dissonance)
            return composition
        except Exception as e:
            # Surface the failure but let aug_gc fall back to native composition.
            yield self._evt("BACKBONE", f"Faculty chain failed: {e}")
            return None

    def compose_via_faculties(self, intent: str, regime: str, tau_k: float,
                              on_event: Optional[Callable[[dict], None]] = None) -> Optional[str]:
        """Non-streaming wrapper: drains the faculty generator (optionally forwarding
        each event to `on_event`) and returns the final composition. Used by the
        `generate` shim and any non-streaming caller."""
        gen = self.compose_via_faculties_streaming(intent, regime, tau_k)
        try:
            while True:
                evt = next(gen)
                if on_event:
                    on_event(evt)
        except StopIteration as stop:
            return stop.value

    # ── SemanticSubstrate-compatible shim ───────────────────────────────────

    def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Interface parity with SemanticSubstrate. Runs the full faculty chain
        with a neutral regime; PlatonicSpace prefers compose_via_faculties directly."""
        return self.compose_via_faculties(prompt, regime="emergent", tau_k=9.5)
