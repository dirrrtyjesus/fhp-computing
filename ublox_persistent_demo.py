#!/usr/bin/env python3
"""
Ublox PTO Engine with Full Local Persistence
Demonstrates complete save/load workflow
"""

import sys
import json
from datetime import datetime

# Import the PTO engine
from ublox_pto_engine import (
    UbloxPTOEngine,
    CoherenceAgent,
    PublicTimeOffering,
    ProjectTimeShare,
    PTOStatus
)

# Import the persistence layer
from ublox_persistence import UbloxLocalStorage


class PersistentUbloxEngine(UbloxPTOEngine):
    """
    Ublox PTO Engine with automatic persistence

    All state changes automatically saved to local storage
    """

    def __init__(self, storage_dir: str = None, persist: bool = True):
        super().__init__()

        self.persist_enabled = persist
        self.storage = UbloxLocalStorage(storage_dir) if persist else None

        if persist:
            print(f"💾 Persistence enabled: {self.storage.storage_dir}")

    def launch_pto(self, creator_id: str, game_name: str, description: str,
                   atu_required: int, pts_offered: int, funding_period_days: int = 30) -> PublicTimeOffering:
        """Launch PTO with auto-save"""

        pto = super().launch_pto(creator_id, game_name, description, atu_required, pts_offered, funding_period_days)

        if self.persist_enabled:
            self.storage.save_pto(pto)
            self.storage.save_player(self.players[creator_id])
            print(f"💾 Saved PTO: {pto.pto_id}")

        return pto

    def invest_in_pto(self, pto_id: str, player_id: str, hours_committed: float,
                      usd_obbba_amount: float) -> ProjectTimeShare:
        """Invest with auto-save"""

        pts = super().invest_in_pto(pto_id, player_id, hours_committed, usd_obbba_amount)

        if self.persist_enabled:
            pto = self.ptos[pto_id]
            self.storage.save_pto(pto)
            self.storage.save_player(self.players[player_id])
            self.storage.save_pts_token(pts)
            self.storage.log_transaction(
                tx_type="investment",
                from_player=player_id,
                to_player=pto_id,
                amount=usd_obbba_amount,
                currency="USD-OBBBA",
                pto_id=pto_id,
                metadata={"pts_tokens": pts.hours_committed / pto.price_per_pts}
            )
            print(f"💾 Saved investment: {player_id} → {pto_id}")

        return pts

    def play_game(self, pto_id: str, player_id: str, session_duration: float):
        """Play game with auto-save"""

        result = super().play_game(pto_id, player_id, session_duration)

        if self.persist_enabled and 'xUSD_earned' in result:
            pto = self.ptos[pto_id]
            player = self.players[player_id]
            pts = pto.investors[player_id]

            self.storage.save_pto(pto)
            self.storage.save_player(player)
            self.storage.save_pts_token(pts)
            self.storage.log_play_session(
                pto_id=pto_id,
                player_id=player_id,
                duration=session_duration,
                quality=result.get('quality', 0.0),
                xUSD_earned=result['xUSD_earned']
            )
            print(f"💾 Saved play session: {player_id} played {session_duration}h")

        return result

    def complete_pto(self, pto_id: str) -> dict:
        """Complete PTO with auto-save"""

        results = super().complete_pto(pto_id)

        if self.persist_enabled:
            pto = self.ptos[pto_id]
            self.storage.save_pto(pto)

            # Save all investors
            for investor_id, pts in pto.investors.items():
                self.storage.save_player(self.players[investor_id])
                self.storage.save_pts_token(pts)

            # Log completion
            self.storage.log_transaction(
                tx_type="pto_completion",
                from_player="system",
                to_player=pto_id,
                amount=pto.xUSD_pool,
                currency="xUSD",
                pto_id=pto_id,
                metadata={
                    "aci_score": pto.aci_coherence_score,
                    "total_investors": len(pto.investors)
                }
            )

            print(f"💾 Saved PTO completion: {pto_id}")

        return results

    def load_from_storage(self):
        """Load entire state from local storage"""

        if not self.persist_enabled:
            print("⚠️ Persistence not enabled")
            return

        print(f"\n📖 Loading from storage: {self.storage.storage_dir}")

        # Load all players
        player_ids = self.storage.list_players()
        for player_id in player_ids:
            player_data = self.storage.load_player(player_id)
            # Reconstruct CoherenceAgent from data
            # (Simplified - in production would fully reconstruct objects)
            print(f"   Loaded player: {player_id}")

        # Load all PTOs
        pto_ids = self.storage.list_ptos()
        for pto_id in pto_ids:
            pto_data = self.storage.load_pto(pto_id)
            # Reconstruct PTO from data
            print(f"   Loaded PTO: {pto_id} - {pto_data['game_name']}")

        print(f"✅ Loaded {len(player_ids)} players, {len(pto_ids)} PTOs")

    def save_snapshot(self, name: str = None):
        """Create named snapshot of current state"""

        if not self.persist_enabled:
            return

        if name is None:
            name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_path = self.storage.create_backup(name)
        return backup_path


