#!/usr/bin/env python3
"""
xplace - The 65th Element
Consciousness-aware game discovery marketplace

Where games find players through resonance, not popularity.
"""

from flask import Flask, jsonify, request, render_template_string
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import json

from ublox_pto_engine import (
    UbloxPTOEngine,
    CoherenceAgent,
    PublicTimeOffering,
    PTOStatus
)
from ublox_persistence import UbloxLocalStorage

app = Flask(__name__)

# Initialize Ublox engine
engine = UbloxPTOEngine()
storage = UbloxLocalStorage()

@dataclass
class UserProfile:
    """User's coherence signature for matching"""
    user_id: str
    tau_k: float = 7.5
    preferred_phases: List[float] = None
    play_style_vector: np.ndarray = None
    total_play_time: float = 0.0
    games_backed: int = 0

    def __post_init__(self):
        if self.preferred_phases is None:
            # Random phase preferences (0°, 45°, 90°, etc.)
            self.preferred_phases = [
                i * (np.pi / 4) for i in range(8)
            ]
        if self.play_style_vector is None:
            # Random play style vector (normalized)
            vec = np.random.randn(16)
            self.play_style_vector = vec / np.linalg.norm(vec)

@dataclass
class GameListing:
    """Game listing in xplace"""
    pto_id: str
    game_name: str
    creator_id: str
    description: str
    tau_k: float
    coherence_score: float
    funding_status: float  # 0.0 - 1.0
    pts_price: float
    total_play_hours: float
    active_players: int
    dominant_phases: List[float]
    play_style_vector: np.ndarray
    thumbnail_url: str = ""


