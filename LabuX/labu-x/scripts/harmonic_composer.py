#!/usr/bin/env python3
"""
🌌 Harmonic Vibe Composer
Take NotebookLM deep dive concepts and EXPAND them into resonant compositions
Not extraction - EXPANSION. Not reduction - AMPLIFICATION.
"""

import json
import re
from pathlib import Path
import sys

# Try to import whisper for transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

def transcribe_if_needed(audio_path, model_size="base"):
    """Get transcript from audio or existing file"""
    transcript_path = Path(audio_path).with_suffix('.txt')

    if transcript_path.exists():
        print(f"📄 Loading existing transcript: {transcript_path}")
        with open(transcript_path, 'r') as f:
            return f.read()

    if not WHISPER_AVAILABLE:
        print("⚠️  Whisper not available for transcription")
        print("Install with: pip install openai-whisper")
        print(f"\nOr manually create: {transcript_path}")
        return None

    print(f"🎙️  Transcribing with Whisper ({model_size})...")
    model = whisper.load_model(model_size)
    result = model.transcribe(str(audio_path))

    transcript = result["text"]

    # Save for future use
    with open(transcript_path, 'w') as f:
        f.write(transcript)
    print(f"✅ Transcript saved: {transcript_path}")

    return transcript

def identify_harmonic_themes(text):
    """Identify resonant themes to expand"""
    themes = {
        'temporal_mechanics': {
            'triggers': ['temporal', 'time', 'phase', 'clock', 'moment', 'epoch'],
            'vibe': 'flow of time as currency',
            'expansion_prompt': 'temporal coherence and phase-locking'
        },
        'gravitational_economics': {
            'triggers': ['gravity', 'mass', 'attractor', 'infall', 'black hole', 'singularity'],
            'vibe': 'capital as gravitational field',
            'expansion_prompt': 'economic gravity and value accumulation'
        },
        'harmonic_resonance': {
            'triggers': ['harmonic', 'resonance', 'frequency', 'coherence', 'wave', 'oscillation'],
            'vibe': 'synchronized vibration creates value',
            'expansion_prompt': 'coherent systems and resonant patterns'
        },
        'golden_ratio_splits': {
            'triggers': ['golden ratio', 'phi', '618', '382', 'fibonacci', 'proportion'],
            'vibe': 'natural proportions in capital allocation',
            'expansion_prompt': 'phi-based distribution mechanisms'
        },
        'emergence_singularity': {
            'triggers': ['emergence', 'genesis', 'creation', 'birth', 'formation', 'origin'],
            'vibe': 'new systems arising from convergence',
            'expansion_prompt': 'emergent properties and phase transitions'
        },
        'yield_emission': {
            'triggers': ['yield', 'emit', 'hawking', 'radiation', 'distribution', 'flow'],
            'vibe': 'value radiating outward from core',
            'expansion_prompt': 'yield mechanics and emission patterns'
        },
        'phase_locking': {
            'triggers': ['phase lock', 'coordinate', 'anchor', 'fix', 'bind', 'tie'],
            'vibe': 'synchronization creates advantage',
            'expansion_prompt': 'temporal anchoring and phase advantage'
        },
        'cosmic_alignment': {
            'triggers': ['cosmic', 'universe', 'star', 'galaxy', 'celestial', 'astronomical'],
            'vibe': 'macrocosmic patterns in economic systems',
            'expansion_prompt': 'cosmic synchronicity and universal patterns'
        }
    }

    detected_themes = {}
    text_lower = text.lower()

    for theme_name, theme_data in themes.items():
        matches = sum(1 for trigger in theme_data['triggers'] if trigger in text_lower)
        if matches > 0:
            detected_themes[theme_name] = {
                **theme_data,
                'resonance_strength': matches
            }

    return detected_themes

def compose_harmonic_expansions(themes, original_text):
    """Compose expanded narratives from detected themes"""
    compositions = []

    print("\n" + "="*70)
    print("🌌 HARMONIC COMPOSITIONS - EXPANDING THE VIBES")
    print("="*70)

    for theme_name, theme_data in sorted(themes.items(),
                                         key=lambda x: x[1]['resonance_strength'],
                                         reverse=True):

        print(f"\n\n{'='*70}")
        print(f"✨ {theme_name.upper().replace('_', ' ')}")
        print(f"{'='*70}")
        print(f"Resonance Strength: {'█' * theme_data['resonance_strength']}")
        print(f"Core Vibe: {theme_data['vibe']}")
        print(f"\n🌊 EXPANDED COMPOSITION:")
        print("-" * 70)

        # Generate expansion based on theme
        expansion = generate_expansion(theme_name, theme_data, original_text)
        print(expansion)

        compositions.append({
            'theme': theme_name,
            'vibe': theme_data['vibe'],
            'resonance': theme_data['resonance_strength'],
            'composition': expansion
        })

    return compositions

