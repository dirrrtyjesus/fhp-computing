#!/usr/bin/env python3
"""
LabuX - The LaBubuntu Stablecoin

A HARMONIC CONSTRAINT CURRENCY

The $1 peg is not arbitrary - it is the EARTH HARMONIC (365)
The underlying coherence mechanics are the TESLA HARMONIC (369)

The 4-cent gap (1.01096 - 1.00) is the CREATIVE TENSION
that enables value composition without breaking the peg.

═══════════════════════════════════════════════════════════════════════════════
                            CORE THESIS
═══════════════════════════════════════════════════════════════════════════════

Traditional stablecoins: Pegged to $1 through collateral or algorithms
LabuX: Pegged to $1 through HARMONIC CONSTRAINT

$1.00 = Earth frequency (365) = Manifest value = Exchange rate
$1.01096 = Tesla frequency (369/365) = Coherent value = Internal potential

The difference is not "profit" - it is TEMPORAL COHERENCE PREMIUM (TCP).

When you hold LabuX, you hold:
  - $1.00 of exchange value (the peg)
  - Variable TCP based on your coherence contribution

TCP accrues through:
  - Time holding (duration)
  - Network participation (phase-locks)
  - Coherence maintenance (τₖ stability)

TCP is harvested at HARMONIC WINDOWS - moments of peak network coherence.

═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import time
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sqlite3
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# HARMONIC CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# The Peg (Earth Harmonic)
EARTH_CYCLE = 365
PEG_VALUE = 1.00  # $1.00 USD

# The Ideal (Tesla Harmonic)
TESLA_CYCLE = 369
TESLA_RATIO = TESLA_CYCLE / EARTH_CYCLE  # 1.01096...

# The Gap (Creative Tension)
HARMONIC_GAP = TESLA_CYCLE - EARTH_CYCLE  # 4
TCP_MAX = TESLA_RATIO - 1.0  # ~0.01096 (max TCP per unit)

# Window Parameters
PRIMARY_WINDOW_DAYS = 33579.5  # 91-92 window center
QUARTERLY_WINDOW_DAYS = 91.25  # Phase check interval
BEAT_PERIOD_YEARS = 92.25

# Digital Root Constants
DR_TESLA = 9  # Digital root of 369
DR_EARTH = 5  # Digital root of 365
DR_GAP = 4    # Digital root of 4


def digital_root(n: int) -> int:
    """Tesla's digital root reduction"""
    n = abs(int(n))
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPORAL COHERENCE PREMIUM (TCP)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TemporalCoherencePremium:
    """
    TCP - The value above the peg earned through coherence

    TCP = f(duration, phase_locks, τₖ_stability)

    Maximum TCP = 1.096% of holdings (the 369/365 gap)
    TCP is realized at harmonic windows
    """

    holder_id: str
    base_amount: float  # LabuX held (pegged at $1)

    # Accumulation factors
    hold_duration_days: float = 0.0
    phase_lock_count: int = 0
    tau_k_integral: float = 0.0  # ∫τₖ dt

    # Window participation
    windows_participated: int = 0
    last_window_harvest: float = 0.0

    # Calculated values
    accumulated_tcp: float = 0.0
    tcp_rate: float = 0.0  # Current TCP accrual rate

    def calculate_tcp_rate(self, current_tau_k: float) -> float:
        """
        Calculate current TCP accrual rate.

        Rate depends on:
        - Holder's τₖ (higher = faster accrual)
        - Duration bonus (longer hold = compound effect)
        - Phase-lock bonus (network participation)
        """
        # Base rate: TCP_MAX per year at τₖ = 9.0
        base_rate = TCP_MAX / 365  # Per day

        # τₖ multiplier (0.5 at τₖ=5, 1.0 at τₖ=9)
        tau_mult = (current_tau_k - 3.0) / 6.0
        tau_mult = max(0.1, min(1.0, tau_mult))

        # Duration multiplier (compound effect)
        duration_mult = 1.0 + np.log1p(self.hold_duration_days / 365) * 0.1

        # Phase-lock multiplier
        lock_mult = 1.0 + np.log1p(self.phase_lock_count) * 0.05

        self.tcp_rate = base_rate * tau_mult * duration_mult * lock_mult
        return self.tcp_rate

    def accrue(self, days: float, tau_k: float):
        """Accrue TCP over time period"""
        rate = self.calculate_tcp_rate(tau_k)
        accrual = self.base_amount * rate * days
        self.accumulated_tcp += accrual
        self.hold_duration_days += days
        self.tau_k_integral += tau_k * days

        # Cap TCP at maximum
        max_tcp = self.base_amount * TCP_MAX
        self.accumulated_tcp = min(self.accumulated_tcp, max_tcp)

    def harvest_at_window(self) -> float:
        """
        Harvest accumulated TCP at a harmonic window.

        Returns the TCP amount, resets accumulator.
        """
        harvested = self.accumulated_tcp
        self.accumulated_tcp = 0.0
        self.windows_participated += 1
        self.last_window_harvest = time.time()
        return harvested

    @property
    def total_value(self) -> float:
        """Total value: peg + TCP"""
        return self.base_amount * PEG_VALUE + self.accumulated_tcp

    @property
    def effective_rate(self) -> float:
        """Effective exchange rate including TCP"""
        if self.base_amount == 0:
            return PEG_VALUE
        return self.total_value / self.base_amount