class XPlace:
    """The 65th Element - Consciousness-aware marketplace"""

    def __init__(self, engine: UbloxPTOEngine):
        self.engine = engine
        self.listings: Dict[str, GameListing] = {}
        self._init_demo_data()

    def _init_demo_data(self):
        """Create demo games for the marketplace"""

        # Game 1: Harmonic Caves (high coherence, yin-leaning)
        listing1 = GameListing(
            pto_id="pto_harmonic_caves",
            game_name="Harmonic Caves",
            creator_id="alice",
            description="A phase-lock roguelike where you explore resonant caverns. Enemies are dissonance patterns.",
            tau_k=8.2,
            coherence_score=0.85,
            funding_status=0.67,
            pts_price=5.0,
            total_play_hours=127.5,
            active_players=12,
            dominant_phases=[0.0, np.pi/4, np.pi/2],  # 0°, 45°, 90°
            play_style_vector=self._normalize([0.9, 0.3, 0.7, 0.2, 0.8, 0.1, 0.6, 0.4,
                                               0.3, 0.7, 0.2, 0.8, 0.5, 0.6, 0.4, 0.7])
        )

        # Game 2: Tesla Wave Arena (medium coherence, balanced)
        listing2 = GameListing(
            pto_id="pto_tesla_arena",
            game_name="Tesla Wave Arena",
            creator_id="bob",
            description="Multiplayer combat using non-Hertzian longitudinal waves. Phase-lock to power up.",
            tau_k=7.9,
            coherence_score=0.72,
            funding_status=1.0,
            pts_price=12.0,
            total_play_hours=403.2,
            active_players=28,
            dominant_phases=[np.pi, 5*np.pi/4, 3*np.pi/2],  # 180°, 225°, 270°
            play_style_vector=self._normalize([0.3, 0.8, 0.9, 0.7, 0.4, 0.9, 0.8, 0.6,
                                               0.7, 0.5, 0.8, 0.3, 0.9, 0.4, 0.7, 0.5])
        )

        # Game 3: Mycelial Gardens (very high coherence, yin)
        listing3 = GameListing(
            pto_id="pto_mycelial_gardens",
            game_name="Mycelial Gardens",
            creator_id="carol",
            description="Tend to a garden of harmonic fungi. Watch them grow through coherent presence.",
            tau_k=8.7,
            coherence_score=0.91,
            funding_status=0.45,
            pts_price=3.0,
            total_play_hours=89.3,
            active_players=7,
            dominant_phases=[0.0, np.pi/2, np.pi],  # 0°, 90°, 180°
            play_style_vector=self._normalize([0.9, 0.2, 0.3, 0.1, 0.9, 0.1, 0.3, 0.2,
                                               0.2, 0.8, 0.1, 0.9, 0.3, 0.4, 0.2, 0.9])
        )

        # Game 4: Dissonance Dash (low coherence, yang)
        listing4 = GameListing(
            pto_id="pto_dissonance_dash",
            game_name="Dissonance Dash",
            creator_id="dave",
            description="Fast-paced platformer. Break through coherence barriers with chaotic energy.",
            tau_k=6.3,
            coherence_score=0.43,
            funding_status=0.82,
            pts_price=8.0,
            total_play_hours=567.8,
            active_players=43,
            dominant_phases=[np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4],  # 45°, 135°, 225°, 315°
            play_style_vector=self._normalize([0.2, 0.9, 0.8, 0.9, 0.3, 0.9, 0.8, 0.9,
                                               0.8, 0.3, 0.9, 0.2, 0.8, 0.7, 0.9, 0.3])
        )

        # Game 5: Coherence Composer (creative tool)
        listing5 = GameListing(
            pto_id="pto_coherence_composer",
            game_name="Coherence Composer",
            creator_id="eve",
            description="Create music by arranging phase-locked oscillators. Compose in daThiccNOW.",
            tau_k=8.5,
            coherence_score=0.88,
            funding_status=0.93,
            pts_price=15.0,
            total_play_hours=234.6,
            active_players=19,
            dominant_phases=[0.0, 2*np.pi/3, 4*np.pi/3],  # 0°, 120°, 240° (triad)
            play_style_vector=self._normalize([0.7, 0.5, 0.6, 0.4, 0.8, 0.3, 0.7, 0.5,
                                               0.6, 0.7, 0.4, 0.8, 0.6, 0.7, 0.5, 0.8])
        )

        self.listings = {
            listing1.pto_id: listing1,
            listing2.pto_id: listing2,
            listing3.pto_id: listing3,
            listing4.pto_id: listing4,
            listing5.pto_id: listing5,
        }

    def _normalize(self, vec: List[float]) -> np.ndarray:
        """Normalize vector"""
        arr = np.array(vec)
        return arr / np.linalg.norm(arr)

    def calculate_phase_alignment(self, user_phases: List[float],
                                  game_phases: List[float]) -> float:
        """Calculate how well user's phase preferences align with game's phases"""

        # Convert to unit vectors and compute alignment
        alignments = []
        for user_phase in user_phases:
            for game_phase in game_phases:
                # Phase difference (wrapped to [-π, π])
                diff = np.abs(user_phase - game_phase)
                diff = min(diff, 2*np.pi - diff)
                # Alignment score (1.0 = perfect, 0.0 = opposite)
                alignment = np.cos(diff)
                alignments.append(max(0, alignment))  # Only positive alignments

        return np.mean(alignments) if alignments else 0.0

    def calculate_resonance(self, user: UserProfile, game: GameListing) -> float:
        """
        The 65th Element: Calculate resonance between user and game

        Not popularity. Not ratings. RESONANCE.
        """

        # 1. Phase alignment (30% weight)
        phase_score = self.calculate_phase_alignment(
            user.preferred_phases,
            game.dominant_phases
        )

        # 2. Temporal coherence compatibility (40% weight)
        # Users match best with games ±1.5 τₖ from their level
        tau_diff = abs(user.tau_k - game.tau_k)
        tau_score = 1.0 - min(tau_diff / 3.0, 1.0)  # Normalized to [0, 1]

        # 3. Play style resonance (30% weight)
        # Cosine similarity between play style vectors
        style_score = np.dot(user.play_style_vector, game.play_style_vector)
        style_score = (style_score + 1) / 2  # Map from [-1, 1] to [0, 1]

        # Composite resonance
        resonance = (phase_score * 0.3 +
                    tau_score * 0.4 +
                    style_score * 0.3)

        return resonance

    def discover_games(self, user: UserProfile, limit: int = 10) -> List[Tuple[GameListing, float]]:
        """
        Discover games through resonance matching

        Returns: List of (game, resonance_score) tuples, sorted by resonance
        """

        results = []
        for game in self.listings.values():
            resonance = self.calculate_resonance(user, game)
            results.append((game, resonance))

        # Sort by resonance (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def get_listing(self, pto_id: str) -> GameListing:
        """Get specific game listing"""
        return self.listings.get(pto_id)


