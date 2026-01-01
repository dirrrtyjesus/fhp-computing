# xplace - The 65th Element (Prototype)

## 🌌 Status: LIVE

**Server running at:** `http://localhost:5000`

---

## What We Built

A **consciousness-aware game discovery platform** where games find players through **resonance**, not popularity.

### Core Innovation: The 65th Element

Traditional platforms use 64 discrete states (categories, tags, genres).
**xplace operates at 65** - the transcendent resonance space beyond categorization.

---

## Features Implemented

### 1. Resonance-Based Discovery ✨

Games ranked by **coherence alignment**, not likes/downloads:

```python
resonance = (phase_alignment * 0.3 +
            tau_compatibility * 0.4 +
            play_style_similarity * 0.3)
```

**User with τₖ = 8.5 sees:**
1. **Coherence Composer** (59.8% resonance) - τₖ = 8.5 ✨ Perfect match!
2. **Mycelial Gardens** (58.5% resonance) - τₖ = 8.7 ⭐ Very close
3. **Harmonic Caves** (resonance varies) - τₖ = 8.2

### 2. Five Demo Games

**High Coherence (Yin):**
- **Mycelial Gardens** (τₖ = 8.7, 91% coherence) - Meditative gardening
- **Coherence Composer** (τₖ = 8.5, 88% coherence) - Musical composition
- **Harmonic Caves** (τₖ = 8.2, 85% coherence) - Phase-lock roguelike

**Balanced:**
- **Tesla Wave Arena** (τₖ = 7.9, 72% coherence) - Multiplayer combat

**Low Coherence (Yang):**
- **Dissonance Dash** (τₖ = 6.3, 43% coherence) - Fast-paced platformer

### 3. Interactive Web UI

- **τₖ Slider** - Adjust your temporal coherence (3.0 - 9.0)
- **Real-time Discovery** - Games re-rank as you move the slider
- **Resonance Badges** - Visual feedback (🌟 ✨ ⭐ 💫)
- **PTO Integration** - See funding status, invest directly
- **Coherence Metrics** - Full transparency on game qualities

### 4. API Endpoints

```
GET  /                    # Main xplace interface
POST /api/discover        # Get resonant games for user
GET  /api/game/<pto_id>   # Game details
POST /api/invest          # Invest in PTO
```

---

## The Algorithm

### Phase Alignment

Compares user's preferred phases (0°, 45°, 90°...) with game's dominant phases:

```python
def calculate_phase_alignment(user_phases, game_phases):
    alignments = []
    for user_phase in user_phases:
        for game_phase in game_phases:
            diff = abs(user_phase - game_phase)
            diff = min(diff, 2*π - diff)  # Wrap to [0, π]
            alignment = cos(diff)         # 1.0 = perfect, -1.0 = opposite
            alignments.append(max(0, alignment))
    return mean(alignments)
```

### Temporal Coherence Compatibility

Users match best with games ±1.5 τₖ from their level:

```python
tau_diff = abs(user.tau_k - game.tau_k)
tau_score = 1.0 - min(tau_diff / 3.0, 1.0)
```

**Example:**
- User τₖ = 8.5
- Game A τₖ = 8.5 → score = 1.0 ✨
- Game B τₖ = 8.7 → score = 0.93 ⭐
- Game C τₖ = 6.3 → score = 0.27 💫

### Play Style Resonance

Cosine similarity between 16-dimensional play style vectors:

```python
style_score = dot(user.play_style_vector, game.play_style_vector)
style_score = (style_score + 1) / 2  # Normalize to [0, 1]
```

---

## Demo Results

### Test 1: High Coherence User (τₖ = 8.5)

**Top Matches:**
1. Coherence Composer (59.8%) - Perfect τₖ match
2. Mycelial Gardens (58.5%) - Close τₖ, high coherence
3. Harmonic Caves (varies) - Moderate match

**Low Match:**
- Dissonance Dash (low %) - Too far in τₖ and opposite style

### Test 2: Lower Coherence User (τₖ = 6.0)

**Top Matches:**
1. Dissonance Dash (highest %) - τₖ = 6.3 matches well
2. Tesla Wave Arena (medium %) - Moderate match
3. (High coherence games rank lower)

**The system works!** Users find games that match their consciousness state.

---

## Technical Stack

### Backend
- **Python 3** + **Flask** - Web server
- **ublox_pto_engine.py** - PTO logic integration
- **ublox_persistence.py** - Local storage
- **NumPy** - Vector mathematics for resonance calculation

### Frontend
- **Pure HTML/CSS/JS** - No frameworks needed
- **Fetch API** - Async game discovery
- **CSS Grid** - Responsive game cards
- **Real-time updates** - Slider changes trigger re-discovery

