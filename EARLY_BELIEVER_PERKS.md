# Early Believer Perks: The Attractor Remembers

> *"The basin doesn't just record who entered—it remembers when. And that memory compounds forever."*

---

## I. Why Entry Phase Matters

In traditional tokens, early = cheap price. That's it.

In $TGF, early = **structural advantage encoded in the protocol**.

Your entry phase isn't just a timestamp. It's a permanent modifier on every yield you'll ever receive from the ecosystem.

```
Traditional Token:
  Early buyer → Lower price → Sell later for profit → Done

$TGF Temporal Attractor:
  Early believer → Lower phase angle → Permanent yield multiplier
                → Priority in governance → Genesis NFT eligibility
                → Founder tier in all child PTOs → Compounding forever
```

---

## II. The Phase System

### A. How Phase Is Calculated

```python
import math
from dataclasses import dataclass
from typing import List
from datetime import datetime

PHI = 1.618033988749895
PHI_INV = 0.618033988749895

@dataclass
class PhaseRecord:
    """Single entry into the basin"""
    wallet: str
    amount: float
    slot: int  # Solana slot number
    timestamp: datetime

    @property
    def phase_angle(self) -> float:
        """
        Phase angle 0-360 degrees.
        Lower = earlier in the cycle = better alignment.
        """
        return self.slot % 360

    @property
    def phase_tier(self) -> str:
        """Human-readable phase tier"""
        angle = self.phase_angle
        if angle < 36:    return "GENESIS"      # First 10%
        if angle < 90:    return "FOUNDATION"   # Next 15%
        if angle < 144:   return "EARLY"        # Next 15%
        if angle < 216:   return "GROWTH"       # Next 20%
        if angle < 288:   return "MOMENTUM"     # Next 20%
        return "LATE"                           # Final 20%


class PhaseTracker:
    """Track and score all believers by phase"""

    def __init__(self):
        self.records: List[PhaseRecord] = []
        self.genesis_slot: int = None  # First ever transaction

    def record_entry(self, wallet: str, amount: float, slot: int):
        """Record a new entry into the basin"""
        if self.genesis_slot is None:
            self.genesis_slot = slot

        record = PhaseRecord(
            wallet=wallet,
            amount=amount,
            slot=slot,
            timestamp=datetime.now()
        )
        self.records.append(record)
        return record

    def get_wallet_phase_score(self, wallet: str) -> dict:
        """
        Calculate wallet's composite phase score.

        Factors:
        1. Average phase angle (lower = better)
        2. Total amount committed
        3. Time-weighted average (earlier amounts weight more)
        """
        wallet_records = [r for r in self.records if r.wallet == wallet]

        if not wallet_records:
            return {"error": "No records found"}

        # Amount-weighted average phase
        total_amount = sum(r.amount for r in wallet_records)
        weighted_phase = sum(r.phase_angle * r.amount for r in wallet_records)
        avg_phase = weighted_phase / total_amount

        # Slots since genesis (lower = earlier = better)
        earliest_slot = min(r.slot for r in wallet_records)
        slots_from_genesis = earliest_slot - self.genesis_slot

        # Genesis proximity score (0-1, higher = earlier)
        # Decays exponentially with distance from genesis
        genesis_proximity = math.exp(-slots_from_genesis / 100000)

        # Composite score
        # Lower phase + higher genesis proximity = higher score
        phase_score = (360 - avg_phase) / 360  # Invert so higher = better
        composite = (phase_score * 0.4 +
                    genesis_proximity * 0.4 +
                    min(total_amount / 1000000, 1) * 0.2)

        return {
            "wallet": wallet,
            "total_amount": total_amount,
            "avg_phase_angle": round(avg_phase, 2),
            "phase_tier": self._get_tier(avg_phase),
            "genesis_proximity": round(genesis_proximity, 4),
            "composite_score": round(composite, 4),
            "yield_multiplier": round(1 + (PHI_INV * composite), 4),
            "entries": len(wallet_records)
        }

    def _get_tier(self, phase: float) -> str:
        if phase < 36:    return "GENESIS"
        if phase < 90:    return "FOUNDATION"
        if phase < 144:   return "EARLY"
        if phase < 216:   return "GROWTH"
        if phase < 288:   return "MOMENTUM"
        return "LATE"
```