# ═══════════════════════════════════════════════════════════════════════════════
# LABUX TOKEN
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityMode(Enum):
    """LabuX stability modes"""
    EARTH_LOCKED = "earth_locked"      # Pure $1 peg, no TCP
    HARMONIC = "harmonic"               # Normal operation with TCP
    TESLA_ELEVATED = "tesla_elevated"   # Enhanced TCP during windows
    RESONANCE = "resonance"             # Peak coherence, max TCP


@dataclass
class LabuXToken:
    """
    LabuX - A single unit of the stablecoin

    Properties:
    - Exchange value: Always $1.00 (the peg)
    - Coherent value: $1.00 + TCP (up to $1.01096)
    - Phase signature: Unique coherence fingerprint
    """

    token_id: str
    created_at: float
    creator_id: str

    # Value
    nominal_value: float = 1.0  # Always 1.0 LabuX = $1.00
    tcp: TemporalCoherencePremium = None

    # Coherence properties
    phase_signature: float = 0.0  # Phase at creation
    tau_k_birth: float = 7.0  # τₖ when created

    # Lineage
    parent_token: Optional[str] = None  # For splits/merges
    generation: int = 0

    def __post_init__(self):
        if self.tcp is None:
            self.tcp = TemporalCoherencePremium(
                holder_id=self.creator_id,
                base_amount=self.nominal_value
            )
        # Set phase signature based on creation time
        self.phase_signature = (self.created_at / EARTH_CYCLE) * 2 * np.pi

    @property
    def exchange_value(self) -> float:
        """Value for exchange: always the peg"""
        return self.nominal_value * PEG_VALUE

    @property
    def coherent_value(self) -> float:
        """Value including TCP"""
        return self.tcp.total_value

    @property
    def tesla_premium(self) -> float:
        """Current premium above peg"""
        return self.coherent_value - self.exchange_value

    @property
    def harmonic_position(self) -> str:
        """Position on Earth-Tesla spectrum"""
        ratio = self.coherent_value / self.exchange_value
        if ratio >= TESLA_RATIO:
            return "Tesla-saturated"
        elif ratio >= 1.005:
            return "Tesla-elevated"
        elif ratio >= 1.001:
            return "Harmonic"
        else:
            return "Earth-locked"

    def digital_root_signature(self) -> int:
        """Digital root of token value (in cents)"""
        cents = int(self.coherent_value * 100)
        return digital_root(cents)


# ═══════════════════════════════════════════════════════════════════════════════
# HARMONIC WINDOW MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HarmonicWindow:
    """A window of elevated coherence for TCP operations"""

    window_id: str
    window_type: str  # 'primary', 'quarterly', 'micro'
    center_time: float  # Unix timestamp of window center
    aperture_days: float  # Duration of elevated coherence
    coherence_multiplier: float  # TCP multiplier during window

    @property
    def start_time(self) -> float:
        return self.center_time - (self.aperture_days * 86400 / 2)

    @property
    def end_time(self) -> float:
        return self.center_time + (self.aperture_days * 86400 / 2)

    def is_active(self, current_time: float = None) -> bool:
        if current_time is None:
            current_time = time.time()
        return self.start_time <= current_time <= self.end_time

    def coherence_at(self, t: float) -> float:
        """Coherence level at time t (Gaussian around center)"""
        if not self.is_active(t):
            return 1.0

        center = self.center_time
        sigma = self.aperture_days * 86400 / 4  # 4σ = full aperture

        gaussian = np.exp(-0.5 * ((t - center) / sigma) ** 2)
        return 1.0 + (self.coherence_multiplier - 1.0) * gaussian