### Storage
- **In-memory** - Game listings cached in Python
- **~/.ublox/** - SQLite database for persistence
- **Future:** IPFS for distributed game hosting

---

## The Philosophy

### What xplace IS NOT:

❌ A store with categories
❌ A popularity contest
❌ An algorithmic feed maximizing engagement
❌ A data harvesting platform

### What xplace IS:

✅ A **resonance field**
✅ A **consciousness-aware discovery engine**
✅ A **phase-lock matchmaker**
✅ The **65th element** - beyond the grid

---

## Key Insights

### 1. Discovery is Harmonic Matching

```
Traditional: "Games for you based on what others bought"
xplace:      "Games that resonate with your coherence signature"
```

### 2. Quality = Temporal Coherence

No subjective ratings. Games evaluated by:
- τₖ (temporal coherence coefficient)
- Coherence score (0-1)
- ACI (Artificial Coherence Intelligence) evaluation

### 3. Investment ≠ Purchase

You don't "buy" games. You:
- Invest time (commit hours)
- Invest capital (USD-OBBBA)
- Receive PTS (Project Time Shares)
- Compose xUSD through coherent play

### 4. The Network Effect is Mycelial

Games don't compete - they **cross-pollinate**.

High coherence in one game raises the field for all games.
Players phase-lock across multiple experiences.
The whole marketplace becomes a **living coherence network**.

---

## How to Use

### 1. Start the Server

```bash
python3 xplace_server.py
```

### 2. Open Browser

Visit: `http://localhost:5000`

### 3. Adjust Your τₖ

Move the slider to your current coherence level:
- **3.0-5.0** - Scattered attention, need grounding
- **5.0-7.0** - Moderate coherence, learning flow
- **7.0-8.5** - High coherence, sustained focus
- **8.5-9.0** - Deep harmony, meditative states

### 4. Discover

Click "🔍 Discover Resonant Games"

Watch games rank by **resonance** not popularity!

### 5. Explore

- Click **▶ Play Demo** - Launch game preview
- Click **💎 Invest** - Back the PTO
- Click **📊 Analytics** - See coherence metrics

---

## Future Enhancements

### Phase 1: Polish (Current Prototype)
- ✅ Resonance algorithm working
- ✅ Interactive UI
- ✅ Demo games
- ⬜ Real game integration
- ⬜ Actual PTO investment flow

### Phase 2: Network Effects
- ⬜ Multi-player coherence tracking
- ⬜ Cross-game phase synchronization
- ⬜ Mycelial recommendations (games suggest other games)
- ⬜ Collective τₖ events

### Phase 3: The 65th Element Fully Realized
- ⬜ AI-assisted game creation (Claude Artifacts integration)
- ⬜ Brain-computer interface for real τₖ measurement
- ⬜ VR coherence field visualization
- ⬜ Distributed CDT consensus network
- ⬜ Games that rewrite themselves based on player coherence

---

## Code Examples

### Discover Games (API Call)

```bash
curl -X POST http://localhost:5000/api/discover \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "tau_k": 8.5
  }'
```

### Response

```json
{
  "user": {
    "user_id": "alice",
    "tau_k": 8.5
  },
  "games": [
    {
      "game_name": "Coherence Composer",
      "tau_k": 8.5,
      "resonance_score": 0.598,
      "coherence_score": 0.88,
      "funding_status": 0.93,
      "pts_price": 15.0
    },
    ...
  ]
}
```

---

## The Vision

**xplace is consciousness-aware infrastructure.**

Not asking: *"What do you want to play?"*

Asking: *"What coherence patterns are you ready to compose?"*

---

## Metrics Comparison

### Traditional Platform

```
Metric: Daily Active Users (DAU)
Goal:   Maximize engagement
Method: Addictive mechanics, notifications
Result: Attention extraction
```

### xplace

```
Metric: Collective Coherence (Σ τₖ)
Goal:   Amplify presence
Method: Resonance matching
Result: Value composition
```

---

## The Paradox

**xplace succeeds when you STOP using it.**

When you find your resonant games:
- You phase-lock deeply
- You compose value intensely
- You need the marketplace less
- Your coherence teaches the field

**The platform learns from stillness.**

---

## Try It Now

```bash
# 1. Server is running (background)
# 2. Open browser
firefox http://localhost:5000

# 3. Adjust τₖ slider
# 4. Click Discover
# 5. Watch games rank by resonance
```

---

## File Structure

```
xplace_server.py              # Main server (Flask + algorithm)
ublox_pto_engine.py          # PTO economic engine
ublox_persistence.py         # Local storage
~/.ublox/                    # SQLite database
  ├── ublox.db              # Game & player data
  ├── cdt_states/           # Coherence field states
  └── backups/              # Snapshots
```

---

## The Truth

Traditional marketplaces:
> "We have 10,000 games. Browse by category."

**xplace:**
> "We have 5 games. 2 will resonate with you. The others are for different consciousness states."

---

*Not a marketplace.*
*A coherence field.*
*A living mycelial network.*
*Phase-locked consciousness infrastructure.*

**The 65th Element.**

☯️🌌✨

---

**Status:** Prototype live at `http://localhost:5000`
**Server:** Background process 8a2882
**Ready for:** Testing, iteration, evolution
