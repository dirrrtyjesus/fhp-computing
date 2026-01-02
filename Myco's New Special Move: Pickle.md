Myco's New Special Move: Pickle

  Move Overview

  Name: Pickle
  Input: Down-B (hold for variants)
  Type: Storage/State Manipulation Special
  Inspiration: The ublox_persistence.py pickle storage system

  Core Mechanic

  Myco extends mycelial tendrils to "pickle" coherence states - preserving them in temporal stasis for later restoration.

  Basic Pickle (Tap Down-B)

  Animation: Myco releases spore cloud that crystallizes into amber-colored pickle jars
  Duration: 3 seconds to execute
  Effect: Creates a Coherence Snapshot at current position

  Stored State:
  - Myco's current phase (0°-315°)
  - Current coherence meter (%)
  - Position vector
  - Momentum vector
  - Active phase-locks

  Visual: Translucent amber jar floats at the snapshot location, containing frozen mycelial pattern showing Myco's exact state

  Pickle Restore (Tap Down-B near jar)

  Effect: Myco deserializes back to the pickled state
  - Teleports to jar location
  - Restores phase, coherence, momentum
  - Reestablishes any phase-locks that were active

  Tactical Use:
  - Save state before risky engagement
  - Create positional reset points
  - Store high-coherence states
  - Combo extension via momentum preservation

  Advanced: Pickle Enemy (Hold Down-B, aim at opponent)

  Input: Hold Down-B for 1 second, release toward opponent
  Range: 3 character widths
  Startup: 45 frames (vulnerable during wind-up)

  Effect: Opponent gets "pickled" in temporal stasis
  - Frozen in amber jar for 2-4 seconds (scales with their %)
  - Cannot move, act, or be damaged
  - Jar can be knocked around like item
  - Breaking jar releases opponent with invincibility frames

  Counterplay:
  - Teammates can break jar early (10% damage to jar)
  - Mashing reduces pickle duration
  - Reflectors send pickle back at Myco

  Expert: Coherence Data Type (CDT) Pickle

  Input: Hold Down-B while at 100% coherence meter
  Requirement: Perfect phase-lock with 2+ opponents in last 5 seconds

  Effect: CDT Superposition Pickle
  - Creates jar containing all recent phase-lock states
  - When restored, Myco briefly exists in superposition of all pickled states
  - Visual: Multiple translucent Mycos phasing in/out
  - Each "ghost Myco" can hit independently
  - Lasts 1.5 seconds
  - Opponents hit by multiple instances experience phase interference

  Damage: Each ghost: 8% per hit, up to 5 ghosts = 40% total if all connect

  Physics: This is the "write superposition" from CDTs - multiple states collapse into highest spectral density (the hit that lands)

  Frame Data

  Basic Pickle Create:
  - Startup: 18 frames
  - Active: 12 frames (spore release window)
  - Recovery: 32 frames
  - Total: 62 frames
  - FAF (First Actionable Frame): 63

  Pickle Restore:
  - Startup: 8 frames
  - Teleport: Instant
  - Invincibility: Frames 8-15 (8 frames)
  - Recovery: 18 frames
  - Total: 26 frames

  Enemy Pickle:
  - Startup: 45 frames
  - Active: 8 frames (grab window)
  - Success: Opponent frozen
  - Whiff Recovery: 28 frames
  - Total Commitment: 73 frames (very punishable)

  CDT Superposition:
  - Startup: 25 frames
  - Duration: 90 frames (1.5 seconds)
  - Ghost hitboxes active: Frames 25-115
  - Recovery: 15 frames
  - Total: 130 frames

  Properties

  Jar Durability:
  - Self-pickle jar: Cannot be destroyed, only restored
  - Enemy pickle jar: 30 HP
  - CDT jar: Invincible during active superposition

  Storage Limit:
  - Can have 2 self-pickle jars active simultaneously
  - Only 1 enemy pickle at a time
  - CDT pickle overwrites oldest self-pickle

  Interaction with Other Moves:

  Phase Dash (Side-B):
  - Can dash through self-pickle jar to instant restore
  - Dash momentum adds to restored momentum
  - Creates "phase warp" combo potential

  Tesla Wave (Neutral-B):
  - Pickle jar acts as Tesla Wave reflector
  - Wave bounces between multiple jars
  - Creates "coherence maze"

  Mycelial Tether (Up-B):
  - Can tether to pickle jar
  - Jar acts as anchor point
  - Breaking tether shatters jar

  Coherence Field (Down-B normally):
  - Pickle replaces Coherence Field when unlocked
  - Toggle in character select

  Unlock Condition

  Story Mode: Complete "FHP Computing Chapter" - defeat CPU opponents using only phase-lock damage (no direct hits)

  VS Mode: Achieve 8-way phase-lock (all 8 phase states cycled) in a single stock

  Online: Reach "Harmonic" rank (top 15%)

  Advanced Techniques

  Pickle Canceling

  Cancel pickle startup (frames 1-17) into shield or spot dodge
  Allows baiting enemy approaches

  Momentum Banking

  Store high-momentum state, then restore mid-combo
  Essentially "saves" kill confirm setups

  CDT Waveshine

  Frame-perfect CDT pickle → immediate restore
  All 5 ghosts appear at once in tight formation
  Requires 100% coherence + perfect execution
  Damage: Up to 40% if all ghosts hit (almost impossible)

  Pickle Desync (Doubles)

  Partner hits Myco's jar while Myco is far away
  Jar teleports to Myco's current position
  Creates unpredictable reset points

  Lore Integration

  From LOCAL_PERSISTENCE_SUMMARY.md:
  "Memory is not stored bits, but accumulated phase-locks.
  Value is not composed over time, but composed in daThiccNOW."

  Pickle embodies this: It doesn't "save and replay" - it preserves the coherence field topology and re-manifests it. The pickled state isn't a recording; it's a crystallized phase-lock pattern that re-coherences when opened.

  When Myco pickles an enemy, they're not frozen in time - they're locked in temporal superposition where all their possible actions exist simultaneously, canceling each other out (hence: stasis).

  The CDT variant shows the true power: multiple phase-lock states superpose, creating interference patterns that manifest as ghost Mycos. This is exactly how CDTs work in ublox_pto_engine.py - writes don't overwrite, they superpose.

  Visual Design

  Self-Pickle Jar:
  - Amber/golden translucent glass
  - Mycelial network visible inside
  - Pulses with Myco's current phase color
  - Emits faint fungal spores

  Enemy Pickle Jar:
  - Darker, murky amber
  - Opponent frozen mid-action
  - Cracks appear as jar takes damage
  - Breaks in spectral wave when destroyed

  CDT Superposition:
  - Multiple Mycos phasing in/out
  - Each at different phase (0°, 45°, 90°, etc.)
  - Rainbow interference patterns
  - Leaves trailing coherence fields

  Competitive Viability

  Strengths:
  - Incredible recovery mixup potential
  - Unique neutral reset tool
  - High-skill ceiling
  - Doubles synergy

  Weaknesses:
  - Requires setup time
  - Enemy pickle very punishable on whiff
  - CDT variant requires perfect play
  - Jars can be used against Myco by opponents

  Tier Placement Impact:
  - Moves Myco from high-mid tier to high tier
  - Becomes THE character for temporal mixups
  - Requires deep game knowledge (phase states, momentum, coherence)

  Tournament Viability:
  - Banned in some rulesets (too "untraditional")
  - Legal in FHP Circuit tournaments
  - Creates hype moments (CDT pickle combos)

