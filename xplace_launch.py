#!/usr/bin/env python3
"""
xplace Network Launcher

Start your own xplace node and join the distributed game network.
No KYC. No central authority. Pure resonance.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from xplace_distributed import XPlaceNode, GameManifest
import numpy as np


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

PRESETS = {
    'seed': {
        'description': 'Seed node - first node in a new network',
        'port': 6565,
        'tau_k': 8.0,
        'bootstrap': []
    },
    'standard': {
        'description': 'Standard node - connects to main network',
        'port': 6566,
        'tau_k': 7.5,
        'bootstrap': [('127.0.0.1', 6565)]  # Local seed for testing
    },
    'high-coherence': {
        'description': 'High coherence node - prioritizes quality games',
        'port': 6567,
        'tau_k': 8.7,
        'bootstrap': [('127.0.0.1', 6565)]
    },
    'explorer': {
        'description': 'Explorer node - lower coherence, broader discovery',
        'port': 6568,
        'tau_k': 6.0,
        'bootstrap': [('127.0.0.1', 6565)]
    }
}


# ============================================================================
# DEMO GAMES
# ============================================================================

def get_demo_games():
    """Get demo game manifests"""
    return [
        GameManifest(
            game_id="",
            name="Myco",
            creator_node="",
            description="Mycelial consciousness exploration. Grow networks, form connections, transcend individual awareness into collective coherence.",
            version="0.1.0",
            tau_k=8.5,
            coherence_score=0.89,
            tags=["meditative", "exploration", "mycelial", "consciousness", "growth"],
            dominant_phases=[0.0, np.pi/3, 2*np.pi/3],
            play_style_vector=[0.9, 0.2, 0.3, 0.1, 0.8, 0.2, 0.4, 0.3,
                              0.2, 0.9, 0.1, 0.8, 0.3, 0.5, 0.2, 0.9],
            pto_id="pto_myco",
            pts_price=5.0,
            funding_status=0.35
        ),
        GameManifest(
            game_id="",
            name="Harmonic Caves",
            creator_node="",
            description="Phase-lock roguelike where you explore resonant caverns. Enemies are dissonance patterns - harmonize or perish.",
            version="1.2.0",
            tau_k=8.2,
            coherence_score=0.85,
            tags=["roguelike", "exploration", "harmonic", "procedural"],
            dominant_phases=[0.0, np.pi/4, np.pi/2],
            play_style_vector=[0.9, 0.3, 0.7, 0.2, 0.8, 0.1, 0.6, 0.4,
                              0.3, 0.7, 0.2, 0.8, 0.5, 0.6, 0.4, 0.7],
            pto_id="pto_harmonic_caves",
            pts_price=5.0,
            funding_status=0.67
        ),
        GameManifest(
            game_id="",
            name="Tesla Wave Arena",
            creator_node="",
            description="Multiplayer combat using non-Hertzian longitudinal waves. Phase-lock with teammates to amplify power.",
            version="2.1.0",
            tau_k=7.9,
            coherence_score=0.72,
            tags=["multiplayer", "combat", "tesla", "waves", "arena"],
            dominant_phases=[np.pi, 5*np.pi/4, 3*np.pi/2],
            play_style_vector=[0.3, 0.8, 0.9, 0.7, 0.4, 0.9, 0.8, 0.6,
                              0.7, 0.5, 0.8, 0.3, 0.9, 0.4, 0.7, 0.5],
            pto_id="pto_tesla_arena",
            pts_price=12.0,
            funding_status=1.0
        ),
        GameManifest(
            game_id="",
            name="Coherence Composer",
            creator_node="",
            description="Create music by arranging phase-locked oscillators. Compose in daThiccNOW. Export to temporal frequencies.",
            version="1.0.0",
            tau_k=8.5,
            coherence_score=0.88,
            tags=["creative", "music", "composition", "oscillators"],
            dominant_phases=[0.0, 2*np.pi/3, 4*np.pi/3],
            play_style_vector=[0.7, 0.5, 0.6, 0.4, 0.8, 0.3, 0.7, 0.5,
                              0.6, 0.7, 0.4, 0.8, 0.6, 0.7, 0.5, 0.8],
            pto_id="pto_coherence_composer",
            pts_price=15.0,
            funding_status=0.93
        ),
        GameManifest(
            game_id="",
            name="Dissonance Dash",
            creator_node="",
            description="Fast-paced platformer. Break through coherence barriers with chaotic energy. Embrace the noise.",
            version="2.0.1",
            tau_k=6.3,
            coherence_score=0.43,
            tags=["platformer", "action", "chaotic", "fast-paced"],
            dominant_phases=[np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4],
            play_style_vector=[0.2, 0.9, 0.8, 0.9, 0.3, 0.9, 0.8, 0.9,
                              0.8, 0.3, 0.9, 0.2, 0.8, 0.7, 0.9, 0.3],
            pto_id="pto_dissonance_dash",
            pts_price=8.0,
            funding_status=0.82
        ),
        GameManifest(
            game_id="",
            name="Mycelial Gardens",
            creator_node="",
            description="Tend to a garden of harmonic fungi. Watch them grow through coherent presence. Patience is power.",
            version="0.9.0",
            tau_k=8.7,
            coherence_score=0.91,
            tags=["meditative", "gardening", "fungi", "slow", "presence"],
            dominant_phases=[0.0, np.pi/2, np.pi],
            play_style_vector=[0.9, 0.2, 0.3, 0.1, 0.9, 0.1, 0.3, 0.2,
                              0.2, 0.8, 0.1, 0.9, 0.3, 0.4, 0.2, 0.9],
            pto_id="pto_mycelial_gardens",
            pts_price=3.0,
            funding_status=0.45
        )
    ]


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

async def interactive_mode(node: XPlaceNode):
    """Run interactive command mode"""

    print("\n" + "="*50)
    print("  xplace Interactive Mode")
    print("  Type 'help' for commands")
    print("="*50 + "\n")

    while True:
        try:
            cmd = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input("xplace> ").strip()
            )
        except EOFError:
            break

        if not cmd:
            continue

        parts = cmd.split()
        command = parts[0].lower()

        if command == 'help':
            print("""