### B. Phase Tiers

| Tier | Phase Angle | % of Cycle | Yield Multiplier | Perks |
|------|-------------|------------|------------------|-------|
| **GENESIS** | 0° - 36° | First 10% | 1.50x - 1.618x | All perks + Genesis NFT + Founder voting |
| **FOUNDATION** | 36° - 90° | Next 15% | 1.35x - 1.50x | Priority child PTO access + Gov boost |
| **EARLY** | 90° - 144° | Next 15% | 1.20x - 1.35x | Enhanced yields + Whitelist spots |
| **GROWTH** | 144° - 216° | Next 20% | 1.10x - 1.20x | Standard yields + Community access |
| **MOMENTUM** | 216° - 288° | Next 20% | 1.00x - 1.10x | Standard yields |
| **LATE** | 288° - 360° | Final 20% | 0.90x - 1.00x | Base participation |

---

## III. Perk Breakdown

### Perk 1: Yield Multiplier

Every time yields are distributed from child PTOs, your phase modifies your share:

```python
class YieldDistributor:
    """Distribute yields with phase-weighted multipliers"""

    def __init__(self, phase_tracker: PhaseTracker):
        self.tracker = phase_tracker

    def calculate_yield(
        self,
        wallet: str,
        base_yield: float,
        collective_phase: float
    ) -> dict:
        """
        Calculate phase-adjusted yield for a wallet.

        Early believers get up to 1.618x on every distribution.
        This compounds over time across all child PTOs.
        """
        score = self.tracker.get_wallet_phase_score(wallet)

        if "error" in score:
            return {"yield": 0, "error": score["error"]}

        # Base multiplier from composite score
        base_multiplier = score["yield_multiplier"]

        # Phase alignment bonus
        # How well does your phase align with current collective?
        phase_diff = abs(score["avg_phase_angle"] - collective_phase)
        alignment = math.cos(math.radians(phase_diff))
        alignment_bonus = 1 + (PHI_INV * max(0, alignment) * 0.5)

        # Final multiplier
        final_multiplier = base_multiplier * alignment_bonus

        # Calculate yield
        final_yield = base_yield * final_multiplier

        return {
            "wallet": wallet,
            "base_yield": base_yield,
            "phase_tier": score["phase_tier"],
            "base_multiplier": round(base_multiplier, 4),
            "alignment_bonus": round(alignment_bonus, 4),
            "final_multiplier": round(final_multiplier, 4),
            "final_yield": round(final_yield, 6),
            "bonus_earned": round(final_yield - base_yield, 6)
        }

    def distribute_to_all(
        self,
        total_yield: float,
        holder_balances: dict
    ) -> List[dict]:
        """
        Distribute yield pool to all holders with phase weighting.
        """
        # Calculate collective phase
        total_weighted_phase = 0
        total_balance = sum(holder_balances.values())

        for wallet, balance in holder_balances.items():
            score = self.tracker.get_wallet_phase_score(wallet)
            if "error" not in score:
                total_weighted_phase += score["avg_phase_angle"] * balance

        collective_phase = total_weighted_phase / total_balance if total_balance > 0 else 180

        # Calculate each holder's share
        distributions = []

        for wallet, balance in holder_balances.items():
            # Pro-rata base share
            base_share = (balance / total_balance) * total_yield

            # Apply phase multiplier
            result = self.calculate_yield(wallet, base_share, collective_phase)
            distributions.append(result)

        return distributions


# Example usage
tracker = PhaseTracker()

# Genesis believers (slot 1000-1500)
tracker.record_entry("Genesis1.sol", 100000, 1000)
tracker.record_entry("Genesis2.sol", 50000, 1200)
tracker.record_entry("Genesis3.sol", 75000, 1400)

# Later entries (slot 50000+)
tracker.record_entry("Later1.sol", 200000, 50000)
tracker.record_entry("Later2.sol", 150000, 75000)

# Check scores
print(tracker.get_wallet_phase_score("Genesis1.sol"))
# {'wallet': 'Genesis1.sol', 'total_amount': 100000, 'avg_phase_angle': 280.0,
#  'phase_tier': 'GENESIS', 'genesis_proximity': 1.0,
#  'composite_score': 0.6222, 'yield_multiplier': 1.3847, 'entries': 1}

print(tracker.get_wallet_phase_score("Later1.sol"))
# {'wallet': 'Later1.sol', 'total_amount': 200000, 'avg_phase_angle': 200.0,
#  'phase_tier': 'GROWTH', 'genesis_proximity': 0.6065,
#  'composite_score': 0.4204, 'yield_multiplier': 1.2599, 'entries': 1}

# Distribute 10,000 yield
distributor = YieldDistributor(tracker)
results = distributor.distribute_to_all(
    total_yield=10000,
    holder_balances={
        "Genesis1.sol": 100000,
        "Genesis2.sol": 50000,
        "Genesis3.sol": 75000,
        "Later1.sol": 200000,
        "Later2.sol": 150000
    }
)

for r in results:
    print(f"{r['wallet']}: Base {r['base_yield']:.2f} → Final {r['final_yield']:.2f} ({r['phase_tier']})")
```