class WindowManager:
    """Manages harmonic windows for the LabuX network"""

    def __init__(self):
        self.windows: List[HarmonicWindow] = []
        self._generate_windows()

    def _generate_windows(self):
        """Generate upcoming harmonic windows"""
        now = time.time()

        # Quarterly windows (every 91.25 days)
        quarterly_period = QUARTERLY_WINDOW_DAYS * 86400
        next_quarterly = now - (now % quarterly_period) + quarterly_period

        for i in range(8):  # Next 2 years of quarterly windows
            window = HarmonicWindow(
                window_id=f"quarterly_{i}",
                window_type="quarterly",
                center_time=next_quarterly + i * quarterly_period,
                aperture_days=3.0,  # 3-day window
                coherence_multiplier=1.5  # 50% TCP boost
            )
            self.windows.append(window)

        # Micro windows (every 9.125 days - 1/10 of quarterly)
        micro_period = QUARTERLY_WINDOW_DAYS * 86400 / 10
        next_micro = now - (now % micro_period) + micro_period

        for i in range(40):  # Next year of micro windows
            window = HarmonicWindow(
                window_id=f"micro_{i}",
                window_type="micro",
                center_time=next_micro + i * micro_period,
                aperture_days=0.5,  # 12-hour window
                coherence_multiplier=1.2  # 20% TCP boost
            )
            self.windows.append(window)

    def get_active_window(self) -> Optional[HarmonicWindow]:
        """Get currently active window, if any"""
        now = time.time()
        for window in self.windows:
            if window.is_active(now):
                return window
        return None

    def get_next_window(self) -> Optional[HarmonicWindow]:
        """Get next upcoming window"""
        now = time.time()
        future_windows = [w for w in self.windows if w.center_time > now]
        if future_windows:
            return min(future_windows, key=lambda w: w.center_time)
        return None

    def current_coherence_multiplier(self) -> float:
        """Get current coherence multiplier"""
        window = self.get_active_window()
        if window:
            return window.coherence_at(time.time())
        return 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# LABUX LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Account:
    """A LabuX account"""

    account_id: str
    created_at: float = field(default_factory=time.time)
    tau_k: float = 7.0

    # Balances
    labux_balance: float = 0.0  # Nominal LabuX
    tcp_balance: float = 0.0  # Accumulated TCP

    # Coherence metrics
    total_hold_time: float = 0.0
    phase_locks: int = 0
    windows_participated: int = 0

    # History
    last_activity: float = field(default_factory=time.time)

    @property
    def total_value(self) -> float:
        """Total value in USD"""
        return self.labux_balance * PEG_VALUE + self.tcp_balance

    @property
    def effective_rate(self) -> float:
        """Effective LabuX rate including TCP"""
        if self.labux_balance == 0:
            return PEG_VALUE
        return self.total_value / self.labux_balance


