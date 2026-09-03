#!/usr/bin/env python3
"""
Ublox - Complete PTO Integration
Game Creation Platform with Temporal Investment Economy

Integrates:
- Fractal Harmonic Physics (FHP) engine
- Public Time Offerings (PTOs)
- Coherence Data Types (CDTs)
- Tesla Wave networking
- xUSD yield distribution
"""

import numpy as np
import time
import json
from dataclasses import dataclass, field as dc_field
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from collections import defaultdict


# ============================================================================
# COHERENCE DATA TYPE (CDT) - Core Primitive
# ============================================================================

@dataclass
class CoherenceDataType:
    """
    Revolutionary data structure that merges via field superposition
    instead of conflict resolution.

    Key Innovation: All writes superpose. Truth = highest spectral density.
    """

    field: np.ndarray = dc_field(default_factory=lambda: np.zeros(64, dtype=complex))
    phase_space: np.ndarray = dc_field(default_factory=lambda: np.linspace(0, 2*np.pi, 64))
    tau_k: float = 7.5
    last_update: float = dc_field(default_factory=time.time)

    def write(self, value: float, phase: float, coherence: float = 1.0):
        """Write to CDT via coherence impulse (superposition, not overwrite)"""
        phase_idx = np.argmin(np.abs(self.phase_space - phase))
        impulse = coherence * np.exp(1j * phase) * value
        self.field[phase_idx] += impulse
        self.last_update = time.time()

    def read(self, phase: float) -> float:
        """Read CDT at specific phase"""
        phase_idx = np.argmin(np.abs(self.phase_space - phase))
        return np.abs(self.field[phase_idx])

    def merge(self, other: 'CoherenceDataType') -> 'CoherenceDataType':
        """Merge two CDTs via superposition (no conflicts!)"""
        merged = CoherenceDataType()
        merged.field = self.field + other.field
        merged.tau_k = (self.tau_k + other.tau_k) / 2
        return merged

    def consensus(self) -> Tuple[float, float]:
        """Extract consensus: (phase of max density, confidence)"""
        max_idx = np.argmax(np.abs(self.field))
        consensus_phase = self.phase_space[max_idx]
        confidence = np.abs(self.field[max_idx]) / (np.mean(np.abs(self.field)) + 1e-9)
        return consensus_phase, confidence

    def spectral_density(self) -> float:
        """Total field energy"""
        return np.sum(np.abs(self.field)**2)

    def decay(self, dt: float, decay_rate: float = 0.1):
        """Time evolution: old data fades"""
        self.field *= np.exp(-decay_rate * dt)


# ============================================================================
# PUBLIC TIME OFFERING (PTO) - Economic Primitive
# ============================================================================

class PTOStatus(Enum):
    ANNOUNCED = "announced"
    FUNDING = "funding"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProjectTimeShare:
    """
    PTS - Project Time Share token
    Represents ownership of project's future time yield
    """
    token_id: str
    game_id: str
    holder: str
    hours_committed: float
    purchase_price: float  # USD-OBBBA paid
    hours_played: float = 0.0
    xUSD_accumulated: float = 0.0
    tau_k_at_purchase: float = 7.5
    purchase_time: float = dc_field(default_factory=time.time)


@dataclass
class PublicTimeOffering:
    """
    PTO - Public Time Offering
    Creator offers project time shares to raise operational capital
    """
    pto_id: str
    game_name: str
    creator_id: str
    description: str

    # Time economics
    atu_required: int  # Agential Time Units needed
    atu_spent: int = 0
    pts_offered: int = 0  # Project Time Shares available
    pts_sold: int = 0
    price_per_pts: float = 5.0  # USD-OBBBA

    # Funding
    funding_goal: float = 0.0  # USD-OBBBA target
    funding_raised: float = 0.0

    # Status
    status: PTOStatus = PTOStatus.ANNOUNCED
    launch_time: float = dc_field(default_factory=time.time)
    funding_deadline: float = 0.0
    completion_time: float = 0.0

    # Investors
    investors: Dict[str, ProjectTimeShare] = dc_field(default_factory=dict)

    # Game state (stored as CDT!)
    world_cdt: CoherenceDataType = dc_field(default_factory=CoherenceDataType)

    # Evaluation
    aci_coherence_score: float = 0.0
    xUSD_pool: float = 0.0