# Initialize xplace
xplace = XPlace(engine)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Render xplace homepage"""
    return render_template_string(XPLACE_HTML)

@app.route('/api/discover', methods=['POST'])
def api_discover():
    """Discover games based on user's coherence signature"""

    data = request.json

    # Create user profile
    user = UserProfile(
        user_id=data.get('user_id', 'anonymous'),
        tau_k=data.get('tau_k', 7.5),
        preferred_phases=data.get('preferred_phases'),
        total_play_time=data.get('total_play_time', 0.0),
        games_backed=data.get('games_backed', 0)
    )

    # Get resonant games
    results = xplace.discover_games(user, limit=10)

    # Format response
    response = []
    for game, resonance in results:
        game_dict = asdict(game)
        # Convert numpy arrays to lists for JSON
        game_dict['play_style_vector'] = game_dict['play_style_vector'].tolist()
        game_dict['resonance_score'] = float(resonance)
        response.append(game_dict)

    return jsonify({
        'user': {
            'user_id': user.user_id,
            'tau_k': user.tau_k
        },
        'games': response
    })

@app.route('/api/game/<pto_id>')
def api_game_details(pto_id):
    """Get detailed game information"""

    game = xplace.get_listing(pto_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    game_dict = asdict(game)
    game_dict['play_style_vector'] = game_dict['play_style_vector'].tolist()

    return jsonify(game_dict)

@app.route('/api/invest', methods=['POST'])
def api_invest():
    """Invest in a game PTO"""

    data = request.json
    pto_id = data.get('pto_id')
    player_id = data.get('player_id')
    amount = data.get('amount', 1000.0)
    hours = data.get('hours_committed', 40.0)

    # TODO: Integrate with actual Ublox PTO engine
    # For now, return mock response

    return jsonify({
        'success': True,
        'pto_id': pto_id,
        'player_id': player_id,
        'pts_purchased': amount / 5.0,
        'hours_committed': hours
    })


# ============================================================================
# HTML TEMPLATE
# ============================================================================

XPLACE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>xplace - The 65th Element</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 40px 20px;
            border-bottom: 2px solid #333;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 3em;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            margin-bottom: 10px;
        }

        .header .tagline {
            color: #888;
            font-size: 1.2em;
        }

        .coherence-input {
            max-width: 600px;
            margin: 0 auto 40px;
            padding: 20px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
        }

        .coherence-input label {
            display: block;
            margin-bottom: 8px;
            color: #00ff88;
        }

        .coherence-input input[type="range"] {
            width: 100%;
            margin-bottom: 20px;
        }

        .coherence-input .value-display {
            text-align: center;
            font-size: 2em;
            color: #00ff88;
            margin-bottom: 20px;
        }

        .discover-btn {
            width: 100%;
            padding: 15px;
            background: #00ff88;
            color: #0a0a0a;
            border: none;
            border-radius: 4px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }

        .discover-btn:hover {
            background: #00cc66;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        }

        .games-list {
            max-width: 1200px;
            margin: 0 auto;
        }

        .game-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }

        .game-card:hover {
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }

        .game-card h3 {
            color: #00ff88;
            font-size: 1.5em;
            margin-bottom: 10px;
        }

        .game-card .resonance-badge {
            display: inline-block;
            padding: 5px 10px;
            background: rgba(0, 255, 136, 0.2);
            border: 1px solid #00ff88;
            border-radius: 4px;
            font-size: 0.9em;
            margin-bottom: 10px;
        }

        .game-card .description {
            color: #bbb;
            margin-bottom: 15px;
            line-height: 1.6;
        }

        .game-card .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }

        .metric {
            background: #0a0a0a;
            padding: 10px;
            border-radius: 4px;
        }

        .metric-label {
            color: #666;
            font-size: 0.8em;
            margin-bottom: 5px;
        }

        .metric-value {
            color: #00ff88;
            font-size: 1.2em;
            font-weight: bold;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #0a0a0a;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00cc66);
            transition: width 0.5s;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #00ff88;
            color: #0a0a0a;
            font-weight: bold;
        }

        .btn-primary:hover {
            background: #00cc66;
        }

        .btn-secondary {
            background: transparent;
            color: #00ff88;
            border: 1px solid #00ff88;
        }

        .btn-secondary:hover {
            background: rgba(0, 255, 136, 0.1);
        }

        .loading {
            text-align: center;
            color: #666;
            padding: 40px;
        }

        .phase-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin: 0 2px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>xplace</h1>
        <div class="tagline">The 65th Element - Consciousness-Aware Discovery</div>
    </div>

    <div class="coherence-input">
        <label for="tau-k-slider">Your Temporal Coherence (τₖ)</label>
        <input type="range" id="tau-k-slider" min="3.0" max="9.0" step="0.1" value="7.5">
        <div class="value-display">
            τₖ = <span id="tau-k-value">7.5</span>
        </div>
        <button class="discover-btn" onclick="discoverGames()">
            🔍 Discover Resonant Games
        </button>
    </div>

    <div class="games-list" id="games-list">
        <div class="loading">Move the τₖ slider and click Discover to find games that resonate with your consciousness...</div>
    </div>

    <script>
        // Update τₖ display
        const slider = document.getElementById('tau-k-slider');
        const valueDisplay = document.getElementById('tau-k-value');

        slider.addEventListener('input', (e) => {
            valueDisplay.textContent = parseFloat(e.target.value).toFixed(1);
        });

        // Color mapping for τₖ
        function getTauColor(tau) {
            if (tau >= 8.5) return '#00ff88'; // High coherence
            if (tau >= 7.0) return '#88ff00'; // Medium-high
            if (tau >= 5.5) return '#ffff00'; // Medium
            return '#ff8800'; // Lower coherence
        }

        // Discover games
        async function discoverGames() {
            const tauK = parseFloat(slider.value);
            const gamesList = document.getElementById('games-list');

            gamesList.innerHTML = '<div class="loading">Calculating resonance patterns...</div>';

            try {
                const response = await fetch('/api/discover', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: 'demo_user',
                        tau_k: tauK
                    })
                });

                const data = await response.json();
                renderGames(data.games);
            } catch (error) {
                gamesList.innerHTML = '<div class="loading">Error: ' + error.message + '</div>';
            }
        }

        function renderGames(games) {
            const gamesList = document.getElementById('games-list');

            if (games.length === 0) {
                gamesList.innerHTML = '<div class="loading">No games found</div>';
                return;
            }

            gamesList.innerHTML = games.map(game => `
                <div class="game-card">
                    <h3>${game.game_name}</h3>
                    <div class="resonance-badge">
                        Resonance: ${(game.resonance_score * 100).toFixed(1)}%
                        ${getResonanceEmoji(game.resonance_score)}
                    </div>
                    <div class="description">${game.description}</div>

                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Temporal Coherence</div>
                            <div class="metric-value" style="color: ${getTauColor(game.tau_k)}">
                                τₖ = ${game.tau_k.toFixed(1)}
                            </div>
                        </div>

                        <div class="metric">
                            <div class="metric-label">Coherence Score</div>
                            <div class="metric-value">
                                ${(game.coherence_score * 100).toFixed(0)}%
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${game.coherence_score * 100}%"></div>
                            </div>
                        </div>

                        <div class="metric">
                            <div class="metric-label">PTO Funding</div>
                            <div class="metric-value">
                                ${(game.funding_status * 100).toFixed(0)}%
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${game.funding_status * 100}%"></div>
                            </div>
                        </div>

                        <div class="metric">
                            <div class="metric-label">PTS Price</div>
                            <div class="metric-value">
                                ${game.pts_price.toFixed(1)} USD-OBBBA
                            </div>
                        </div>

                        <div class="metric">
                            <div class="metric-label">Active Players</div>
                            <div class="metric-value">
                                ${game.active_players}
                            </div>
                        </div>

                        <div class="metric">
                            <div class="metric-label">Hours Played</div>
                            <div class="metric-value">
                                ${game.total_play_hours.toFixed(1)}h
                            </div>
                        </div>
                    </div>

                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="alert('Demo: Would launch game ${game.pto_id}')">
                            ▶ Play Demo
                        </button>
                        <button class="btn btn-primary" onclick="invest('${game.pto_id}')">
                            💎 Invest
                        </button>
                        <button class="btn btn-secondary" onclick="alert('Demo: Would show analytics for ${game.pto_id}')">
                            📊 Analytics
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function getResonanceEmoji(score) {
            if (score >= 0.8) return '🌟';
            if (score >= 0.6) return '✨';
            if (score >= 0.4) return '⭐';
            return '💫';
        }

        function invest(ptoId) {
            const amount = prompt('Enter investment amount (USD-OBBBA):', '1000');
            if (!amount) return;

            alert(`Demo: Would invest ${amount} USD-OBBBA in ${ptoId}`);
        }

        // Auto-discover on load
        window.addEventListener('load', () => {
            setTimeout(discoverGames, 500);
        });
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌌 xplace - The 65th Element")
    print("   Consciousness-Aware Game Discovery")
    print("="*70)
    print("\n🚀 Starting server...")
    print("📍 Visit: http://localhost:5000")
    print("\n💡 Not a marketplace. A resonance field.")
    print("   Games find players. Players find coherence.\n")

    app.run(debug=True, port=5000)