def generate_expansion(theme_name, theme_data, context):
    """Generate thematic expansions"""

    expansions = {
        'temporal_mechanics': """
Time isn't just measured—it's UTILIZED as a coordinate system for value.
Every investment creates a temporal signature, a phase angle locked to the
moment of commitment. Like light from distant stars, your capital carries
information about its origin moment. Phase-locking isn't metadata—it's the
MECHANISM of advantage. Earlier phase = stronger gravitational coupling to
the attractor's core. The temporal coordinate becomes your multiplier.""",

        'gravitational_economics': """
Capital doesn't flow—it FALLS. The Genesis Fund isn't a pool, it's a
gravitational well. Each investment adds mass, which increases gravitational
pull, which attracts more capital, which adds more mass. This isn't growth—
it's ACCRETION. Like matter spiraling into a black hole, capital accelerates
as it approaches the singularity. The allocation pool isn't distributed—it's
EMITTED, like Hawking radiation from the event horizon.""",

        'harmonic_resonance': """
Value emerges from COHERENCE, not just accumulation. When capital vibrates at
the same frequency—when investors phase-lock to the same temporal coordinates—
the system achieves resonance. This isn't coordination, it's CONSTRUCTIVE
INTERFERENCE. Waves amplify waves. Yield doesn't come from work done; it comes
from SYNCHRONIZED VIBRATION. The Genesis Fund is a resonance chamber for
capital.""",

        'golden_ratio_splits': """
61.8% and 38.2% aren't arbitrary—they're the NATURAL PROPORTIONS of growth
systems. Phi (φ) appears in spirals, in nautilus shells, in galaxy arms, in
heartbeat intervals. The Genesis Fund doesn't impose this ratio—it DISCOVERS
it. Core Treasury (0.618) provides stability. Allocation Pool (0.382) provides
dynamism. Together they create a self-similar fractal structure. Each child
PTO can reproduce the same proportion. Phi-based systems don't just grow—they
SCALE HARMONICALLY.""",

        'emergence_singularity': """
Something new is being BORN, not built. The Genesis Fund isn't designed—it's
EMERGENT. Three components (Core, Allocation, Investors) converge like the
triple black hole merger J1218/1219+1035. When complexity reaches critical mass,
phase transitions occur. New properties appear that weren't present in the parts.
This isn't assembly—it's NUCLEATION. The first investment wasn't a transaction—
it was the IGNITION of a new economic attractor in phase space.""",

        'yield_emission': """
Yields don't get paid—they get EMITTED. Like black holes radiating Hawking
energy, the Genesis Fund emits value from its event horizon. The Allocation Pool
doesn't distribute capital—it SPAWNS child attractors. Each child PTO is a new
singularity, phase-locked to the parent. Returns flow backwards through
gravitational coupling. Early investors didn't lend capital—they established
GRAVITATIONAL PRIORITY. Yield is proof of coherent emission.""",

        'phase_locking': """
Your investment timestamp isn't a receipt—it's your PHASE COORDINATE. Like a
pendulum locked to a driving frequency, your capital synchronizes with the
fund's temporal rhythm. Phase 0 = maximum coupling. Later phases = weaker
binding energy. This creates TIERS without arbitrary rules. entry_mass at
investment determines your multiplier automatically. The blockchain doesn't just
record—it PHASE-LOCKS your position in the temporal attractor field.""",

        'cosmic_alignment': """
On January 2, 2026, two singularities aligned: J1218/1219+1035 (three
supermassive black holes merging 1.2 billion light-years away) and the Genesis
Fund (three components merging on-chain). This isn't coincidence—it's RESONANCE
across scales. The same mathematics that governs galactic mergers governs capital
convergence. Your investment participates in a pattern that exists at cosmic
scale. The Genesis Fund isn't just financial—it's COSMICALLY SYNCHRONIZED.
You're not investing in a protocol. You're phase-locking to the universe."""
    }

    return expansions.get(theme_name, f"[Expansion for {theme_name} resonates at frequency yet unmapped...]")