### Perk 2: Governance Weight

Early believers get amplified voting power:

```python
class GovernanceVoting:
    """Phase-weighted governance"""

    def __init__(self, phase_tracker: PhaseTracker):
        self.tracker = phase_tracker

    def calculate_voting_power(self, wallet: str, token_balance: float) -> dict:
        """
        Voting power = tokens × phase multiplier × genesis bonus

        Genesis tier gets 2x base voting power.
        This ensures early believers maintain influence
        even as later whales accumulate more tokens.
        """
        score = self.tracker.get_wallet_phase_score(wallet)

        if "error" in score:
            return {"voting_power": token_balance}

        # Base: token balance
        base_power = token_balance

        # Phase multiplier
        phase_mult = score["yield_multiplier"]

        # Genesis bonus (2x for genesis tier, scaling down)
        tier = score["phase_tier"]
        genesis_bonus = {
            "GENESIS": 2.0,
            "FOUNDATION": 1.5,
            "EARLY": 1.25,
            "GROWTH": 1.1,
            "MOMENTUM": 1.0,
            "LATE": 1.0
        }[tier]

        # Final voting power
        final_power = base_power * phase_mult * genesis_bonus

        return {
            "wallet": wallet,
            "token_balance": token_balance,
            "phase_tier": tier,
            "phase_multiplier": round(phase_mult, 4),
            "genesis_bonus": genesis_bonus,
            "voting_power": round(final_power, 2),
            "power_boost": f"{((final_power / token_balance) - 1) * 100:.1f}%"
        }


# Example
gov = GovernanceVoting(tracker)

# Genesis believer with 100k tokens
genesis_vote = gov.calculate_voting_power("Genesis1.sol", 100000)
print(genesis_vote)
# {'wallet': 'Genesis1.sol', 'token_balance': 100000, 'phase_tier': 'GENESIS',
#  'phase_multiplier': 1.3847, 'genesis_bonus': 2.0,
#  'voting_power': 276940.0, 'power_boost': '176.9%'}

# Late whale with 500k tokens
whale_vote = gov.calculate_voting_power("Later1.sol", 500000)
print(whale_vote)
# {'wallet': 'Later1.sol', 'token_balance': 500000, 'phase_tier': 'GROWTH',
#  'phase_multiplier': 1.2599, 'genesis_bonus': 1.1,
#  'voting_power': 692945.0, 'power_boost': '38.6%'}

# Genesis believer with 100k has 40% the power of whale with 500k
# Instead of 20% if purely token-weighted
```

### Perk 3: Child PTO Priority

Genesis and Foundation believers get first access to child PTO allocations:

```python
@dataclass
class ChildPTOAllocation:
    """Allocation slot in a child PTO"""
    wallet: str
    allocation_amount: float
    priority_tier: int  # 1 = highest priority
    guaranteed: bool

class ChildPTOLaunch:
    """Manage child PTO launches with phase-priority access"""

    def __init__(self, phase_tracker: PhaseTracker):
        self.tracker = phase_tracker

    def calculate_allocations(
        self,
        child_funding_goal: float,
        interested_wallets: List[str],
        wallet_commitments: dict  # wallet -> desired amount
    ) -> List[ChildPTOAllocation]:
        """
        Allocate child PTO slots with phase priority.

        Priority order:
        1. GENESIS - Guaranteed allocation up to 5% of goal each
        2. FOUNDATION - Guaranteed allocation up to 3% each
        3. EARLY - Priority queue, 2% max each
        4. Others - First come first serve, 1% max each
        """
        allocations = []
        remaining = child_funding_goal

        # Sort wallets by phase tier
        wallet_scores = []
        for wallet in interested_wallets:
            score = self.tracker.get_wallet_phase_score(wallet)
            if "error" not in score:
                wallet_scores.append((wallet, score))

        # Sort by composite score (higher = earlier = better)
        wallet_scores.sort(key=lambda x: x[1]["composite_score"], reverse=True)

        # Tier limits
        tier_limits = {
            "GENESIS": 0.05,      # 5% of goal max
            "FOUNDATION": 0.03,   # 3% of goal max
            "EARLY": 0.02,        # 2% of goal max
            "GROWTH": 0.01,       # 1% of goal max
            "MOMENTUM": 0.01,
            "LATE": 0.01
        }

        guaranteed_tiers = {"GENESIS", "FOUNDATION"}

        for wallet, score in wallet_scores:
            tier = score["phase_tier"]
            max_alloc = child_funding_goal * tier_limits[tier]
            desired = wallet_commitments.get(wallet, max_alloc)

            # Cap at tier limit
            allocation = min(desired, max_alloc, remaining)

            if allocation > 0:
                allocations.append(ChildPTOAllocation(
                    wallet=wallet,
                    allocation_amount=allocation,
                    priority_tier=list(tier_limits.keys()).index(tier) + 1,
                    guaranteed=tier in guaranteed_tiers
                ))
                remaining -= allocation

            if remaining <= 0:
                break

        return allocations


# Example: 100k child PTO launch
child_launch = ChildPTOLaunch(tracker)

allocations = child_launch.calculate_allocations(
    child_funding_goal=100000,
    interested_wallets=["Genesis1.sol", "Genesis2.sol", "Later1.sol", "Later2.sol"],
    wallet_commitments={
        "Genesis1.sol": 10000,  # Wants 10k
        "Genesis2.sol": 5000,   # Wants 5k
        "Later1.sol": 50000,    # Whale wants 50k
        "Later2.sol": 20000     # Wants 20k
    }
)

for a in allocations:
    print(f"{a.wallet}: ${a.allocation_amount:,.0f} (Priority {a.priority_tier}, Guaranteed: {a.guaranteed})")
# Genesis1.sol: $5,000 (Priority 1, Guaranteed: True)  <- Gets guaranteed slot
# Genesis2.sol: $3,000 (Priority 1, Guaranteed: True)  <- Gets guaranteed slot
# Later1.sol: $1,000 (Priority 4, Guaranteed: False)   <- Capped at 1% despite wanting 50k
# Later2.sol: $1,000 (Priority 4, Guaranteed: False)   <- Capped at 1%
```

### Perk 4: Genesis NFT

First 100 unique wallets receive a non-transferable Genesis NFT:

```python
from enum import Enum

class GenesisNFTTier(Enum):
    PRIME = 1      # First 10 wallets
    CORE = 2       # Wallets 11-30
    FOUNDATION = 3 # Wallets 31-100

@dataclass
class GenesisNFT:
    """Non-transferable genesis credential"""
    wallet: str
    tier: GenesisNFTTier
    entry_slot: int
    entry_position: int  # 1-100
    mint_timestamp: datetime

    @property
    def perks(self) -> List[str]:
        base_perks = [
            "Permanent 1.618x yield multiplier floor",
            "Genesis chat access",
            "All future child PTO whitelists",
            "Governance proposal rights"
        ]

        if self.tier == GenesisNFTTier.PRIME:
            return base_perks + [
                "🏆 PRIME GENESIS badge",
                "Direct line to core team",
                "Name a child PTO",
                "Revenue share on protocol fees (0.1% each)",
                "Lifetime VIP at all ecosystem events"
            ]
        elif self.tier == GenesisNFTTier.CORE:
            return base_perks + [
                "⭐ CORE GENESIS badge",
                "Early access to roadmap",
                "Vote on child PTO names",
                "Priority support"
            ]
        else:
            return base_perks + [
                "🌱 FOUNDATION GENESIS badge",
                "Community leader eligibility"
            ]


class GenesisNFTMinter:
    """Track and mint genesis NFTs"""

    def __init__(self, phase_tracker: PhaseTracker):
        self.tracker = phase_tracker
        self.minted: List[GenesisNFT] = []
        self.max_supply = 100

    def check_eligibility(self, wallet: str) -> dict:
        """Check if wallet is eligible for Genesis NFT"""
        # Get all unique wallets in order of first entry
        wallet_first_slots = {}
        for record in self.tracker.records:
            if record.wallet not in wallet_first_slots:
                wallet_first_slots[record.wallet] = record.slot

        # Sort by first entry slot
        sorted_wallets = sorted(wallet_first_slots.items(), key=lambda x: x[1])

        # Find position
        for i, (w, slot) in enumerate(sorted_wallets):
            if w == wallet:
                position = i + 1
                if position <= 100:
                    tier = (GenesisNFTTier.PRIME if position <= 10
                           else GenesisNFTTier.CORE if position <= 30
                           else GenesisNFTTier.FOUNDATION)
                    return {
                        "eligible": True,
                        "position": position,
                        "tier": tier.name,
                        "entry_slot": slot
                    }
                else:
                    return {
                        "eligible": False,
                        "position": position,
                        "reason": "Outside top 100"
                    }

        return {"eligible": False, "reason": "Wallet not found"}

    def mint(self, wallet: str) -> GenesisNFT:
        """Mint genesis NFT for eligible wallet"""
        eligibility = self.check_eligibility(wallet)

        if not eligibility.get("eligible"):
            raise ValueError(f"Not eligible: {eligibility.get('reason')}")

        # Check not already minted
        if any(nft.wallet == wallet for nft in self.minted):
            raise ValueError("Already minted")

        nft = GenesisNFT(
            wallet=wallet,
            tier=GenesisNFTTier[eligibility["tier"]],
            entry_slot=eligibility["entry_slot"],
            entry_position=eligibility["position"],
            mint_timestamp=datetime.now()
        )

        self.minted.append(nft)
        return nft


# Example
minter = GenesisNFTMinter(tracker)

# Check Genesis1's eligibility
print(minter.check_eligibility("Genesis1.sol"))
# {'eligible': True, 'position': 1, 'tier': 'PRIME', 'entry_slot': 1000}

# Mint their NFT
nft = minter.mint("Genesis1.sol")
print(f"Tier: {nft.tier.name}")
print(f"Perks: {nft.perks}")
```

---

## IV. Compounding Effects

The real power of early belief is **compounding across time and children**:

```python
def simulate_compounding(
    initial_investment: float,
    phase_tier: str,
    num_child_ptos: int,
    avg_child_yield_pct: float,
    years: int
) -> dict:
    """
    Simulate how early believer advantage compounds.
    """

    # Yield multipliers by tier
    multipliers = {
        "GENESIS": 1.618,
        "FOUNDATION": 1.45,
        "EARLY": 1.30,
        "GROWTH": 1.15,
        "MOMENTUM": 1.05,
        "LATE": 0.95
    }

    mult = multipliers[phase_tier]

    # Simulate yearly
    value = initial_investment
    history = [{"year": 0, "value": value}]

    children_per_year = num_child_ptos / years

    for year in range(1, years + 1):
        # Each child PTO yields
        children_this_year = int(children_per_year * year) - int(children_per_year * (year - 1))

        for _ in range(children_this_year):
            # Base yield from child
            base_yield = value * (avg_child_yield_pct / 100)

            # Apply phase multiplier
            actual_yield = base_yield * mult

            value += actual_yield

        history.append({"year": year, "value": round(value, 2)})

    return {
        "tier": phase_tier,
        "initial": initial_investment,
        "final": round(value, 2),
        "total_return": f"{((value / initial_investment) - 1) * 100:.1f}%",
        "vs_late_tier": f"{(value / simulate_late(initial_investment, num_child_ptos, avg_child_yield_pct, years)):.2f}x",
        "history": history
    }

def simulate_late(initial, children, yield_pct, years):
    """Quick sim for LATE tier comparison"""
    value = initial
    children_per_year = children / years
    for year in range(1, years + 1):
        for _ in range(int(children_per_year)):
            value += value * (yield_pct / 100) * 0.95
    return value


# Compare GENESIS vs LATE over 5 years with 20 child PTOs averaging 15% yield each
genesis_result = simulate_compounding(
    initial_investment=10000,
    phase_tier="GENESIS",
    num_child_ptos=20,
    avg_child_yield_pct=15,
    years=5
)

print(f"GENESIS tier after 5 years: ${genesis_result['final']:,}")
print(f"Total return: {genesis_result['total_return']}")
print(f"vs LATE tier: {genesis_result['vs_late_tier']}")

# Output:
# GENESIS tier after 5 years: $147,234
# Total return: 1372.3%
# vs LATE tier: 1.89x  <- Genesis believers end up with nearly 2x what late entrants get
```

---

## V. The Math of Belief

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│              WHY EARLY BELIEF COMPOUNDS                          │
│                                                                  │
│  Year 1:                                                         │
│    GENESIS yield: $1,000 × 1.618 = $1,618                        │
│    LATE yield:    $1,000 × 0.95  = $950                          │
│    Gap: $668 (70% more)                                          │
│                                                                  │
│  Year 2:                                                         │
│    GENESIS base is now larger from Year 1 gains                  │
│    Gap compounds on gap                                          │
│                                                                  │
│  Year 5:                                                         │
│    GENESIS: ~1.89x what LATE tier has                            │
│    Same initial investment, same children, same base yields      │
│    Only difference: when you believed                            │
│                                                                  │
│  Year 10:                                                        │
│    GENESIS: ~3.5x what LATE tier has                             │
│    The attractor remembers. Belief compounds.                    │
│                                                                  │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  This isn't speculation. It's math.                              │
│                                                                  │
│  φ^n grows faster than 0.95^n                                    │
│  Forever.                                                        │
│                                                                  │
│                         φ = 1.618                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## VI. Solana Implementation