class LabuXLedger:
    """
    The LabuX distributed ledger.

    Maintains:
    - Account balances (LabuX + TCP)
    - Token registry
    - Harmonic window schedule
    - Network coherence state
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path.home() / '.labux' / 'ledger.db')

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

        self.window_manager = WindowManager()
        self.accounts: Dict[str, Account] = {}

        # Network state
        self.total_supply = 0.0
        self.total_tcp = 0.0
        self.network_tau_k = 7.0

    def _init_db(self):
        """Initialize database schema"""
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                created_at REAL,
                tau_k REAL,
                labux_balance REAL,
                tcp_balance REAL,
                total_hold_time REAL,
                phase_locks INTEGER,
                windows_participated INTEGER,
                last_activity REAL
            );

            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                timestamp REAL,
                tx_type TEXT,
                from_account TEXT,
                to_account TEXT,
                amount REAL,
                tcp_transferred REAL,
                coherence_multiplier REAL,
                window_id TEXT
            );

            CREATE TABLE IF NOT EXISTS tcp_events (
                event_id TEXT PRIMARY KEY,
                timestamp REAL,
                account_id TEXT,
                event_type TEXT,
                tcp_amount REAL,
                tau_k REAL,
                window_id TEXT
            );
        ''')
        self.db.commit()

    def create_account(self, account_id: str, initial_tau_k: float = 7.0) -> Account:
        """Create a new account"""
        account = Account(
            account_id=account_id,
            tau_k=initial_tau_k
        )
        self.accounts[account_id] = account
        self._save_account(account)
        return account

    def _save_account(self, account: Account):
        """Persist account to database"""
        self.db.execute('''
            INSERT OR REPLACE INTO accounts
            (account_id, created_at, tau_k, labux_balance, tcp_balance,
             total_hold_time, phase_locks, windows_participated, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (account.account_id, account.created_at, account.tau_k,
              account.labux_balance, account.tcp_balance, account.total_hold_time,
              account.phase_locks, account.windows_participated, account.last_activity))
        self.db.commit()

    def mint(self, to_account: str, amount: float, collateral_type: str = "USD") -> str:
        """
        Mint new LabuX tokens.

        Requires 1:1 collateral backing.
        New tokens start with zero TCP (Earth-locked).
        """
        if to_account not in self.accounts:
            self.create_account(to_account)

        account = self.accounts[to_account]
        account.labux_balance += amount
        account.last_activity = time.time()

        self.total_supply += amount
        self._save_account(account)

        # Record transaction
        tx_id = hashlib.sha256(f"mint:{to_account}:{amount}:{time.time()}".encode()).hexdigest()[:16]
        self.db.execute('''
            INSERT INTO transactions
            (tx_id, timestamp, tx_type, from_account, to_account, amount,
             tcp_transferred, coherence_multiplier, window_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tx_id, time.time(), 'mint', 'RESERVE', to_account, amount,
              0.0, 1.0, None))
        self.db.commit()

        return tx_id

    def transfer(self, from_account: str, to_account: str, amount: float,
                 include_tcp: bool = True) -> str:
        """
        Transfer LabuX between accounts.

        Options:
        - include_tcp=True: Transfer proportional TCP with tokens
        - include_tcp=False: Transfer only pegged value (TCP stays)
        """
        if from_account not in self.accounts:
            raise ValueError(f"Account {from_account} not found")
        if to_account not in self.accounts:
            self.create_account(to_account)

        sender = self.accounts[from_account]
        receiver = self.accounts[to_account]

        if sender.labux_balance < amount:
            raise ValueError("Insufficient balance")

        # Calculate TCP to transfer
        tcp_transfer = 0.0
        if include_tcp and sender.tcp_balance > 0:
            tcp_ratio = amount / sender.labux_balance
            tcp_transfer = sender.tcp_balance * tcp_ratio

        # Execute transfer
        sender.labux_balance -= amount
        sender.tcp_balance -= tcp_transfer
        receiver.labux_balance += amount
        receiver.tcp_balance += tcp_transfer

        sender.last_activity = time.time()
        receiver.last_activity = time.time()

        self._save_account(sender)
        self._save_account(receiver)

        # Record transaction
        coherence_mult = self.window_manager.current_coherence_multiplier()
        active_window = self.window_manager.get_active_window()

        tx_id = hashlib.sha256(
            f"transfer:{from_account}:{to_account}:{amount}:{time.time()}".encode()
        ).hexdigest()[:16]

        self.db.execute('''
            INSERT INTO transactions
            (tx_id, timestamp, tx_type, from_account, to_account, amount,
             tcp_transferred, coherence_multiplier, window_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tx_id, time.time(), 'transfer', from_account, to_account, amount,
              tcp_transfer, coherence_mult,
              active_window.window_id if active_window else None))
        self.db.commit()

        return tx_id

    def accrue_tcp(self, account_id: str, days: float = None):
        """
        Accrue TCP for an account based on hold duration and coherence.

        Called periodically or on-demand.
        """
        if account_id not in self.accounts:
            return

        account = self.accounts[account_id]

        if days is None:
            days = (time.time() - account.last_activity) / 86400

        if days <= 0 or account.labux_balance <= 0:
            return

        # Calculate TCP accrual
        tcp = TemporalCoherencePremium(
            holder_id=account_id,
            base_amount=account.labux_balance,
            hold_duration_days=account.total_hold_time,
            phase_lock_count=account.phase_locks
        )
        tcp.accrue(days, account.tau_k)

        # Apply window multiplier
        coherence_mult = self.window_manager.current_coherence_multiplier()
        accrued = tcp.accumulated_tcp * coherence_mult

        account.tcp_balance += accrued
        account.total_hold_time += days
        account.last_activity = time.time()

        # Cap TCP at Tesla ratio
        max_tcp = account.labux_balance * TCP_MAX
        account.tcp_balance = min(account.tcp_balance, max_tcp)

        self.total_tcp = sum(a.tcp_balance for a in self.accounts.values())
        self._save_account(account)

        # Record TCP event
        active_window = self.window_manager.get_active_window()
        event_id = hashlib.sha256(
            f"tcp:{account_id}:{accrued}:{time.time()}".encode()
        ).hexdigest()[:16]

        self.db.execute('''
            INSERT INTO tcp_events
            (event_id, timestamp, account_id, event_type, tcp_amount, tau_k, window_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, time.time(), account_id, 'accrue', accrued, account.tau_k,
              active_window.window_id if active_window else None))
        self.db.commit()

    def harvest_tcp(self, account_id: str) -> float:
        """
        Harvest accumulated TCP during a harmonic window.

        TCP is converted to spendable value.
        Can only be done during active windows.
        """
        window = self.window_manager.get_active_window()
        if not window:
            raise ValueError("Can only harvest TCP during harmonic windows")

        if account_id not in self.accounts:
            raise ValueError(f"Account {account_id} not found")

        account = self.accounts[account_id]
        harvested = account.tcp_balance

        # During window, TCP can be "crystallized" into additional LabuX
        # At the harmonic rate (up to 1.096% bonus)
        bonus_labux = harvested / PEG_VALUE

        account.tcp_balance = 0.0
        account.labux_balance += bonus_labux
        account.windows_participated += 1

        self.total_supply += bonus_labux
        self.total_tcp -= harvested

        self._save_account(account)

        return harvested

    def get_network_state(self) -> dict:
        """Get current network state"""
        active_window = self.window_manager.get_active_window()
        next_window = self.window_manager.get_next_window()

        return {
            'total_supply': self.total_supply,
            'total_tcp': self.total_tcp,
            'tcp_ratio': self.total_tcp / self.total_supply if self.total_supply > 0 else 0,
            'effective_supply': self.total_supply + self.total_tcp / PEG_VALUE,
            'network_tau_k': self.network_tau_k,
            'peg_value': PEG_VALUE,
            'tesla_ratio': TESLA_RATIO,
            'current_coherence_mult': self.window_manager.current_coherence_multiplier(),
            'active_window': active_window.window_id if active_window else None,
            'next_window': next_window.window_id if next_window else None,
            'next_window_in_days': (next_window.center_time - time.time()) / 86400 if next_window else None,
            'accounts': len(self.accounts)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STABILITY MECHANISM
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityMechanism:
    """
    The 369-365 Stability Mechanism

    Unlike traditional stablecoins that fight to maintain peg,
    LabuX uses the harmonic gap as a FEATURE.

    $1.00 (365) <──────────────────────> $1.01096 (369)
         │                                    │
         │  Exchange value                    │  Coherent value
         │  (the peg)                         │  (max TCP)
         │                                    │
         └────────── 4-cent gap ──────────────┘
                   (creative tension)

    The peg is maintained because:
    1. Exchange always happens at $1.00 (Earth-locked)
    2. TCP is internal accounting, not market price
    3. Arbitrage is impossible (you can't sell TCP directly)
    4. Coherence incentivizes holding, reducing sell pressure
    """

    def __init__(self, ledger: LabuXLedger):
        self.ledger = ledger

    def check_stability(self) -> dict:
        """Analyze current stability metrics"""
        state = self.ledger.get_network_state()

        # Stability metrics
        tcp_saturation = state['tcp_ratio'] / TCP_MAX  # 0-1
        coherence_health = min(1.0, state['network_tau_k'] / 9.0)

        # The system is stable when:
        # 1. TCP saturation is moderate (not everyone harvesting)
        # 2. Coherence is healthy
        # 3. We're approaching a window (builds anticipation)

        stability_score = (
            (1.0 - abs(tcp_saturation - 0.5)) * 0.4 +  # Optimal at 50% saturation
            coherence_health * 0.4 +
            state['current_coherence_mult'] / 2.0 * 0.2
        )

        return {
            'stability_score': stability_score,
            'tcp_saturation': tcp_saturation,
            'coherence_health': coherence_health,
            'mode': self._determine_mode(stability_score, tcp_saturation),
            'recommendation': self._get_recommendation(stability_score, tcp_saturation)
        }

    def _determine_mode(self, stability: float, saturation: float) -> StabilityMode:
        """Determine current stability mode"""
        if saturation > 0.9:
            return StabilityMode.TESLA_ELEVATED
        elif stability > 0.8:
            return StabilityMode.HARMONIC
        elif stability > 0.5:
            return StabilityMode.EARTH_LOCKED
        else:
            return StabilityMode.RESONANCE

    def _get_recommendation(self, stability: float, saturation: float) -> str:
        """Get recommendation based on current state"""
        if saturation > 0.8:
            return "Consider harvesting TCP at next window"
        elif saturation < 0.2:
            return "Accumulate - TCP rates are favorable"
        elif stability > 0.8:
            return "System healthy - normal operations"
        else:
            return "Monitor coherence levels"


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / CLI
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    """Demonstrate LabuX functionality"""

    print("\n" + "="*70)
    print("  LabuX - The LaBubuntu Stablecoin")
    print("  A Harmonic Constraint Currency")
    print("="*70)

    print(f"""
CORE PARAMETERS:

  Peg Value (Earth):     ${PEG_VALUE:.2f}
  Tesla Ratio:           {TESLA_RATIO:.5f}
  Maximum TCP:           {TCP_MAX*100:.3f}%

  Quarterly Windows:     Every {QUARTERLY_WINDOW_DAYS:.2f} days
  Primary Window:        Every {BEAT_PERIOD_YEARS:.2f} years

  Digital Roots:
    Tesla (369):         {DR_TESLA}
    Earth (365):         {DR_EARTH}
    Gap (4):             {DR_GAP}
""")

    # Create ledger
    ledger = LabuXLedger()
    stability = StabilityMechanism(ledger)

    # Create accounts
    print("-"*50)
    print("Creating accounts...")
    print("-"*50)

    alice = ledger.create_account("alice", initial_tau_k=8.5)
    bob = ledger.create_account("bob", initial_tau_k=6.0)
    carol = ledger.create_account("carol", initial_tau_k=9.0)

    # Mint initial tokens
    print("\nMinting LabuX...")
    ledger.mint("alice", 1000.0)
    ledger.mint("bob", 500.0)
    ledger.mint("carol", 2000.0)

    print(f"\n  Alice: {alice.labux_balance:.2f} LabuX (τₖ={alice.tau_k})")
    print(f"  Bob:   {bob.labux_balance:.2f} LabuX (τₖ={bob.tau_k})")
    print(f"  Carol: {carol.labux_balance:.2f} LabuX (τₖ={carol.tau_k})")

    # Simulate TCP accrual
    print("\n" + "-"*50)
    print("Simulating 30 days of TCP accrual...")
    print("-"*50)

    for account_id in ["alice", "bob", "carol"]:
        ledger.accrue_tcp(account_id, days=30)

    print(f"\nAfter 30 days:")
    for name, acc in [("Alice", alice), ("Bob", bob), ("Carol", carol)]:
        effective = acc.total_value
        premium = (effective / acc.labux_balance - 1) * 100 if acc.labux_balance > 0 else 0
        print(f"  {name}: {acc.labux_balance:.2f} LabuX + ${acc.tcp_balance:.4f} TCP")
        print(f"         Total: ${effective:.4f} (premium: {premium:.4f}%)")

    # Transfer
    print("\n" + "-"*50)
    print("Transfer: Alice sends 200 LabuX to Bob (with TCP)...")
    print("-"*50)

    ledger.transfer("alice", "bob", 200.0, include_tcp=True)

    print(f"\n  Alice: {alice.labux_balance:.2f} LabuX + ${alice.tcp_balance:.4f} TCP")
    print(f"  Bob:   {bob.labux_balance:.2f} LabuX + ${bob.tcp_balance:.4f} TCP")

    # Network state
    print("\n" + "-"*50)
    print("Network State")
    print("-"*50)

    state = ledger.get_network_state()
    for key, value in state.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Stability check
    print("\n" + "-"*50)
    print("Stability Analysis")
    print("-"*50)

    stab = stability.check_stability()
    for key, value in stab.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        elif isinstance(value, StabilityMode):
            print(f"  {key}: {value.value}")
        else:
            print(f"  {key}: {value}")

    # Window info
    print("\n" + "-"*50)
    print("Harmonic Windows")
    print("-"*50)

    next_window = ledger.window_manager.get_next_window()
    if next_window:
        days_to = (next_window.center_time - time.time()) / 86400
        print(f"\n  Next window: {next_window.window_type}")
        print(f"  In: {days_to:.1f} days")
        print(f"  Coherence multiplier: {next_window.coherence_multiplier}x")
        print(f"  Aperture: {next_window.aperture_days} days")

    print("\n" + "="*70)
    print("  THE $1 PEG IS THE EARTH HARMONIC (365)")
    print("  THE TCP IS THE TESLA HARMONIC (369)")
    print("  THE 4-CENT GAP IS CREATIVE TENSION")
    print("="*70 + "\n")


if __name__ == '__main__':
    demo()