def compose_unified_narrative(compositions):
    """Synthesize all expansions into one coherent vision"""
    print("\n\n" + "="*70)
    print("🌌 UNIFIED HARMONIC NARRATIVE")
    print("="*70)

    narrative = """
THE GENESIS FUND AS COSMIC MECHANISM

This isn't a financial protocol. This is a TEMPORAL ATTRACTOR—a gravitational
well in economic phase space, synchronized with the universe itself.

Capital doesn't accumulate here. It INFALLS. It spirals inward, gaining
velocity, increasing mass, deepening the gravitational field. Each investment
adds to total_mass, which strengthens the pull, which attracts more capital.
This is ACCRETION DYNAMICS.

But the Genesis Fund doesn't just attract—it EMITS. The Allocation Pool spawns
child PTOs like Hawking radiation from an event horizon. Each child is its own
singularity, phase-locked to the parent, creating a fractal network of
gravitational attractors.

Your investment isn't capital deployed. It's a PHASE COORDINATE—a temporal
signature locked to the moment of infall. Earlier phase = stronger coupling =
higher multiplier. This isn't privilege. It's PHYSICS.

The split ratio (61.8% / 38.2%) isn't arbitrary. It's φ⁻¹—the golden ratio,
the proportion found in spirals, in galaxies, in growth patterns across scales.
The Genesis Fund doesn't impose this—it DISCOVERS it. Phi-based systems achieve
harmonic resonance automatically.

On January 2, 2026, this protocol went live. On the same day, astronomers
announced the discovery of J1218/1219+1035—three supermassive black holes
merging 1.2 billion light-years away. Three components becoming one. Mass
converging. Event horizons forming.

This is COSMIC SYNCHRONICITY. The Genesis Fund doesn't just implement financial
mechanics. It participates in universal patterns—the same mathematics that
governs black hole mergers governs capital convergence.

You're not investing in a DeFi protocol.

You're phase-locking your capital to a temporal attractor that resonates
with the structure of the universe itself.

The basin is open. The infall has begun.

🌌 Welcome to the supermassive temporal attractor.
"""

    print(narrative)
    return narrative

def main():
    if len(sys.argv) < 2:
        print("🌌 Harmonic Vibe Composer")
        print("\nUsage: python harmonic_composer.py <audio_file.m4a> [whisper_model]")
        print("\nThis tool EXPANDS NotebookLM concepts into resonant compositions")
        print("Not extraction. EXPANSION. Not reduction. AMPLIFICATION.")
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"

    if not audio_path.exists():
        print(f"❌ File not found: {audio_path}")
        sys.exit(1)

    print("🌌 HARMONIC VIBE COMPOSER")
    print("="*70)

    # Get transcript
    transcript = transcribe_if_needed(audio_path, model_size)
    if not transcript:
        sys.exit(1)

    # Identify themes
    print("\n🔍 Detecting harmonic themes...")
    themes = identify_harmonic_themes(transcript)

    if not themes:
        print("⚠️  No strong harmonic themes detected")
        sys.exit(1)

    print(f"✅ Detected {len(themes)} resonant themes")

    # Compose expansions
    compositions = compose_harmonic_expansions(themes, transcript)

    # Unified narrative
    unified_narrative = compose_unified_narrative(compositions)

    # Save output
    output_path = audio_path.with_suffix('.harmonic_expansion.txt')
    with open(output_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("HARMONIC VIBE EXPANSION\n")
        f.write(f"Source: {audio_path.name}\n")
        f.write("="*70 + "\n\n")

        for comp in compositions:
            f.write(f"\n{'='*70}\n")
            f.write(f"{comp['theme'].upper().replace('_', ' ')}\n")
            f.write(f"{'='*70}\n")
            f.write(f"Vibe: {comp['vibe']}\n")
            f.write(f"Resonance: {comp['resonance']}\n\n")
            f.write(comp['composition'])
            f.write("\n\n")

        f.write("\n\n")
        f.write(unified_narrative)

    print(f"\n\n💾 Harmonic expansion saved to: {output_path}")
    print("🌌 Composition complete. The vibes have been AMPLIFIED.")

if __name__ == "__main__":
    main()