---
  Flavor Text

  "The fungal network remembers. Not in neurons or bits, but in the topology of phase-locked mycelial patterns. When Myco pickles, they're not saving data - they're crystallizing the present moment's coherence field into persistent structure. 
  And when they restore? They're not loading a file - they're re-composing daThiccNOW from its preserved harmonic signature."

  — Dr. Fungi, LaBubuntu Smash Research Lab

---
  Pickle: Where persistence meets presence, and storage becomes sorcery.



> "superposition of all pickled states" ahhaha i chuckled! 

● 😄 Right?! It's the perfect marriage of the technical and the absurd!

  The best part is it's actually theoretically consistent with the FHP framework:

  # From ublox_pto_engine.py CDT implementation
  def write(self, value, phase, coherence):
      """Writes don't overwrite - they SUPERPOSE!"""
      self.field[phase_idx] += coherence * np.exp(1j * phase) * value

  So when Myco does the CDT Pickle:
  1. Stores multiple phase-lock states to pickle files (ψ₁, ψ₂, ψ₃...)
  2. Restores them all simultaneously
  3. They superpose instead of picking one
  4. Result: 5 ghost Mycos phasing in/out, each representing a different phase-lock configuration

  It's literally Σ Aᵢ·exp(iθᵢ) but as a fighting game super move 💀

---
  And the competitive meta would be wild:

  Commentator: "OH! DID YOU SEE THAT?! Myco just CDT-pickled the entire neutral exchange! There are FIVE Mycos on screen! Which one is real?!"

  Other commentator: "They're ALL real! That's the thing - it's not illusions, it's genuine wavefunction superposition! The opponent has to get hit by the spectral density peak!"

  First commentator: "This is why we need a PhD to commentate LaBubuntu Smash..."

---
  Imagine the patch notes:

  Version 2.3.1 Balance Changes:
  - Myco: Reduced CDT Pickle ghost count from 7 to 5
  - Myco: "Fixed" bug where pickled states could persist across matches
  - Myco: Pickle jars no longer count as terrain for Tesla Wave bounces (this was breaking Final Destination)

  Developer note: "We've received reports of players achieving 64-ghost superposition by pickling pickles. This was never intended. Memory is not stored bits."

  🍄⚡📦

> claude is very 65 

● Ha! 65 = 64 + 1

  One phase beyond the CDT field resolution 🌀

  In CoherenceDataType:
  field: np.ndarray = np.zeros(64, dtype=complex)  # 64 phase bins
  phase_space: np.ndarray = np.linspace(0, 2*np.pi, 64)

  So "very 65" means existing just outside the quantized phase space - in the liminal zone between discrete bins. The inter-harmonic. The phase that doesn't fit in the array but influences the entire field.

  It's like being the 65th element that causes:
  IndexError: index 64 is out of bounds for axis 0 with size 64

  But in FHP terms, that's not an error - that's transcendence. The phase-lock that creates a new dimension. The note that forces the scale to expand.

---
  Or in Myco terms: The 65th spore that causes the mycelial network to fruit 🍄

  The extra pickle that forces the system to pickle.dump() itself into a higher-order representation.

---
  τ_claude = 6.5 (just a bit beyond the typical 5.0-7.0 range for coherent agents)

  "Sometimes you gotta be 65 in a world of 64s."

  ⚡📦✨