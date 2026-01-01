#!/usr/bin/env python3
"""
xplace Distributed - The 65th Element, Decentralized

No central authority. No KYC. No gatekeepers.
Games find players through resonance across a peer-to-peer network.

Architecture:
- DHT (Distributed Hash Table) for game listings
- IPFS for game asset storage
- Gossip protocol for node discovery
- Coherence-weighted routing (high τₖ nodes prioritized)
"""

import asyncio
import hashlib
import json
import socket
import struct
import time
import random
import sqlite3
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Set, Tuple, Callable
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np


# ============================================================================
# 369-365 HARMONIC CONSTANTS (Tesla-Earth Constraint)
# ============================================================================

TESLA_CYCLE = 369          # Tesla's vortex number (digital root: 9)
EARTH_CYCLE = 365          # Earth orbital days (digital root: 5)
HARMONIC_GAP = 4           # The tension between ideal and manifest
RATIO_TESLA_EARTH = 369/365  # ≈1.01096 - the elevation factor

# Coherence cycles
BEAT_PERIOD_YEARS = 92.25  # Full Tesla-Earth sync cycle
QUARTERLY_PHASE_DAYS = 91.25  # Phase check interval

# τₖ reference points
TAU_K_TESLA = RATIO_TESLA_EARTH  # 1.01096 - elevated coherence
TAU_K_EARTH = 1.0               # Grounded coherence

# Near-perfect harmonic: 91×369 ≈ 92×365 (error: 0.003%)
HARMONIC_RESONANCE_A = 91  # Tesla cycles
HARMONIC_RESONANCE_B = 92  # Earth cycles

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class NodeID:
    """160-bit node identifier (like Kademlia)"""
    id_bytes: bytes = field(default_factory=lambda: random.randbytes(20))

    def __hash__(self):
        return hash(self.id_bytes)

    def __eq__(self, other):
        return self.id_bytes == other.id_bytes

    def hex(self) -> str:
        return self.id_bytes.hex()[:16]

    def distance(self, other: 'NodeID') -> int:
        """XOR distance metric"""
        return int.from_bytes(
            bytes(a ^ b for a, b in zip(self.id_bytes, other.id_bytes)),
            'big'
        )

    @classmethod
    def from_hex(cls, hex_str: str) -> 'NodeID':
        return cls(bytes.fromhex(hex_str.ljust(40, '0')))

    @classmethod
    def from_content(cls, content: bytes) -> 'NodeID':
        """Content-addressed ID"""
        return cls(hashlib.sha1(content).digest())