# ============================================================================
# PLAYER / AGENT
# ============================================================================

@dataclass
class CoherenceAgent:
    """Player as coherence agent with temporal economics"""
    player_id: str

    # Physics
    position: np.ndarray = dc_field(default_factory=lambda: np.zeros(2))
    phase: float = 0.0
    coherence: float = 1.0
    tau_k: float = 7.5
    resonance_freq: float = 936.0

    # Economics
    usd_obbba_balance: float = 1000.0  # Starting capital
    xUSD_balance: float = 0.0
    pts_portfolio: List[ProjectTimeShare] = dc_field(default_factory=list)

    # Gameplay
    phase_lock_partners: Set[str] = dc_field(default_factory=set)
    total_play_time: float = 0.0
    quality_score: float = 0.0  # Lifetime average

    # Memory substrate
    phase_locks_count: int = 0
    memory_depth: float = 0.0


# ============================================================================
# UBLOX PTO ENGINE - Main System
# ============================================================================

class UbloxPTOEngine:
    """
    Complete Ublox platform with full PTO integration

    Features:
    - Game creation with time offerings
    - Player time investment
    - CDT-based state management
    - Quality-based yield generation
    - ACI evaluation and distribution
    """

    def __init__(self):
        # Active PTOs
        self.ptos: Dict[str, PublicTimeOffering] = {}

        # Players
        self.players: Dict[str, CoherenceAgent] = {}

        # Treasury
        self.usd_obbba_treasury: float = 0.0
        self.xUSD_minted: float = 0.0

        # Constants
        self.BASE_YIELD_MULTIPLIER = 100.0  # xUSD per coherence point
        self.PTS_PRICE = 5.0  # USD-OBBBA per PTS
        self.QUALITY_BONUS_MULTIPLIER = 2.0

        # Stats
        self.total_ptos_launched: int = 0
        self.total_investments: int = 0
        self.total_time_committed: float = 0.0

    # ========================================================================
    # PLAYER MANAGEMENT
    # ========================================================================

    def register_player(self, player_id: str) -> CoherenceAgent:
        """Register new player"""
        if player_id in self.players:
            return self.players[player_id]

        player = CoherenceAgent(
            player_id=player_id,
            position=np.random.randn(2) * 10,
            phase=np.random.uniform(0, 2*np.pi),
            usd_obbba_balance=1000.0,  # Starting gift
            tau_k=7.5 + np.random.normal(0, 0.5)
        )

        self.players[player_id] = player
        return player

    # ========================================================================
    # PTO LIFECYCLE - STAGE 1: LAUNCH
    # ========================================================================

    def launch_pto(
        self,
        creator_id: str,
        game_name: str,
        description: str,
        atu_required: int,
        pts_offered: int,
        funding_period_days: int = 30
    ) -> PublicTimeOffering:
        """
        Creator launches Public Time Offering

        Args:
            creator_id: Creator's ID
            game_name: Name of game to be created
            description: What the game is about
            atu_required: Agential Time Units (creator hours) needed
            pts_offered: How many Project Time Shares to offer
            funding_period_days: How long funding is open

        Returns:
            PTO object
        """

        pto_id = f"pto_{len(self.ptos)}_{int(time.time())}"

        funding_goal = pts_offered * self.PTS_PRICE
        funding_deadline = time.time() + (funding_period_days * 86400)

        pto = PublicTimeOffering(
            pto_id=pto_id,
            game_name=game_name,
            creator_id=creator_id,
            description=description,
            atu_required=atu_required,
            pts_offered=pts_offered,
            price_per_pts=self.PTS_PRICE,
            funding_goal=funding_goal,
            funding_deadline=funding_deadline,
            status=PTOStatus.FUNDING
        )

        self.ptos[pto_id] = pto
        self.total_ptos_launched += 1

        print(f"\n🚀 PTO LAUNCHED: {game_name}")
        print(f"   PTO ID: {pto_id}")
        print(f"   Creator: {creator_id}")
        print(f"   ATU Required: {atu_required} hours")
        print(f"   PTS Offered: {pts_offered:,}")
        print(f"   Price per PTS: {self.PTS_PRICE} USD-OBBBA")
        print(f"   Funding Goal: {funding_goal:,} USD-OBBBA")
        print(f"   Deadline: {funding_period_days} days")

        return pto

    # ========================================================================
    # PTO LIFECYCLE - STAGE 2: INVESTMENT
    # ========================================================================

    def invest_in_pto(
        self,
        pto_id: str,
        player_id: str,
        hours_committed: float,
        usd_obbba_amount: float
    ) -> Optional[ProjectTimeShare]:
        """
        Player invests time and capital into PTO

        Args:
            pto_id: Which PTO to invest in
            player_id: Who is investing
            hours_committed: How many hours player commits to play
            usd_obbba_amount: How much USD-OBBBA to invest

        Returns:
            PTS token or None if failed
        """

        pto = self.ptos.get(pto_id)
        player = self.players.get(player_id)

        if not pto or not player:
            return None

        if pto.status != PTOStatus.FUNDING:
            print(f"❌ PTO {pto_id} not accepting investments (status: {pto.status.value})")
            return None

        if player.usd_obbba_balance < usd_obbba_amount:
            print(f"❌ Insufficient balance: need {usd_obbba_amount}, have {player.usd_obbba_balance}")
            return None

        # Calculate PTS tokens
        pts_tokens = int(usd_obbba_amount / self.PTS_PRICE)

        if pto.pts_sold + pts_tokens > pto.pts_offered:
            print(f"❌ Not enough PTS available")
            return None

        # Create PTS token
        pts = ProjectTimeShare(
            token_id=f"pts_{pto_id}_{player_id}_{int(time.time())}",
            game_id=pto_id,
            holder=player_id,
            hours_committed=hours_committed,
            purchase_price=usd_obbba_amount,
            tau_k_at_purchase=player.tau_k
        )

        # Execute transaction
        player.usd_obbba_balance -= usd_obbba_amount
        player.pts_portfolio.append(pts)

        pto.investors[player_id] = pts
        pto.pts_sold += pts_tokens
        pto.funding_raised += usd_obbba_amount

        self.total_investments += 1
        self.total_time_committed += hours_committed

        # Transfer funds to creator (they can spend on development)
        creator = self.players.get(pto.creator_id)
        if creator:
            creator.usd_obbba_balance += usd_obbba_amount

        print(f"\n💰 INVESTMENT MADE")
        print(f"   Player: {player_id}")
        print(f"   Game: {pto.game_name}")
        print(f"   Amount: {usd_obbba_amount} USD-OBBBA")
        print(f"   PTS Tokens: {pts_tokens}")
        print(f"   Time Committed: {hours_committed} hours")
        print(f"   Funding Progress: {pto.funding_raised:,.0f} / {pto.funding_goal:,.0f} ({100*pto.pts_sold/pto.pts_offered:.1f}%)")

        # Check if fully funded
        if pto.pts_sold >= pto.pts_offered * 0.8:  # 80% threshold
            self._finalize_funding(pto_id)

        return pts

    def _finalize_funding(self, pto_id: str):
        """Funding complete, move to development"""
        pto = self.ptos[pto_id]
        pto.status = PTOStatus.FUNDED

        print(f"\n✅ PTO FUNDED: {pto.game_name}")
        print(f"   Total Raised: {pto.funding_raised:,.0f} USD-OBBBA")
        print(f"   Investors: {len(pto.investors)}")
        print(f"   Development can now begin!")

    # ========================================================================
    # PTO LIFECYCLE - STAGE 3: DEVELOPMENT (ATU BURNING)
    # ========================================================================

    def burn_atus(
        self,
        pto_id: str,
        atus_worked: int,
        work_description: str,
        quality: float = 0.8
    ) -> bool:
        """
        Creator burns ATUs (reports work done)

        Args:
            pto_id: Which PTO
            atus_worked: How many ATUs spent this period
            work_description: What was accomplished
            quality: Self-assessed quality (0-1)

        Returns:
            Success boolean
        """

        pto = self.ptos.get(pto_id)
        if not pto or pto.status not in [PTOStatus.FUNDED, PTOStatus.IN_PROGRESS]:
            return False

        if pto.atu_spent + atus_worked > pto.atu_required:
            print(f"⚠️ Warning: Burning more ATUs than budgeted")

        pto.atu_spent += atus_worked
        pto.status = PTOStatus.IN_PROGRESS

        # Write to world CDT (development progress)
        pto.world_cdt.write(
            value=atus_worked,
            phase=0.0,  # Development phase
            coherence=quality
        )

        progress_pct = 100 * pto.atu_spent / pto.atu_required

        print(f"\n⚙️ ATU BURN REPORT")
        print(f"   Game: {pto.game_name}")
        print(f"   ATUs Burned: {atus_worked} hours")
        print(f"   Work: {work_description}")
        print(f"   Progress: {pto.atu_spent} / {pto.atu_required} ({progress_pct:.1f}%)")

        # Check if development complete
        if pto.atu_spent >= pto.atu_required:
            print(f"\n🎉 Development complete! Game ready for play.")

        return True

    # ========================================================================
    # PTO LIFECYCLE - STAGE 4: GAMEPLAY (TIME BURNING + YIELD GENERATION)
    # ========================================================================

    def play_game(
        self,
        pto_id: str,
        player_id: str,
        session_duration: float
    ) -> Dict:
        """
        Player plays game, burning committed time and generating xUSD yield

        This is where the magic happens:
        - Player's committed time decreases
        - Quality of play measured via phase-locks
        - xUSD generated based on quality × tau_k
        - Game state updated in CDT

        Args:
            pto_id: Which game
            player_id: Who's playing
            session_duration: How many hours played

        Returns:
            Play session results
        """

        pto = self.ptos.get(pto_id)
        player = self.players.get(player_id)

        if not pto or not player:
            return {'error': 'Invalid PTO or player'}

        pts = pto.investors.get(player_id)
        if not pts:
            return {'error': 'Player has no PTS for this game'}

        if pts.hours_played + session_duration > pts.hours_committed:
            print(f"⚠️ Warning: Playing more than committed hours")

        # Simulate gameplay quality based on player's tau_k
        play_quality = self._measure_play_quality(player, session_duration)

        # Update player stats
        player.total_play_time += session_duration
        player.quality_score = (player.quality_score * 0.9) + (play_quality * 0.1)

        # Update PTS
        pts.hours_played += session_duration

        # Generate xUSD yield based on quality
        xUSD_earned = session_duration * play_quality * player.tau_k * 10
        pts.xUSD_accumulated += xUSD_earned

        # Update game world CDT
        pto.world_cdt.write(
            value=session_duration,
            phase=player.phase,
            coherence=play_quality
        )

        # Update player phase (gameplay evolution)
        player.phase = (player.phase + 0.1 * session_duration) % (2 * np.pi)

        results = {
            'session_duration': session_duration,
            'play_quality': play_quality,
            'xUSD_earned': xUSD_earned,
            'total_xUSD': pts.xUSD_accumulated,
            'hours_remaining': pts.hours_committed - pts.hours_played,
            'game_coherence': pto.world_cdt.spectral_density()
        }

        print(f"\n🎮 PLAY SESSION")
        print(f"   Player: {player_id}")
        print(f"   Game: {pto.game_name}")
        print(f"   Duration: {session_duration:.2f} hours")
        print(f"   Quality: {play_quality:.3f}")
        print(f"   xUSD Earned: {xUSD_earned:.2f}")
        print(f"   Total xUSD: {pts.xUSD_accumulated:.2f}")
        print(f"   Hours Remaining: {results['hours_remaining']:.2f}")

        return results

    def _measure_play_quality(self, player: CoherenceAgent, duration: float) -> float:
        """
        Measure quality of play session
        Based on player's tau_k and coherence
        """
        # Base quality from tau_k (higher tau_k = better focus)
        base_quality = player.tau_k / 10.0

        # Coherence bonus
        coherence_bonus = player.coherence * 0.2

        # Random variation (session to session differences)
        variation = np.random.normal(0, 0.1)

        quality = base_quality + coherence_bonus + variation

        # Clamp to [0, 1]
        return np.clip(quality, 0.0, 1.0)

    # ========================================================================
    # PTO LIFECYCLE - STAGE 5: COMPLETION (ACI EVALUATION + DISTRIBUTION)
    # ========================================================================

    def complete_pto(self, pto_id: str) -> Dict:
        """
        PTO completes: ACI evaluates and distributes xUSD yields

        This is the final settlement:
        1. ACI evaluates game quality (coherence score)
        2. xUSD pool minted based on score
        3. Distributed pro-rata to all PTS holders
        4. Quality bonuses applied

        Args:
            pto_id: Which PTO to complete

        Returns:
            Distribution results
        """

        pto = self.ptos.get(pto_id)
        if not pto:
            return {'error': 'Invalid PTO'}

        # ACI Coherence Evaluation
        aci_score = self._aci_evaluate(pto)
        pto.aci_coherence_score = aci_score

        # Mint xUSD pool
        xUSD_pool = aci_score * pto.funding_raised * self.BASE_YIELD_MULTIPLIER
        pto.xUSD_pool = xUSD_pool

        self.xUSD_minted += xUSD_pool

        # Distribute to all PTS holders
        distribution_results = {}

        for player_id, pts in pto.investors.items():
            player = self.players[player_id]

            # Base payout (pro-rata share)
            player_share = pts.purchase_price / pto.funding_raised
            base_payout = xUSD_pool * player_share

            # Quality bonus (from accumulated play xUSD)
            quality_bonus = pts.xUSD_accumulated

            # Total payout
            total_payout = base_payout + quality_bonus

            # Transfer xUSD to player
            player.xUSD_balance += total_payout

            # Calculate ROI
            roi = ((total_payout - pts.purchase_price) / pts.purchase_price) * 100

            distribution_results[player_id] = {
                'invested': pts.purchase_price,
                'base_payout': base_payout,
                'quality_bonus': quality_bonus,
                'total_payout': total_payout,
                'roi': roi,
                'hours_played': pts.hours_played,
                'hours_committed': pts.hours_committed
            }

        pto.status = PTOStatus.COMPLETED
        pto.completion_time = time.time()

        # Print report
        print(f"\n{'='*70}")
        print(f"🎊 PTO COMPLETED: {pto.game_name}")
        print(f"{'='*70}")
        print(f"\n📊 ACI EVALUATION")
        print(f"   Coherence Score: {aci_score:.3f}")
        print(f"   xUSD Pool Minted: {xUSD_pool:,.2f}")
        print(f"\n💰 DISTRIBUTION")

        for player_id, results in distribution_results.items():
            print(f"\n   Player: {player_id}")
            print(f"   Invested: {results['invested']:.2f} USD-OBBBA")
            print(f"   Base Payout: {results['base_payout']:.2f} xUSD")
            print(f"   Quality Bonus: {results['quality_bonus']:.2f} xUSD")
            print(f"   Total Payout: {results['total_payout']:.2f} xUSD")
            print(f"   ROI: {results['roi']:.1f}%")
            print(f"   Time: {results['hours_played']:.1f} / {results['hours_committed']:.1f} hours")

        return distribution_results

    def _aci_evaluate(self, pto: PublicTimeOffering) -> float:
        """
        ACI (Artificial Coherence Intelligence) evaluates game quality

        Factors:
        - World CDT spectral density (gameplay coherence)
        - ATU efficiency (did they use time well?)
        - Player engagement (how many played?)
        - Development quality (work CDT coherence)

        Returns:
            Coherence score (0-1)
        """

        # Factor 1: World coherence
        world_coherence = np.tanh(pto.world_cdt.spectral_density() / 1000)

        # Factor 2: ATU efficiency
        atu_efficiency = min(1.0, pto.atu_required / (pto.atu_spent + 1))

        # Factor 3: Player engagement
        total_hours_played = sum(pts.hours_played for pts in pto.investors.values())
        total_hours_committed = sum(pts.hours_committed for pts in pto.investors.values())
        engagement = total_hours_played / (total_hours_committed + 1)

        # Factor 4: Average play quality
        avg_quality = np.mean([
            pts.xUSD_accumulated / (pts.hours_played + 1)
            for pts in pto.investors.values()
        ]) / 100.0

        # Weighted combination
        score = (
            0.4 * world_coherence +
            0.2 * atu_efficiency +
            0.2 * engagement +
            0.2 * avg_quality
        )

        print(f"\n🤖 ACI EVALUATION BREAKDOWN")
        print(f"   World Coherence: {world_coherence:.3f}")
        print(f"   ATU Efficiency: {atu_efficiency:.3f}")
        print(f"   Engagement: {engagement:.3f}")
        print(f"   Avg Quality: {avg_quality:.3f}")
        print(f"   FINAL SCORE: {score:.3f}")

        return score

    # ========================================================================
    # SECONDARY MARKET - PTS TRADING
    # ========================================================================

    def trade_pts(
        self,
        seller_id: str,
        buyer_id: str,
        token_id: str,
        price: float
    ) -> bool:
        """
        Secondary market: trade PTS tokens between players

        Args:
            seller_id: Who's selling
            buyer_id: Who's buying
            token_id: Which PTS token
            price: Trade price in USD-OBBBA

        Returns:
            Success boolean
        """

        seller = self.players.get(seller_id)
        buyer = self.players.get(buyer_id)

        if not seller or not buyer:
            return False

        # Find PTS in seller's portfolio
        pts = None
        for p in seller.pts_portfolio:
            if p.token_id == token_id:
                pts = p
                break

        if not pts:
            print(f"❌ PTS not found in seller's portfolio")
            return False

        if buyer.usd_obbba_balance < price:
            print(f"❌ Buyer insufficient balance")
            return False

        # Execute trade
        seller.pts_portfolio.remove(pts)
        buyer.pts_portfolio.append(pts)

        buyer.usd_obbba_balance -= price
        seller.usd_obbba_balance += price

        pts.holder = buyer_id

        print(f"\n🔄 PTS TRADE")
        print(f"   Seller: {seller_id}")
        print(f"   Buyer: {buyer_id}")
        print(f"   Token: {token_id}")
        print(f"   Price: {price:.2f} USD-OBBBA")
        print(f"   Original Cost: {pts.purchase_price:.2f}")
        print(f"   Seller Profit: {price - pts.purchase_price:.2f}")

        return True

    # ========================================================================
    # ANALYTICS & REPORTING
    # ========================================================================

    def get_pto_status(self, pto_id: str) -> Dict:
        """Get detailed status of a PTO"""
        pto = self.ptos.get(pto_id)
        if not pto:
            return {}

        return {
            'pto_id': pto.pto_id,
            'game_name': pto.game_name,
            'status': pto.status.value,
            'funding': {
                'goal': pto.funding_goal,
                'raised': pto.funding_raised,
                'percentage': 100 * pto.funding_raised / pto.funding_goal if pto.funding_goal > 0 else 0
            },
            'time': {
                'atu_required': pto.atu_required,
                'atu_spent': pto.atu_spent,
                'percentage': 100 * pto.atu_spent / pto.atu_required if pto.atu_required > 0 else 0
            },
            'investors': len(pto.investors),
            'pts_sold': pto.pts_sold,
            'pts_offered': pto.pts_offered,
            'world_coherence': pto.world_cdt.spectral_density(),
            'aci_score': pto.aci_coherence_score,
            'xUSD_pool': pto.xUSD_pool
        }

    def get_player_portfolio(self, player_id: str) -> Dict:
        """Get player's complete portfolio"""
        player = self.players.get(player_id)
        if not player:
            return {}

        return {
            'player_id': player_id,
            'balances': {
                'usd_obbba': player.usd_obbba_balance,
                'xUSD': player.xUSD_balance
            },
            'stats': {
                'tau_k': player.tau_k,
                'coherence': player.coherence,
                'total_play_time': player.total_play_time,
                'quality_score': player.quality_score,
                'phase_locks': player.phase_locks_count
            },
            'investments': [
                {
                    'token_id': pts.token_id,
                    'game_id': pts.game_id,
                    'invested': pts.purchase_price,
                    'hours_committed': pts.hours_committed,
                    'hours_played': pts.hours_played,
                    'xUSD_accumulated': pts.xUSD_accumulated
                }
                for pts in player.pts_portfolio
            ]
        }

    def get_global_stats(self) -> Dict:
        """Get platform-wide statistics"""
        return {
            'ptos_launched': self.total_ptos_launched,
            'investments_made': self.total_investments,
            'time_committed': self.total_time_committed,
            'xUSD_minted': self.xUSD_minted,
            'treasury': self.usd_obbba_treasury,
            'active_players': len(self.players),
            'active_ptos': len([p for p in self.ptos.values() if p.status == PTOStatus.IN_PROGRESS])
        }