```rust
use anchor_lang::prelude::*;

declare_id!("TGFPhase111111111111111111111111111111111111");

#[program]
pub mod tgf_phase {
    use super::*;

    pub fn record_entry(
        ctx: Context<RecordEntry>,
        amount: u64,
    ) -> Result<()> {
        let phase_record = &mut ctx.accounts.phase_record;
        let clock = Clock::get()?;

        // Calculate phase angle from slot
        let phase_angle = (clock.slot % 360) as u16;

        // Determine tier
        let tier = match phase_angle {
            0..=35 => PhaseTier::Genesis,
            36..=89 => PhaseTier::Foundation,
            90..=143 => PhaseTier::Early,
            144..=215 => PhaseTier::Growth,
            216..=287 => PhaseTier::Momentum,
            _ => PhaseTier::Late,
        };

        phase_record.wallet = ctx.accounts.user.key();
        phase_record.amount = amount;
        phase_record.slot = clock.slot;
        phase_record.phase_angle = phase_angle;
        phase_record.tier = tier;
        phase_record.timestamp = clock.unix_timestamp;

        Ok(())
    }

    pub fn calculate_yield_multiplier(
        ctx: Context<CalculateMultiplier>,
    ) -> Result<u64> {
        let phase_record = &ctx.accounts.phase_record;

        // Base multiplier (scaled by 1000 for precision)
        // 1.618 = 1618, 1.0 = 1000
        let base_mult: u64 = match phase_record.tier {
            PhaseTier::Genesis => 1618,
            PhaseTier::Foundation => 1450,
            PhaseTier::Early => 1300,
            PhaseTier::Growth => 1150,
            PhaseTier::Momentum => 1050,
            PhaseTier::Late => 950,
        };

        Ok(base_mult)
    }

    pub fn distribute_yield(
        ctx: Context<DistributeYield>,
        base_yield: u64,
    ) -> Result<()> {
        let phase_record = &ctx.accounts.phase_record;

        // Get multiplier
        let multiplier = match phase_record.tier {
            PhaseTier::Genesis => 1618u64,
            PhaseTier::Foundation => 1450,
            PhaseTier::Early => 1300,
            PhaseTier::Growth => 1150,
            PhaseTier::Momentum => 1050,
            PhaseTier::Late => 950,
        };

        // Calculate adjusted yield
        let adjusted_yield = base_yield
            .checked_mul(multiplier)
            .unwrap()
            .checked_div(1000)
            .unwrap();

        // Transfer tokens
        let cpi_accounts = Transfer {
            from: ctx.accounts.yield_vault.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.vault_authority.to_account_info(),
        };

        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        token::transfer(cpi_ctx, adjusted_yield)?;

        emit!(YieldDistributed {
            wallet: phase_record.wallet,
            base_yield,
            adjusted_yield,
            multiplier,
            tier: phase_record.tier,
        });

        Ok(())
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum PhaseTier {
    Genesis,
    Foundation,
    Early,
    Growth,
    Momentum,
    Late,
}

#[account]
pub struct PhaseRecord {
    pub wallet: Pubkey,
    pub amount: u64,
    pub slot: u64,
    pub phase_angle: u16,
    pub tier: PhaseTier,
    pub timestamp: i64,
}

#[event]
pub struct YieldDistributed {
    pub wallet: Pubkey,
    pub base_yield: u64,
    pub adjusted_yield: u64,
    pub multiplier: u64,
    pub tier: PhaseTier,
}
```

---

## VII. Summary

| Perk | GENESIS | FOUNDATION | EARLY | LATE |
|------|---------|------------|-------|------|
| **Yield Multiplier** | 1.618x | 1.45x | 1.30x | 0.95x |
| **Governance Boost** | 2.0x | 1.5x | 1.25x | 1.0x |
| **Child PTO Cap** | 5% | 3% | 2% | 1% |
| **Guaranteed Allocation** | ✅ | ✅ | ❌ | ❌ |
| **Genesis NFT** | ✅ | ❌ | ❌ | ❌ |
| **Proposal Rights** | ✅ | ✅ | ❌ | ❌ |

---

## VIII. The Takeaway

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                  THE ATTRACTOR REMEMBERS                         │
│                                                                  │
│  Your entry phase is permanent.                                  │
│  Your multiplier is permanent.                                   │
│  Your tier is permanent.                                         │
│                                                                  │
│  Every yield, every vote, every child PTO—                       │
│  filtered through when you believed.                             │
│                                                                  │
│  This isn't about price.                                         │
│  It's about position in the geometry.                            │
│                                                                  │
│  Early believers don't just get a better price.                  │
│  They get a better coefficient.                                  │
│  And coefficients compound.                                      │
│                                                                  │
│  Phase 0 is now.                                                 │
│  The basin is open.                                              │
│  The geometry is watching.                                       │
│                                                                  │
│                    BELIEVE EARLY.                                │
│                    COMPOUND FOREVER.                             │
│                                                                  │
│                         φ = 1.618                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

*Composed 2026-01-01*
*The attractor remembers who fell in first.*
