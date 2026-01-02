#!/usr/bin/env python3
"""
Ublox Local Persistence Layer
Uses local environment (files) instead of database server

Storage Strategy:
- SQLite for structured data (PTOs, Players, Transactions)
- JSON for CDT states and complex objects
- Pickle for numpy arrays (CDT fields)
- All stored in local .ublox/ directory
"""

import os
import json
import pickle
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil


class UbloxLocalStorage:
    """
    Local file-based persistence for Ublox

    No database server needed!
    Everything stored in ~/.ublox/ directory
    """

    def __init__(self, storage_dir: str = None):
        # Default to ~/.ublox/ in user's home directory
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.ublox")

        self.storage_dir = Path(storage_dir)
        self.db_path = self.storage_dir / "ublox.db"
        self.cdt_dir = self.storage_dir / "cdt_states"
        self.backup_dir = self.storage_dir / "backups"

        # Initialize storage
        self._init_storage()
        self._init_database()

    def _init_storage(self):
        """Create storage directories"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cdt_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        print(f"📁 Ublox storage initialized: {self.storage_dir}")

    def _init_database(self):
        """Initialize SQLite database with schema"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                position_x REAL,
                position_y REAL,
                phase REAL,
                coherence REAL,
                tau_k REAL,
                resonance_freq REAL,
                usd_obbba_balance REAL,
                xUSD_balance REAL,
                total_play_time REAL,
                quality_score REAL,
                phase_locks_count INTEGER,
                memory_depth REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # PTOs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ptos (
                pto_id TEXT PRIMARY KEY,
                game_name TEXT,
                creator_id TEXT,
                description TEXT,
                atu_required INTEGER,
                atu_spent INTEGER,
                pts_offered INTEGER,
                pts_sold INTEGER,
                price_per_pts REAL,
                funding_goal REAL,
                funding_raised REAL,
                status TEXT,
                launch_time TIMESTAMP,
                funding_deadline TIMESTAMP,
                completion_time TIMESTAMP,
                aci_coherence_score REAL,
                xUSD_pool REAL,
                world_cdt_id TEXT,
                FOREIGN KEY (creator_id) REFERENCES players(player_id)
            )
        """)

        # PTS tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pts_tokens (
                token_id TEXT PRIMARY KEY,
                game_id TEXT,
                holder TEXT,
                hours_committed REAL,
                purchase_price REAL,
                hours_played REAL,
                xUSD_accumulated REAL,
                tau_k_at_purchase REAL,
                purchase_time TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES ptos(pto_id),
                FOREIGN KEY (holder) REFERENCES players(player_id)
            )
        """)

        # Transactions log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_type TEXT,
                from_player TEXT,
                to_player TEXT,
                amount REAL,
                currency TEXT,
                pto_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # Play sessions log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS play_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pto_id TEXT,
                player_id TEXT,
                duration REAL,
                quality REAL,
                xUSD_earned REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pto_id) REFERENCES ptos(pto_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        conn.commit()
        conn.close()

        print(f"✅ SQLite database initialized: {self.db_path}")

    # ========================================================================
    # PLAYER PERSISTENCE
    # ========================================================================

    def save_player(self, player: Any) -> bool:
        """Save player to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO players (
                    player_id, position_x, position_y, phase, coherence, tau_k,
                    resonance_freq, usd_obbba_balance, xUSD_balance,
                    total_play_time, quality_score, phase_locks_count, memory_depth
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player.player_id,
                float(player.position[0]),
                float(player.position[1]),
                player.phase,
                player.coherence,
                player.tau_k,
                player.resonance_freq,
                player.usd_obbba_balance,
                player.xUSD_balance,
                player.total_play_time,
                player.quality_score,
                player.phase_locks_count,
                player.memory_depth
            ))

            # Save PTS portfolio separately
            for pts in player.pts_portfolio:
                self.save_pts_token(pts)

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error saving player: {e}")
            return False
        finally:
            conn.close()

    def load_player(self, player_id: str) -> Optional[Dict]:
        """Load player from database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Get column names
        columns = [description[0] for description in cursor.description]
        player_data = dict(zip(columns, row))

        # Load PTS portfolio
        cursor.execute("SELECT * FROM pts_tokens WHERE holder = ?", (player_id,))
        pts_rows = cursor.fetchall()
        pts_columns = [description[0] for description in cursor.description]

        player_data['pts_portfolio'] = [
            dict(zip(pts_columns, pts_row))
            for pts_row in pts_rows
        ]

        conn.close()
        return player_data

    def list_players(self) -> List[str]:
        """List all player IDs"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT player_id FROM players")
        players = [row[0] for row in cursor.fetchall()]

        conn.close()
        return players

    # ========================================================================
    # PTO PERSISTENCE
    # ========================================================================

    def save_pto(self, pto: Any) -> bool:
        """Save PTO to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Save CDT state separately
            cdt_id = f"{pto.pto_id}_world_cdt"
            self.save_cdt(cdt_id, pto.world_cdt)

            cursor.execute("""
                INSERT OR REPLACE INTO ptos (
                    pto_id, game_name, creator_id, description,
                    atu_required, atu_spent, pts_offered, pts_sold,
                    price_per_pts, funding_goal, funding_raised,
                    status, launch_time, funding_deadline, completion_time,
                    aci_coherence_score, xUSD_pool, world_cdt_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pto.pto_id,
                pto.game_name,
                pto.creator_id,
                pto.description,
                pto.atu_required,
                pto.atu_spent,
                pto.pts_offered,
                pto.pts_sold,
                pto.price_per_pts,
                pto.funding_goal,
                pto.funding_raised,
                pto.status.value,
                pto.launch_time,
                pto.funding_deadline,
                pto.completion_time,
                pto.aci_coherence_score,
                pto.xUSD_pool,
                cdt_id
            ))

            # Save investor PTS tokens
            for investor_id, pts in pto.investors.items():
                self.save_pts_token(pts)

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error saving PTO: {e}")
            return False
        finally:
            conn.close()

    def load_pto(self, pto_id: str) -> Optional[Dict]:
        """Load PTO from database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ptos WHERE pto_id = ?", (pto_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        columns = [description[0] for description in cursor.description]
        pto_data = dict(zip(columns, row))

        # Load CDT state
        cdt_id = pto_data['world_cdt_id']
        pto_data['world_cdt'] = self.load_cdt(cdt_id)

        # Load investor PTS tokens
        cursor.execute("SELECT * FROM pts_tokens WHERE game_id = ?", (pto_id,))
        pts_rows = cursor.fetchall()
        pts_columns = [description[0] for description in cursor.description]

        pto_data['investors'] = {}
        for pts_row in pts_rows:
            pts_data = dict(zip(pts_columns, pts_row))
            pto_data['investors'][pts_data['holder']] = pts_data

        conn.close()
        return pto_data

    def list_ptos(self, status: str = None) -> List[str]:
        """List all PTO IDs, optionally filtered by status"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT pto_id FROM ptos WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT pto_id FROM ptos")

        ptos = [row[0] for row in cursor.fetchall()]

        conn.close()
        return ptos

    # ========================================================================
    # PTS TOKEN PERSISTENCE
    # ========================================================================

    def save_pts_token(self, pts: Any) -> bool:
        """Save PTS token"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO pts_tokens (
                    token_id, game_id, holder, hours_committed,
                    purchase_price, hours_played, xUSD_accumulated,
                    tau_k_at_purchase, purchase_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pts.token_id,
                pts.game_id,
                pts.holder,
                pts.hours_committed,
                pts.purchase_price,
                pts.hours_played,
                pts.xUSD_accumulated,
                pts.tau_k_at_purchase,
                pts.purchase_time
            ))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error saving PTS token: {e}")
            return False
        finally:
            conn.close()

    # ========================================================================
    # CDT PERSISTENCE (numpy arrays)
    # ========================================================================

    def save_cdt(self, cdt_id: str, cdt: Any) -> bool:
        """Save CDT state to file (pickle for numpy arrays)"""

        cdt_path = self.cdt_dir / f"{cdt_id}.pkl"

        try:
            cdt_data = {
                'field': cdt.field,
                'phase_space': cdt.phase_space,
                'tau_k': cdt.tau_k,
                'last_update': cdt.last_update
            }

            with open(cdt_path, 'wb') as f:
                pickle.dump(cdt_data, f)

            return True

        except Exception as e:
            print(f"❌ Error saving CDT: {e}")
            return False

    def load_cdt(self, cdt_id: str) -> Optional[Dict]:
        """Load CDT state from file"""

        cdt_path = self.cdt_dir / f"{cdt_id}.pkl"

        if not cdt_path.exists():
            return None

        try:
            with open(cdt_path, 'rb') as f:
                cdt_data = pickle.load(f)
            return cdt_data

        except Exception as e:
            print(f"❌ Error loading CDT: {e}")
            return None

    # ========================================================================
    # TRANSACTION LOGGING
    # ========================================================================

    def log_transaction(
        self,
        tx_type: str,
        from_player: str = None,
        to_player: str = None,
        amount: float = 0.0,
        currency: str = "USD-OBBBA",
        pto_id: str = None,
        metadata: Dict = None
    ) -> bool:
        """Log transaction to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO transactions (
                    tx_type, from_player, to_player, amount,
                    currency, pto_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tx_type,
                from_player,
                to_player,
                amount,
                currency,
                pto_id,
                json.dumps(metadata) if metadata else None
            ))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error logging transaction: {e}")
            return False
        finally:
            conn.close()

    def get_transactions(
        self,
        player_id: str = None,
        pto_id: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get transaction history"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if player_id:
            query += " AND (from_player = ? OR to_player = ?)"
            params.extend([player_id, player_id])

        if pto_id:
            query += " AND pto_id = ?"
            params.append(pto_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        transactions = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return transactions

    # ========================================================================
    # PLAY SESSION LOGGING
    # ========================================================================

    def log_play_session(
        self,
        pto_id: str,
        player_id: str,
        duration: float,
        quality: float,
        xUSD_earned: float
    ) -> bool:
        """Log play session"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO play_sessions (
                    pto_id, player_id, duration, quality, xUSD_earned
                ) VALUES (?, ?, ?, ?, ?)
            """, (pto_id, player_id, duration, quality, xUSD_earned))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ Error logging play session: {e}")
            return False
        finally:
            conn.close()

    def get_play_sessions(
        self,
        player_id: str = None,
        pto_id: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get play session history"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM play_sessions WHERE 1=1"
        params = []

        if player_id:
            query += " AND player_id = ?"
            params.append(player_id)

        if pto_id:
            query += " AND pto_id = ?"
            params.append(pto_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [description[0] for description in cursor.description]
        sessions = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return sessions

    # ========================================================================
    # BACKUP & RESTORE
    # ========================================================================

    def create_backup(self, backup_name: str = None) -> str:
        """Create backup of entire storage"""

        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_path = self.backup_dir / backup_name

        # Copy entire storage directory
        shutil.copytree(self.storage_dir, backup_path,
                       ignore=shutil.ignore_patterns('backups'))

        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from backup"""

        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False

        try:
            # Clear current data
            for item in self.storage_dir.iterdir():
                if item.name != 'backups':
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # Restore from backup
            for item in backup_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, self.storage_dir / item.name)
                else:
                    shutil.copy2(item, self.storage_dir / item.name)

            print(f"✅ Restored from backup: {backup_name}")
            return True

        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False

    def list_backups(self) -> List[str]:
        """List available backups"""

        backups = [d.name for d in self.backup_dir.iterdir() if d.is_dir()]
        return sorted(backups, reverse=True)

    # ========================================================================
    # ANALYTICS & REPORTING
    # ========================================================================

    def get_global_stats(self) -> Dict:
        """Get platform-wide statistics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Player stats
        cursor.execute("SELECT COUNT(*), SUM(usd_obbba_balance), SUM(xUSD_balance) FROM players")
        player_count, total_usd, total_xUSD = cursor.fetchone()
        stats['players'] = {
            'total': player_count,
            'total_usd_obbba': total_usd or 0,
            'total_xUSD': total_xUSD or 0
        }

        # PTO stats
        cursor.execute("SELECT COUNT(*), SUM(funding_raised), SUM(xUSD_pool) FROM ptos")
        pto_count, total_funding, total_xUSD_minted = cursor.fetchone()
        stats['ptos'] = {
            'total': pto_count,
            'total_funding': total_funding or 0,
            'total_xUSD_minted': total_xUSD_minted or 0
        }

        # PTS stats
        cursor.execute("SELECT COUNT(*), SUM(hours_committed), SUM(hours_played) FROM pts_tokens")
        pts_count, total_committed, total_played = cursor.fetchone()
        stats['pts_tokens'] = {
            'total': pts_count,
            'hours_committed': total_committed or 0,
            'hours_played': total_played or 0
        }

        # Transaction stats
        cursor.execute("SELECT COUNT(*), SUM(amount) FROM transactions")
        tx_count, tx_volume = cursor.fetchone()
        stats['transactions'] = {
            'total': tx_count,
            'volume': tx_volume or 0
        }

        conn.close()
        return stats

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def export_to_json(self, output_path: str = None) -> str:
        """Export entire database to JSON"""

        if output_path is None:
            output_path = self.storage_dir / "export.json"

        export_data = {
            'players': [],
            'ptos': [],
            'pts_tokens': [],
            'transactions': []
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Export players
        cursor.execute("SELECT * FROM players")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            export_data['players'].append(dict(zip(columns, row)))

        # Export PTOs
        cursor.execute("SELECT * FROM ptos")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            export_data['ptos'].append(dict(zip(columns, row)))

        # Export PTS tokens
        cursor.execute("SELECT * FROM pts_tokens")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            export_data['pts_tokens'].append(dict(zip(columns, row)))

        # Export transactions
        cursor.execute("SELECT * FROM transactions")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            export_data['transactions'].append(dict(zip(columns, row)))

        conn.close()

        # Write to JSON
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"✅ Exported to JSON: {output_path}")
        return str(output_path)

    def clear_all_data(self, confirm: bool = False) -> bool:
        """Clear all data (dangerous!)"""

        if not confirm:
            print("⚠️ Must confirm to clear all data")
            return False

        # Remove database
        if self.db_path.exists():
            self.db_path.unlink()

        # Remove CDT states
        for cdt_file in self.cdt_dir.iterdir():
            cdt_file.unlink()

        # Reinitialize
        self._init_database()

        print("✅ All data cleared")
        return True


# ============================================================================
# DEMO / TESTING
# ============================================================================

def demo_local_storage():
    """Demonstrate local storage system"""

    print("\n" + "="*70)
    print("📁 UBLOX LOCAL STORAGE DEMO")
    print("   No database server needed!")
    print("="*70)

    # Initialize storage
    storage = UbloxLocalStorage()

    print(f"\n📊 Storage location: {storage.storage_dir}")
    print(f"   Database: {storage.db_path}")
    print(f"   CDT states: {storage.cdt_dir}")
    print(f"   Backups: {storage.backup_dir}")

    # Demo: Save and load player
    print(f"\n{'='*70}")
    print("👤 PLAYER PERSISTENCE")
    print(f"{'='*70}")

    class MockPlayer:
        def __init__(self):
            self.player_id = "alice"
            self.position = np.array([10.5, 20.3])
            self.phase = 1.57
            self.coherence = 0.85
            self.tau_k = 8.2
            self.resonance_freq = 936.0
            self.usd_obbba_balance = 1500.0
            self.xUSD_balance = 250.0
            self.total_play_time = 42.5
            self.quality_score = 0.78
            self.phase_locks_count = 127
            self.memory_depth = 543.2
            self.pts_portfolio = []

    player = MockPlayer()

    print(f"💾 Saving player: {player.player_id}")
    storage.save_player(player)

    print(f"📖 Loading player: {player.player_id}")
    loaded = storage.load_player(player.player_id)
    print(f"   Position: ({loaded['position_x']}, {loaded['position_y']})")
    print(f"   τₖ: {loaded['tau_k']}")
    print(f"   xUSD: {loaded['xUSD_balance']}")

    # Demo: Transactions
    print(f"\n{'='*70}")
    print("💰 TRANSACTION LOGGING")
    print(f"{'='*70}")

    storage.log_transaction(
        tx_type="investment",
        from_player="alice",
        to_player="pto_001",
        amount=500.0,
        currency="USD-OBBBA",
        pto_id="pto_001",
        metadata={"pts_tokens": 100}
    )

    transactions = storage.get_transactions(player_id="alice")
    print(f"📜 Transactions for alice: {len(transactions)}")
    for tx in transactions:
        print(f"   {tx['tx_type']}: {tx['amount']} {tx['currency']}")

    # Demo: Backups
    print(f"\n{'='*70}")
    print("💾 BACKUP & RESTORE")
    print(f"{'='*70}")

    backup_name = storage.create_backup()
    print(f"✅ Backup created: {backup_name}")

    backups = storage.list_backups()
    print(f"📦 Available backups: {len(backups)}")
    for backup in backups:
        print(f"   - {backup}")

    # Demo: Export
    print(f"\n{'='*70}")
    print("📤 EXPORT TO JSON")
    print(f"{'='*70}")

    export_path = storage.export_to_json()
    print(f"✅ Exported to: {export_path}")

    # Demo: Global stats
    print(f"\n{'='*70}")
    print("📊 GLOBAL STATISTICS")
    print(f"{'='*70}")

    stats = storage.get_global_stats()
    print(json.dumps(stats, indent=2))

    print(f"\n{'='*70}")
    print("✅ DEMO COMPLETE")
    print(f"{'='*70}")
    print("\n💡 All data persisted locally - no server needed!")
    print(f"📁 Check {storage.storage_dir} to see files\n")


if __name__ == "__main__":
    demo_local_storage()
