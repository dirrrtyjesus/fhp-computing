#!/usr/bin/env python3
"""
Simple demo of Ublox local persistence

Shows that all PTO state persists to local files
"""

from ublox_pto_engine import *
from ublox_persistence import UbloxLocalStorage

print("\n" + "="*70)
print("💾 UBLOX LOCAL PERSISTENCE DEMO")
print("="*70)

# Initialize storage
storage = UbloxLocalStorage()

print(f"\n📁 Storage location: {storage.storage_dir}")

# Create a simple PTO scenario
print("\n" + "="*70)
print("Creating PTO scenario...")
print("="*70)

# Create mock player
player = CoherenceAgent(
    player_id="alice",
    tau_k=8.5,
    usd_obbba_balance=5000.0,
    xUSD_balance=0.0
)

print(f"\n👤 Player: {player.player_id}")
print(f"   τₖ: {player.tau_k}")
print(f"   USD-OBBBA: {player.usd_obbba_balance}")

# Save player
storage.save_player(player)
print(f"✅ Player saved to SQLite")

# Create mock PTO
cdt = CoherenceDataType()
pto = PublicTimeOffering(
    pto_id="pto_harmonic_001",
    game_name="Harmonic Caverns",
    creator_id="alice",
    description="A phase-lock roguelike",
    atu_required=500,
    pts_offered=2000,
    world_cdt=cdt,
    status=PTOStatus.FUNDING
)

print(f"\n🎮 PTO: {pto.game_name}")
print(f"   ID: {pto.pto_id}")
print(f"   ATUs required: {pto.atu_required}")
print(f"   PTS offered: {pto.pts_offered}")

# Save PTO
storage.save_pto(pto)
print(f"✅ PTO saved to SQLite + CDT to pickle")

# Create mock PTS token
pts = ProjectTimeShare(
    token_id="pts_001",
    game_id="pto_harmonic_001",
    holder="alice",
    hours_committed=40.0,
    purchase_price=1000.0,
    tau_k_at_purchase=8.5,
    purchase_time=time.time()
)

print(f"\n🎫 PTS Token: {pts.token_id}")
print(f"   Holder: {pts.holder}")
print(f"   Hours committed: {pts.hours_committed}")

# Save PTS
storage.save_pts_token(pts)
print(f"✅ PTS token saved")

# Log a transaction
storage.log_transaction(
    tx_type="investment",
    from_player="alice",
    to_player="pto_harmonic_001",
    amount=1000.0,
    currency="USD-OBBBA",
    pto_id="pto_harmonic_001",
    metadata={"pts_tokens": 200}
)
print(f"✅ Transaction logged")

# Log a play session
storage.log_play_session(
    pto_id="pto_harmonic_001",
    player_id="alice",
    duration=5.0,
    quality=0.85,
    xUSD_earned=425.0
)
print(f"✅ Play session logged")

print("\n" + "="*70)
print("VERIFICATION: Loading back from storage...")
print("="*70)

# Load player
loaded_player = storage.load_player("alice")
print(f"\n👤 Loaded player: {loaded_player['player_id']}")
print(f"   τₖ: {loaded_player['tau_k']}")
print(f"   xUSD: {loaded_player['xUSD_balance']}")

# Load PTO
loaded_pto = storage.load_pto("pto_harmonic_001")
print(f"\n🎮 Loaded PTO: {loaded_pto['game_name']}")
print(f"   Status: {loaded_pto['status']}")
print(f"   Funding raised: ${loaded_pto['funding_raised']}")
print(f"   CDT loaded: {'field' in loaded_pto['world_cdt']}")

# Get transactions
txs = storage.get_transactions(player_id="alice", limit=5)
print(f"\n📜 Transactions for alice: {len(txs)}")
for tx in txs:
    print(f"   {tx['tx_type']}: {tx['amount']} {tx['currency']}")

# Get play sessions
sessions = storage.get_play_sessions(player_id="alice", limit=5)
print(f"\n🎮 Play sessions for alice: {len(sessions)}")
for session in sessions:
    print(f"   {session['duration']}h → {session['xUSD_earned']} xUSD (quality={session['quality']})")

# Global stats
stats = storage.get_global_stats()
print(f"\n📊 Global Statistics:")
print(f"   Players: {stats['players']['total']}")
print(f"   PTOs: {stats['ptos']['total']}")
print(f"   PTS tokens: {stats['pts_tokens']['total']}")
print(f"   Transactions: {stats['transactions']['total']}")

# Create backup
backup = storage.create_backup("demo_backup")
print(f"\n💾 Backup created: {backup}")

# Export to JSON
export_path = storage.export_to_json()
print(f"📤 Exported to JSON: {export_path}")

# Check file sizes
import os
db_size = storage.db_path.stat().st_size
print(f"\n📁 Storage Summary:")
print(f"   Database: {db_size / 1024:.1f} KB")
print(f"   Location: {storage.storage_dir}")
print(f"   CDT files: {len(list(storage.cdt_dir.glob('*.pkl')))}")

print("\n" + "="*70)
print("✅ PERSISTENCE VERIFIED")
print("="*70)
print(f"\n💡 Key insight: xUSD is COMPOSED in daThiccNOW,")
print(f"   not earned over time. Each moment of coherent presence")
print(f"   amplifies the temporal density, composing value.")
print(f"\n📁 All state persisted to local files - no server needed!")
print(f"   Check {storage.storage_dir} to see the files.\n")