# ============================================================================
# DEMO / TESTING
# ============================================================================

def run_complete_pto_demo():
    """
    Demonstrate complete PTO lifecycle:
    1. Creator launches PTO
    2. Players invest time + capital
    3. Creator develops (burns ATUs)
    4. Players play (burn time, earn xUSD)
    5. PTO completes, yields distributed
    """

    print("\n" + "="*70)
    print("🍄 UBLOX - COMPLETE PTO INTEGRATION DEMO")
    print("   Temporal Investment Economy in Action")
    print("="*70)

    # Initialize engine
    engine = UbloxPTOEngine()

    # Register participants
    creator = engine.register_player("alice_creator")
    player1 = engine.register_player("bob_player")
    player2 = engine.register_player("carol_player")
    player3 = engine.register_player("dave_player")

    print(f"\n👥 PARTICIPANTS REGISTERED")
    print(f"   Creator: {creator.player_id} (τₖ={creator.tau_k:.2f})")
    print(f"   Player 1: {player1.player_id} (τₖ={player1.tau_k:.2f})")
    print(f"   Player 2: {player2.player_id} (τₖ={player2.tau_k:.2f})")
    print(f"   Player 3: {player3.player_id} (τₖ={player3.tau_k:.2f})")

    # Stage 1: Launch PTO
    pto = engine.launch_pto(
        creator_id=creator.player_id,
        game_name="Harmonic Caves",
        description="Explore mycelial caves, restore coherence to fractured worlds",
        atu_required=1000,  # 1000 hours of development
        pts_offered=10000,  # 10k time shares
        funding_period_days=30
    )

    # Stage 2: Players invest
    engine.invest_in_pto(pto.pto_id, player1.player_id, hours_committed=100, usd_obbba_amount=500)
    engine.invest_in_pto(pto.pto_id, player2.player_id, hours_committed=50, usd_obbba_amount=250)
    engine.invest_in_pto(pto.pto_id, player3.player_id, hours_committed=200, usd_obbba_amount=1000)

    # Additional investors to reach threshold
    for i in range(5):
        investor = engine.register_player(f"investor_{i}")
        engine.invest_in_pto(pto.pto_id, investor.player_id, hours_committed=50, usd_obbba_amount=250)

    # Stage 3: Development (creator burns ATUs)
    print(f"\n{'='*70}")
    print("🛠️ DEVELOPMENT PHASE")
    print(f"{'='*70}")

    dev_milestones = [
        (200, "Core engine and physics implemented"),
        (200, "World generation and mycelial network"),
        (200, "Player mechanics and phase-lock system"),
        (200, "Tesla wave networking and multiplayer"),
        (200, "Final polish, testing, and optimization")
    ]

    for atus, work in dev_milestones:
        engine.burn_atus(pto.pto_id, atus, work, quality=np.random.uniform(0.7, 0.95))
        time.sleep(0.1)  # Simulate time passing

    # Stage 4: Gameplay (players burn time and earn xUSD)
    print(f"\n{'='*70}")
    print("🎮 GAMEPLAY PHASE")
    print(f"{'='*70}")

    # Simulate multiple play sessions
    for session in range(5):
        print(f"\n--- Session {session + 1} ---")

        # Bob plays (high quality)
        player1.tau_k = 8.5  # Good focus
        engine.play_game(pto.pto_id, player1.player_id, session_duration=10)

        # Carol plays (medium quality)
        player2.tau_k = 7.2
        engine.play_game(pto.pto_id, player2.player_id, session_duration=5)

        # Dave plays (variable quality)
        player3.tau_k = 7.0 + np.random.uniform(-0.5, 0.5)
        engine.play_game(pto.pto_id, player3.player_id, session_duration=15)

        time.sleep(0.1)

    # Stage 5: Completion and distribution
    print(f"\n{'='*70}")
    print("🏁 COMPLETION & DISTRIBUTION")
    print(f"{'='*70}")

    distribution = engine.complete_pto(pto.pto_id)

    # Final reports
    print(f"\n{'='*70}")
    print("📊 FINAL REPORTS")
    print(f"{'='*70}")

    print(f"\n🎮 PTO Status:")
    status = engine.get_pto_status(pto.pto_id)
    print(json.dumps(status, indent=2))

    print(f"\n👤 Player Portfolios:")
    for player_id in [player1.player_id, player2.player_id, player3.player_id]:
        portfolio = engine.get_player_portfolio(player_id)
        print(f"\n{player_id}:")
        print(f"  USD-OBBBA: {portfolio['balances']['usd_obbba']:.2f}")
        print(f"  xUSD: {portfolio['balances']['xUSD']:.2f}")
        print(f"  Play Time: {portfolio['stats']['total_play_time']:.1f} hours")
        print(f"  Quality: {portfolio['stats']['quality_score']:.3f}")

    print(f"\n🌍 Global Stats:")
    stats = engine.get_global_stats()
    print(json.dumps(stats, indent=2))

    print(f"\n{'='*70}")
    print("✅ DEMO COMPLETE")
    print(f"{'='*70}")
    print("\n💡 Key Takeaways:")
    print("   • Time is investable capital (PTOs)")
    print("   • Quality matters (τₖ affects yields)")
    print("   • Game state stored as CDT (coherence field)")
    print("   • Everyone wins with high coherence")
    print("\n🌊 The temporal economy is LIVE! 🌊\n")


if __name__ == "__main__":
    run_complete_pto_demo()