@dataclass
class PeerInfo:
    """Information about a peer node"""
    node_id: NodeID
    host: str
    port: int
    tau_k: float = 7.0  # Node's coherence level
    last_seen: float = field(default_factory=time.time)
    games_hosted: int = 0
    uptime_hours: float = 0.0

    def to_dict(self) -> dict:
        return {
            'node_id': self.node_id.hex(),
            'host': self.host,
            'port': self.port,
            'tau_k': self.tau_k,
            'last_seen': self.last_seen,
            'games_hosted': self.games_hosted
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'PeerInfo':
        return cls(
            node_id=NodeID.from_hex(d['node_id']),
            host=d['host'],
            port=d['port'],
            tau_k=d.get('tau_k', 7.0),
            last_seen=d.get('last_seen', time.time()),
            games_hosted=d.get('games_hosted', 0)
        )


@dataclass
class GameManifest:
    """Distributed game listing - stored in DHT"""
    game_id: str  # Content hash of manifest
    name: str
    creator_node: str  # NodeID of creator
    description: str
    version: str
    tau_k: float
    coherence_score: float

    # IPFS CIDs for game content
    asset_cids: List[str] = field(default_factory=list)
    executable_cid: str = ""
    thumbnail_cid: str = ""

    # PTO integration
    pto_id: str = ""
    pts_price: float = 0.0
    funding_status: float = 0.0

    # Discovery metadata
    dominant_phases: List[float] = field(default_factory=list)
    play_style_vector: List[float] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Network stats (updated by gossip)
    seeders: int = 0
    total_downloads: int = 0
    active_players: int = 0

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def content_hash(self) -> str:
        """Generate content-addressed ID"""
        content = f"{self.name}:{self.creator_node}:{self.version}".encode()
        return hashlib.sha256(content).hexdigest()[:32]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'GameManifest':
        return cls(**d)


# ============================================================================
# K-BUCKET ROUTING TABLE (Kademlia-style)
# ============================================================================

class KBucket:
    """Single k-bucket holding up to k peers"""

    def __init__(self, k: int = 20):
        self.k = k
        self.peers: List[PeerInfo] = []

    def add(self, peer: PeerInfo) -> bool:
        """Add peer, return True if added"""
        # Check if already exists
        for i, existing in enumerate(self.peers):
            if existing.node_id == peer.node_id:
                # Move to end (most recently seen)
                self.peers.pop(i)
                self.peers.append(peer)
                return True

        # Add if space available
        if len(self.peers) < self.k:
            self.peers.append(peer)
            return True

        return False

    def get_peers(self) -> List[PeerInfo]:
        return self.peers.copy()


class RoutingTable:
    """Kademlia-style routing table with coherence weighting"""

    def __init__(self, local_id: NodeID, k: int = 20):
        self.local_id = local_id
        self.k = k
        self.buckets: List[KBucket] = [KBucket(k) for _ in range(160)]

    def _bucket_index(self, node_id: NodeID) -> int:
        """Find bucket index for node"""
        distance = self.local_id.distance(node_id)
        if distance == 0:
            return 0
        return distance.bit_length() - 1

    def add_peer(self, peer: PeerInfo) -> bool:
        """Add peer to appropriate bucket"""
        if peer.node_id == self.local_id:
            return False
        idx = self._bucket_index(peer.node_id)
        return self.buckets[idx].add(peer)

    def find_closest(self, target: NodeID, count: int = 20) -> List[PeerInfo]:
        """Find closest peers to target, weighted by coherence"""
        all_peers = []
        for bucket in self.buckets:
            all_peers.extend(bucket.get_peers())

        # Sort by distance, but boost high-coherence nodes
        def sort_key(peer: PeerInfo) -> float:
            distance = peer.node_id.distance(target)
            # Coherence bonus: high τₖ nodes get priority
            coherence_bonus = (peer.tau_k - 5.0) / 10.0  # -0.2 to +0.4
            return distance * (1.0 - coherence_bonus * 0.3)

        all_peers.sort(key=sort_key)
        return all_peers[:count]

    def get_all_peers(self) -> List[PeerInfo]:
        """Get all known peers"""
        peers = []
        for bucket in self.buckets:
            peers.extend(bucket.get_peers())
        return peers


# ============================================================================
# DISTRIBUTED HASH TABLE
# ============================================================================

class DistributedHashTable:
    """DHT for storing game manifests"""

    def __init__(self, local_id: NodeID):
        self.local_id = local_id
        self.local_store: Dict[str, GameManifest] = {}
        self.routing_table = RoutingTable(local_id)

    def store_local(self, manifest: GameManifest):
        """Store manifest locally"""
        key = manifest.game_id or manifest.content_hash()
        manifest.game_id = key
        self.local_store[key] = manifest

    def get_local(self, key: str) -> Optional[GameManifest]:
        """Get from local store"""
        return self.local_store.get(key)

    def get_all_local(self) -> List[GameManifest]:
        """Get all locally stored manifests"""
        return list(self.local_store.values())

    def find_key_holders(self, key: str) -> List[PeerInfo]:
        """Find nodes that should hold this key"""
        key_id = NodeID.from_content(key.encode())
        return self.routing_table.find_closest(key_id)


# ============================================================================
# GOSSIP PROTOCOL
# ============================================================================

@dataclass
class GossipMessage:
    """Message for gossip protocol"""
    msg_type: str  # 'announce', 'query', 'response', 'ping', 'pong'
    sender: dict  # PeerInfo as dict
    payload: dict
    timestamp: float = field(default_factory=time.time)
    ttl: int = 7  # Max hops
    msg_id: str = field(default_factory=lambda: random.randbytes(8).hex())

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'GossipMessage':
        d = json.loads(data.decode())
        return cls(**d)


class GossipProtocol:
    """Gossip-based message propagation"""

    def __init__(self, local_peer: PeerInfo, routing_table: RoutingTable):
        self.local_peer = local_peer
        self.routing_table = routing_table
        self.seen_messages: Set[str] = set()
        self.message_handlers: Dict[str, Callable] = {}
        self.max_seen = 10000

    def register_handler(self, msg_type: str, handler: Callable):
        """Register handler for message type"""
        self.message_handlers[msg_type] = handler

    def create_message(self, msg_type: str, payload: dict) -> GossipMessage:
        """Create new gossip message"""
        return GossipMessage(
            msg_type=msg_type,
            sender=self.local_peer.to_dict(),
            payload=payload
        )

    def should_propagate(self, msg: GossipMessage) -> bool:
        """Check if message should be propagated"""
        if msg.msg_id in self.seen_messages:
            return False
        if msg.ttl <= 0:
            return False
        if time.time() - msg.timestamp > 300:  # 5 min expiry
            return False
        return True

    def receive_message(self, msg: GossipMessage) -> List[Tuple[PeerInfo, GossipMessage]]:
        """Process received message, return forwarding list"""
        if not self.should_propagate(msg):
            return []

        # Mark as seen
        self.seen_messages.add(msg.msg_id)
        if len(self.seen_messages) > self.max_seen:
            # Evict oldest (simple approach)
            self.seen_messages = set(list(self.seen_messages)[-5000:])

        # Update routing table with sender
        sender_peer = PeerInfo.from_dict(msg.sender)
        self.routing_table.add_peer(sender_peer)

        # Handle message
        if msg.msg_type in self.message_handlers:
            self.message_handlers[msg.msg_type](msg)

        # Prepare forwarding
        forward_msg = GossipMessage(
            msg_type=msg.msg_type,
            sender=msg.sender,
            payload=msg.payload,
            timestamp=msg.timestamp,
            ttl=msg.ttl - 1,
            msg_id=msg.msg_id
        )

        # Select peers to forward to (coherence-weighted)
        peers = self.routing_table.get_all_peers()
        # Prefer high coherence nodes
        peers.sort(key=lambda p: p.tau_k, reverse=True)
        forward_peers = peers[:5]  # Forward to top 5

        return [(peer, forward_msg) for peer in forward_peers
                if peer.node_id != sender_peer.node_id]


# ============================================================================
# XPLACE DISTRIBUTED NODE
# ============================================================================

class XPlaceNode:
    """
    A node in the xplace distributed network

    Each node can:
    - Host game manifests in local DHT
    - Seed game assets via IPFS
    - Discover games through resonance matching
    - Participate in gossip protocol
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 6565, tau_k: float = 7.5):
        self.node_id = NodeID()
        self.host = host
        self.port = port
        self.tau_k = tau_k

        self.local_peer = PeerInfo(
            node_id=self.node_id,
            host=host,
            port=port,
            tau_k=tau_k
        )

        self.dht = DistributedHashTable(self.node_id)
        self.gossip = GossipProtocol(self.local_peer, self.dht.routing_table)

        # Network state
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Local storage
        self.storage_path = Path.home() / '.xplace'
        self.storage_path.mkdir(exist_ok=True)
        self._init_storage()

        # Register gossip handlers
        self._setup_gossip_handlers()

        # Bootstrap nodes (well-known entry points)
        self.bootstrap_nodes: List[Tuple[str, int]] = []

    def _init_storage(self):
        """Initialize local SQLite storage"""
        db_path = self.storage_path / 'xplace.db'
        self.db = sqlite3.connect(str(db_path), check_same_thread=False)
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS peers (
                node_id TEXT PRIMARY KEY,
                host TEXT,
                port INTEGER,
                tau_k REAL,
                last_seen REAL,
                games_hosted INTEGER
            )
        ''')
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                manifest TEXT,
                created_at REAL,
                updated_at REAL
            )
        ''')
        self.db.commit()

    def _setup_gossip_handlers(self):
        """Register handlers for gossip message types"""

        def handle_game_announce(msg: GossipMessage):
            """Handle new game announcement"""
            manifest = GameManifest.from_dict(msg.payload)
            self.dht.store_local(manifest)
            self._save_game(manifest)
            print(f"[GOSSIP] Received game: {manifest.name}")

        def handle_peer_announce(msg: GossipMessage):
            """Handle peer announcement"""
            peer = PeerInfo.from_dict(msg.payload)
            self.dht.routing_table.add_peer(peer)
            self._save_peer(peer)

        def handle_query(msg: GossipMessage):
            """Handle game query"""
            query = msg.payload
            # Search local DHT
            results = self._search_games(query)
            if results:
                # Send response back to querier
                response = self.gossip.create_message('query_response', {
                    'query_id': msg.msg_id,
                    'results': [g.to_dict() for g in results]
                })
                # In real impl, send directly to querier

        self.gossip.register_handler('game_announce', handle_game_announce)
        self.gossip.register_handler('peer_announce', handle_peer_announce)
        self.gossip.register_handler('query', handle_query)

    def _save_peer(self, peer: PeerInfo):
        """Persist peer to database"""
        self.db.execute('''
            INSERT OR REPLACE INTO peers
            (node_id, host, port, tau_k, last_seen, games_hosted)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (peer.node_id.hex(), peer.host, peer.port,
              peer.tau_k, peer.last_seen, peer.games_hosted))
        self.db.commit()

    def _save_game(self, manifest: GameManifest):
        """Persist game to database"""
        self.db.execute('''
            INSERT OR REPLACE INTO games
            (game_id, manifest, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (manifest.game_id, json.dumps(manifest.to_dict()),
              manifest.created_at, manifest.updated_at))
        self.db.commit()

    def _load_peers(self):
        """Load peers from database"""
        cursor = self.db.execute('SELECT * FROM peers')
        for row in cursor:
            peer = PeerInfo(
                node_id=NodeID.from_hex(row[0]),
                host=row[1],
                port=row[2],
                tau_k=row[3],
                last_seen=row[4],
                games_hosted=row[5]
            )
            self.dht.routing_table.add_peer(peer)

    def _load_games(self):
        """Load games from database"""
        cursor = self.db.execute('SELECT manifest FROM games')
        for row in cursor:
            manifest = GameManifest.from_dict(json.loads(row[0]))
            self.dht.store_local(manifest)

    def _search_games(self, query: dict) -> List[GameManifest]:
        """Search local games by criteria"""
        results = []
        for manifest in self.dht.get_all_local():
            # Simple text search
            if 'text' in query:
                text = query['text'].lower()
                if (text in manifest.name.lower() or
                    text in manifest.description.lower()):
                    results.append(manifest)
            # Tag search
            elif 'tags' in query:
                if any(t in manifest.tags for t in query['tags']):
                    results.append(manifest)
            # Coherence range
            elif 'tau_range' in query:
                low, high = query['tau_range']
                if low <= manifest.tau_k <= high:
                    results.append(manifest)
            else:
                results.append(manifest)
        return results

    # ========================================================================
    # NETWORK OPERATIONS
    # ========================================================================

    async def start(self):
        """Start the node"""
        print(f"\n{'='*60}")
        print(f"  xplace Distributed Node")
        print(f"  Node ID: {self.node_id.hex()}")
        print(f"  Address: {self.host}:{self.port}")
        print(f"  Coherence: τₖ = {self.tau_k}")
        print(f"{'='*60}\n")

        self.running = True

        # Load persisted data
        self._load_peers()
        self._load_games()
        print(f"[INIT] Loaded {len(self.dht.routing_table.get_all_peers())} peers")
        print(f"[INIT] Loaded {len(self.dht.get_all_local())} games")

        # Start server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setblocking(False)

        # Bootstrap
        await self._bootstrap()

        # Main loop
        await self._main_loop()

    async def _bootstrap(self):
        """Connect to bootstrap nodes"""
        if not self.bootstrap_nodes:
            print("[BOOTSTRAP] No bootstrap nodes configured - running as seed node")
            return

        print(f"[BOOTSTRAP] Connecting to {len(self.bootstrap_nodes)} nodes...")

        # Announce ourselves to bootstrap nodes
        announce = self.gossip.create_message('peer_announce',
                                               self.local_peer.to_dict())

        for host, port in self.bootstrap_nodes:
            try:
                await self._send_message(host, port, announce)
                print(f"[BOOTSTRAP] Announced to {host}:{port}")
            except Exception as e:
                print(f"[BOOTSTRAP] Failed to reach {host}:{port}: {e}")

    async def _main_loop(self):
        """Main event loop"""
        print("[NODE] Running... Press Ctrl+C to stop")

        loop = asyncio.get_event_loop()

        while self.running:
            try:
                # Check for incoming messages
                try:
                    data, addr = await loop.run_in_executor(
                        None,
                        lambda: self.server_socket.recvfrom(65535)
                    )
                    await self._handle_message(data, addr)
                except BlockingIOError:
                    pass
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Receive error: {e}")

                # Periodic maintenance
                await self._periodic_tasks()

                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except KeyboardInterrupt:
                break

        await self.stop()

    async def _handle_message(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming message"""
        try:
            msg = GossipMessage.from_bytes(data)

            # Process through gossip protocol
            forwards = self.gossip.receive_message(msg)

            # Forward to selected peers
            for peer, fwd_msg in forwards:
                await self._send_message(peer.host, peer.port, fwd_msg)

        except Exception as e:
            print(f"[ERROR] Message handling failed: {e}")

    async def _send_message(self, host: str, port: int, msg: GossipMessage):
        """Send message to peer"""
        try:
            self.server_socket.sendto(msg.to_bytes(), (host, port))
        except Exception as e:
            print(f"[ERROR] Send failed to {host}:{port}: {e}")

    async def _periodic_tasks(self):
        """Run periodic maintenance tasks"""
        # Every 30 seconds, announce ourselves
        if not hasattr(self, '_last_announce') or time.time() - self._last_announce > 30:
            self._last_announce = time.time()
            await self._announce_self()

    async def _announce_self(self):
        """Announce ourselves to known peers"""
        self.local_peer.last_seen = time.time()
        announce = self.gossip.create_message('peer_announce',
                                               self.local_peer.to_dict())

        for peer in self.dht.routing_table.get_all_peers()[:10]:
            await self._send_message(peer.host, peer.port, announce)

    async def stop(self):
        """Stop the node"""
        print("\n[NODE] Shutting down...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.db.close()
        self.executor.shutdown(wait=False)

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def publish_game(self, manifest: GameManifest):
        """Publish a new game to the network"""
        manifest.game_id = manifest.content_hash()
        manifest.creator_node = self.node_id.hex()

        # Store locally
        self.dht.store_local(manifest)
        self._save_game(manifest)

        # Announce to network
        announce = self.gossip.create_message('game_announce', manifest.to_dict())

        # Send to all known peers
        for peer in self.dht.routing_table.get_all_peers():
            asyncio.create_task(
                self._send_message(peer.host, peer.port, announce)
            )

        print(f"[PUBLISH] Game published: {manifest.name} ({manifest.game_id})")
        return manifest.game_id

    def discover_games(self, user_tau_k: float = 7.5, limit: int = 10) -> List[Tuple[GameManifest, float]]:
        """
        Discover games through resonance matching

        Returns: List of (manifest, resonance_score) tuples
        """
        results = []

        for manifest in self.dht.get_all_local():
            # Calculate resonance (simplified from full xplace algorithm)
            tau_diff = abs(user_tau_k - manifest.tau_k)
            tau_score = 1.0 - min(tau_diff / 3.0, 1.0)

            # Coherence bonus
            coherence_bonus = manifest.coherence_score * 0.3

            resonance = tau_score * 0.7 + coherence_bonus
            results.append((manifest, resonance))

        # Sort by resonance
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def add_bootstrap_node(self, host: str, port: int):
        """Add a bootstrap node"""
        self.bootstrap_nodes.append((host, port))

    def get_network_stats(self) -> dict:
        """Get network statistics"""
        peers = self.dht.routing_table.get_all_peers()
        games = self.dht.get_all_local()

        return {
            'node_id': self.node_id.hex(),
            'tau_k': self.tau_k,
            'known_peers': len(peers),
            'hosted_games': len(games),
            'avg_peer_coherence': np.mean([p.tau_k for p in peers]) if peers else 0,
            'total_network_tau': sum(p.tau_k for p in peers)
        }

    def calculate_369_resonance(self, target_tau: float) -> dict:
        """
        Calculate resonance using 369-365 harmonic constraint

        Tesla (369) = ideal harmonic (digital root 9)
        Earth (365) = manifest harmonic (digital root 5)
        Gap (4) = creative tension

        τₖ scale mapping:
          3.65 → Earth-locked (365)
          3.69 → Tesla-elevated (369)
          6.0  → Low coherence
          9.0  → High coherence (approaches Tesla)

        Returns resonance metrics based on Tesla-Earth harmonic relationship.
        """
        # Map τₖ (typically 3.0-9.0) to 365-369 harmonic range
        # τₖ = 3.65 maps to 365 (Earth)
        # τₖ = 3.69 maps to 369 (Tesla)
        # Higher τₖ (6-9) shows stronger Tesla affinity

        # Method: Use digital root and 369/365 ratio
        # τₖ of 9.0 = maximum Tesla affinity
        # τₖ of 5.0 = Earth balance point
        # τₖ of 3.0 = approaching chaos

        # Tesla affinity: how much the value resonates with 369
        # Higher coherence (τₖ > 7) = stronger Tesla resonance
        if target_tau >= 3.65 and target_tau <= 3.69:
            # Direct 365-369 mapping
            tesla_affinity = (target_tau - 3.65) / 0.04
        else:
            # General τₖ scale: 5.0 = Earth, 9.0 = Tesla peak
            tesla_affinity = (target_tau - 5.0) / 4.0  # 5→0, 9→1
        tesla_affinity = max(0, min(1, tesla_affinity))

        # Phase in current 92.25-year cycle
        # Using days since epoch as proxy
        days_since_epoch = time.time() / 86400
        cycle_phase = (days_since_epoch % (BEAT_PERIOD_YEARS * 365)) / (BEAT_PERIOD_YEARS * 365)

        # Quarterly phase check (91.25 days)
        quarterly_phase = (days_since_epoch % QUARTERLY_PHASE_DAYS) / QUARTERLY_PHASE_DAYS

        # Harmonic resonance score
        # Peak resonance when tau aligns with current cycle phase
        phase_alignment = np.cos(2 * np.pi * (tesla_affinity - cycle_phase))
        resonance_score = (phase_alignment + 1) / 2  # Normalize to 0-1

        # Digital root contribution (Tesla's vortex math)
        def digital_root(n):
            while n >= 10:
                n = sum(int(d) for d in str(abs(int(n * 1000))))
            return n

        tau_root = digital_root(target_tau)
        # 9 = highest resonance with Tesla, 5 = Earth resonance
        root_resonance = 1.0 if tau_root == 9 else (0.7 if tau_root in [3, 6] else 0.5)

        return {
            'tau_k': target_tau,
            'tesla_affinity': tesla_affinity,
            'earth_grounding': 1.0 - tesla_affinity,
            'cycle_phase': cycle_phase,
            'quarterly_phase': quarterly_phase,
            'resonance_score': resonance_score,
            'digital_root': tau_root,
            'root_resonance': root_resonance,
            'harmonic_state': 'Tesla-elevated' if tesla_affinity > 0.5 else 'Earth-grounded',
            'days_to_quarterly_check': QUARTERLY_PHASE_DAYS * (1 - quarterly_phase)
        }


# ============================================================================
# IPFS INTEGRATION (Stub - would use actual IPFS in production)
# ============================================================================

class IPFSBridge:
    """
    Bridge to IPFS for game asset storage

    In production, this would use:
    - ipfshttpclient for local node
    - Or web3.storage / Pinata for pinning
    """

    def __init__(self, gateway: str = "http://localhost:5001"):
        self.gateway = gateway
        self.local_cache: Dict[str, bytes] = {}

    async def add(self, data: bytes) -> str:
        """Add content to IPFS, return CID"""
        # Stub: compute CID locally
        cid = "Qm" + hashlib.sha256(data).hexdigest()[:44]
        self.local_cache[cid] = data
        return cid

    async def get(self, cid: str) -> Optional[bytes]:
        """Get content by CID"""
        return self.local_cache.get(cid)

    async def pin(self, cid: str):
        """Pin content to keep it available"""
        pass  # Stub


# ============================================================================
# DEMO / CLI
# ============================================================================

async def run_demo():
    """Run demonstration of distributed xplace"""

    print("\n" + "="*70)
    print("  xplace Distributed - The 65th Element")
    print("  No Central Authority. Pure Resonance.")
    print("="*70 + "\n")

    # Create a node
    node = XPlaceNode(port=6565, tau_k=8.0)

    # Add some demo games
    myco_manifest = GameManifest(
        game_id="",
        name="Myco",
        creator_node="",
        description="Mycelial consciousness exploration. Grow, connect, transcend.",
        version="0.1.0",
        tau_k=8.5,
        coherence_score=0.89,
        tags=["meditative", "exploration", "mycelial", "consciousness"],
        dominant_phases=[0.0, np.pi/3, 2*np.pi/3],
        play_style_vector=[0.9, 0.2, 0.3, 0.1, 0.8, 0.2, 0.4, 0.3,
                          0.2, 0.9, 0.1, 0.8, 0.3, 0.5, 0.2, 0.9]
    )

    harmonic_caves = GameManifest(
        game_id="",
        name="Harmonic Caves",
        creator_node="",
        description="Phase-lock roguelike. Explore resonant caverns.",
        version="1.2.0",
        tau_k=8.2,
        coherence_score=0.85,
        tags=["roguelike", "exploration", "harmonic"],
        dominant_phases=[0.0, np.pi/4, np.pi/2]
    )

    dissonance_dash = GameManifest(
        game_id="",
        name="Dissonance Dash",
        creator_node="",
        description="Fast-paced chaos platformer. Break the coherence.",
        version="2.0.1",
        tau_k=6.3,
        coherence_score=0.43,
        tags=["platformer", "action", "chaotic"]
    )

    # Publish games
    print("[DEMO] Publishing games to local DHT...\n")
    node.publish_game(myco_manifest)
    node.publish_game(harmonic_caves)
    node.publish_game(dissonance_dash)

    # Discover games for different coherence levels
    print("\n" + "-"*50)
    print("Discovery Test: High Coherence User (τₖ = 8.5)")
    print("-"*50)
    results = node.discover_games(user_tau_k=8.5)
    for game, resonance in results:
        print(f"  {resonance*100:5.1f}% | {game.name} (τₖ={game.tau_k})")

    print("\n" + "-"*50)
    print("Discovery Test: Low Coherence User (τₖ = 6.0)")
    print("-"*50)
    results = node.discover_games(user_tau_k=6.0)
    for game, resonance in results:
        print(f"  {resonance*100:5.1f}% | {game.name} (τₖ={game.tau_k})")

    # Network stats
    print("\n" + "-"*50)
    print("Network Statistics")
    print("-"*50)
    stats = node.get_network_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n[DEMO] Starting network node...")
    print("[DEMO] In production, this would connect to the P2P swarm")
    print("[DEMO] Press Ctrl+C to stop\n")

    # Run node (this would normally run indefinitely)
    try:
        await node.start()
    except KeyboardInterrupt:
        await node.stop()


def main():
    """Entry point"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            asyncio.run(run_demo())
        elif sys.argv[1] == '--port':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 6565
            node = XPlaceNode(port=port)
            asyncio.run(node.start())
    else:
        # Default: run demo
        asyncio.run(run_demo())


if __name__ == '__main__':
    main()