Commands:
  discover [tau]    - Discover games matching coherence level (default: your τₖ)
  games             - List all known games
  peers             - List known peers
  stats             - Show network statistics
  publish           - Publish a new game (interactive)
  search <query>    - Search games by text
  info <game_id>    - Show detailed game info
  quit              - Exit
            """)

        elif command == 'discover':
            tau = float(parts[1]) if len(parts) > 1 else node.tau_k
            print(f"\nDiscovering games for τₖ = {tau}...\n")
            results = node.discover_games(user_tau_k=tau)
            if not results:
                print("  No games found")
            else:
                for game, resonance in results:
                    print(f"  {resonance*100:5.1f}% | {game.name}")
                    print(f"         τₖ={game.tau_k}, coherence={game.coherence_score:.0%}")
                    print(f"         {game.description[:60]}...")
                    print()

        elif command == 'games':
            games = node.dht.get_all_local()
            print(f"\nKnown games ({len(games)}):\n")
            for game in games:
                print(f"  [{game.game_id[:8]}] {game.name}")
                print(f"             τₖ={game.tau_k}, v{game.version}")

        elif command == 'peers':
            peers = node.dht.routing_table.get_all_peers()
            print(f"\nKnown peers ({len(peers)}):\n")
            for peer in peers:
                print(f"  [{peer.node_id.hex()}] {peer.host}:{peer.port}")
                print(f"             τₖ={peer.tau_k}, games={peer.games_hosted}")

        elif command == 'stats':
            stats = node.get_network_stats()
            print("\nNetwork Statistics:\n")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        elif command == 'search':
            if len(parts) < 2:
                print("Usage: search <query>")
                continue
            query = ' '.join(parts[1:])
            results = node._search_games({'text': query})
            print(f"\nSearch results for '{query}':\n")
            for game in results:
                print(f"  {game.name} - {game.description[:50]}...")

        elif command in ('quit', 'exit', 'q'):
            break

        else:
            print(f"Unknown command: {command}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='xplace Distributed Node Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --preset seed              Start a seed node
  %(prog)s --preset standard          Start a standard node
  %(prog)s --port 6570 --tau 8.2      Custom configuration
  %(prog)s --demo                     Run demo mode
  %(prog)s --interactive              Interactive command mode
        """
    )

    parser.add_argument('--preset', choices=list(PRESETS.keys()),
                       help='Use a preset configuration')
    parser.add_argument('--port', type=int, default=6565,
                       help='Port to listen on (default: 6565)')
    parser.add_argument('--tau', type=float, default=7.5,
                       help='Node coherence level τₖ (default: 7.5)')
    parser.add_argument('--bootstrap', nargs='+',
                       help='Bootstrap nodes (host:port)')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demo mode with sample games')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start in interactive mode')
    parser.add_argument('--no-publish', action='store_true',
                       help="Don't publish demo games")

    args = parser.parse_args()

    # Apply preset if specified
    if args.preset:
        preset = PRESETS[args.preset]
        print(f"\n Using preset: {args.preset}")
        print(f"   {preset['description']}\n")
        port = preset['port']
        tau_k = preset['tau_k']
        bootstrap = preset['bootstrap']
    else:
        port = args.port
        tau_k = args.tau
        bootstrap = []
        if args.bootstrap:
            for b in args.bootstrap:
                host, bport = b.split(':')
                bootstrap.append((host, int(bport)))

    # Create node
    node = XPlaceNode(port=port, tau_k=tau_k)

    # Add bootstrap nodes
    for host, bport in bootstrap:
        node.add_bootstrap_node(host, bport)

    # Publish demo games
    if args.demo or not args.no_publish:
        print("[INIT] Publishing demo games...")
        for game in get_demo_games():
            node.publish_game(game)
        print(f"[INIT] Published {len(get_demo_games())} games")

    # Run
    async def run():
        if args.interactive:
            # Start node in background, run interactive mode
            asyncio.create_task(node.start())
            await asyncio.sleep(1)  # Let node initialize
            await interactive_mode(node)
            await node.stop()
        else:
            await node.start()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[NODE] Shutting down...")


if __name__ == '__main__':
    main()