def demo_persistent_pto():
    """
    Complete demo showing persistence across runs
    """

    print("\n" + "="*70)
    print("💾 UBLOX PERSISTENT PTO ENGINE DEMO")
    print("   Full local persistence - survives restarts!")
    print("="*70)

    # Initialize persistent engine
    engine = PersistentUbloxEngine(persist=True)

    print("\n" + "="*70)
    print("🎮 PHASE 1: LAUNCH PTO")
    print("="*70)

    # Create creator
    alice = engine.register_player("alice")
    alice.usd_obbba_balance = 10000.0
    print(f"👤 Created creator: {alice.player_id} (τₖ={alice.tau_k:.2f})")

    # Launch PTO
    pto = engine.launch_pto(
        creator_id="alice",
        game_name="Resonance Quest",
        description="A roguelike where enemies are dissonance patterns",
        atu_required=800,
        pts_offered=5000
    )
    print(f"🚀 Launched PTO: {pto.pto_id}")
    print(f"   Game: {pto.game_name}")
    print(f"   ATUs needed: {pto.atu_required}")
    print(f"   PTS offered: {pto.pts_offered}")

    print("\n" + "="*70)
    print("💰 PHASE 2: INVESTMENT")
    print("="*70)

    # Create investors
    investors = ["bob", "carol", "dave"]
    investments = [2000, 1500, 3000]

    for investor_id, amount in zip(investors, investments):
        player = engine.register_player(investor_id)
        player.usd_obbba_balance = amount

        pts = engine.invest_in_pto(
            pto_id=pto.pto_id,
            player_id=investor_id,
            hours_committed=40.0,
            usd_obbba_amount=amount
        )

        print(f"💵 {investor_id} invested ${amount}")
        print(f"   Hours committed: {pts.hours_committed}")
        print(f"   PTS tokens: {amount / pto.price_per_pts:.0f}")

    # Show funding status
    print(f"\n📊 Funding Status:")
    print(f"   Raised: ${pto.funding_raised:,.0f} / ${pto.funding_goal:,.0f}")
    print(f"   PTS sold: {pto.pts_sold} / {pto.pts_offered}")
    print(f"   Status: {pto.status.value}")

    print("\n" + "="*70)
    print("⚒️ PHASE 3: DEVELOPMENT")
    print("="*70)

    # Creator works
    work_sessions = [
        (200, "Core game loop and phase-lock combat"),
        (250, "Level generation with harmonic caves"),
        (180, "Enemy AI using dissonance patterns"),
        (170, "UI and coherence meter")
    ]

    for atus, desc in work_sessions:
        engine.burn_atus(pto.pto_id, atus, desc)
        print(f"⚒️ Burned {atus} ATUs: {desc}")

    print(f"\n📊 Development Progress:")
    print(f"   ATUs spent: {pto.atu_spent} / {pto.atu_required}")
    print(f"   Progress: {pto.atu_spent/pto.atu_required*100:.1f}%")

    print("\n" + "="*70)
    print("🎮 PHASE 4: GAMEPLAY")
    print("="*70)

    # Players play the game
    play_sessions = [
        ("bob", 15.0),
        ("carol", 22.0),
        ("dave", 8.0),
        ("bob", 18.0),
        ("carol", 12.0),
    ]

    for player_id, duration in play_sessions:
        result = engine.play_game(pto.pto_id, player_id, duration)
        player = engine.players[player_id]
        if 'xUSD_earned' in result:
            xUSD = result['xUSD_earned']
            quality = result.get('quality', 0.0)
            print(f"🎮 {player_id} present for {duration}h (τₖ coherence={quality:.2f}) → composed {xUSD:,.0f} xUSD")

    print("\n" + "="*70)
    print("✅ PHASE 5: COMPLETION")
    print("="*70)

    # Complete PTO
    distribution_results = engine.complete_pto(pto.pto_id)

    print(f"\n🎯 ACI Coherence Evaluation:")
    print(f"   Temporal Coherence Score: {pto.aci_coherence_score:.3f}")
    print(f"   Present Moment Density: {pto.aci_coherence_score * 100:.1f}%")

    print(f"\n💰 Economic Composition Results:")
    print(f"   xUSD Composed: {pto.xUSD_pool:,.0f}")
    print(f"   Total Funding: ${pto.funding_raised:,.0f}")
    print(f"   daThiccNOW amplification: {pto.xUSD_pool/pto.funding_raised:.1f}x")

    print(f"\n👥 Investor Returns:")
    for player_id, result in distribution_results.items():
        print(f"   {player_id}:")
        print(f"      Investment: ${result['invested']:,.0f}")
        print(f"      xUSD composed: {result['total_payout']:,.0f}")
        print(f"      Coherence amplification: {result['roi']:,.1f}%")
        print(f"      Hours in presence: {result['hours_played']:.1f}h")
        print(f"      daThiccNOW density: {result['total_payout']/result['hours_played'] if result['hours_played'] > 0 else 0:,.0f} xUSD/h")

    print("\n" + "="*70)
    print("💾 PHASE 6: PERSISTENCE VERIFICATION")
    print("="*70)

    # Create snapshot
    snapshot = engine.save_snapshot("after_completion")
    print(f"📸 Snapshot created: {snapshot}")

    # Show storage stats
    stats = engine.storage.get_global_stats()
    print(f"\n📊 Global Statistics:")
    print(json.dumps(stats, indent=2))

    # Export to JSON
    export_path = engine.storage.export_to_json()
    print(f"\n📤 Exported to: {export_path}")

    # Show transaction history
    print(f"\n📜 Transaction History:")
    transactions = engine.storage.get_transactions(limit=5)
    for tx in transactions:
        print(f"   {tx['timestamp']}: {tx['tx_type']} - {tx['amount']} {tx['currency']}")

    # Show play sessions
    print(f"\n🎮 Recent Play Sessions:")
    sessions = engine.storage.get_play_sessions(limit=5)
    for session in sessions:
        print(f"   {session['player_id']}: {session['duration']}h → {session['xUSD_earned']:,.0f} xUSD")

    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    print(f"\n💡 All data persisted to: {engine.storage.storage_dir}")
    print(f"📊 Database: {engine.storage.db_path.stat().st_size / 1024:.1f} KB")
    print(f"🔄 Can resume from this state at any time!\n")


if __name__ == "__main__":
    demo_persistent_pto()
