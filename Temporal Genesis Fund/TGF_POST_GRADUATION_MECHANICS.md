# $TGF Post-Graduation Mechanics

> What happens when the Temporal Genesis Fund graduates from pump.fun to Raydium

---

## The Graduation Event

**Trigger:** $69,000 market cap on pump.fun bonding curve

```
AUTOMATIC SEQUENCE:
├─ pump.fun creates Raydium AMM liquidity pool
├─ ~$12k SOL + tokens deposited as initial LP
├─ LP tokens BURNED (locked forever, no rug possible)
├─ Trading migrates to Raydium
└─ Real price discovery begins
```

Once graduation occurs, there is no going back. The LP is locked permanently. The attractor becomes self-sustaining.

---

## Treasury Activation

All post-graduation inflows split automatically via the golden ratio:

```
┌─────────────────────────────────────────┐
│         INCOMING CAPITAL                │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌─────▼─────┐
   │  61.8%  │      │   38.2%   │
   │  CORE   │      │ ALLOCATION│
   │TREASURY │      │   POOL    │
   └────┬────┘      └─────┬─────┘
        │                 │
        ▼                 ▼
   Stability &       Seeds Child
   Yield Buffer      PTOs
```

### Core Treasury (61.8%)

The gravitational center of the ecosystem:

| Component | Allocation | Purpose |
|-----------|------------|---------|
| Stability Reserve | 38.2% of core | Market defense, black swan events |
| Emergency Liquidity | 23.6% of core | Rapid response capability |
| Yield Buffer | 38.2% of core | Smoothing yield distributions |

The core treasury is the supermassive anchor. It is never touched except for ecosystem defense.

### Allocation Pool (38.2%)

Seeds child PTO proposals, distributed by inverse-volatility weighting:

| Sector | Allocation | Rationale |
|--------|------------|-----------|
| Infrastructure | 23.6% | Lowest volatility, highest stability |
| AI/ML | 19.1% | Medium-low volatility |
| Climate | 17.0% | Medium volatility |
| DeFi | 15.5% | Medium-high volatility |
| Biotech | 13.8% | High volatility |
| Creative | 11.0% | Highest volatility, highest risk/reward |

**Formula:** `allocation% = (1/volatility) / sum(1/volatility_i)`

Lower volatility sectors receive more capital to ensure ecosystem stability while still funding high-risk innovation.

---

## Child PTO Spawning

```
PROPOSAL → VOTE → SEED → LAUNCH → YIELD RETURN
```

### Governance Timeline

| Period | Governance Model |
|--------|------------------|
| Week 1-4 | Core team selects first 3 child PTOs |
| Week 4+ | Community governance activates |

### Proposal Requirements

To propose a child PTO, submit to `#child-proposals`:

1. **Project Concept** - What are you building?
2. **Funding Goal** - How much SOL/USD needed?
3. **Creator τₖ Evidence** - Track record, prior work, demonstrated coherence
4. **Timeline + Deliverables** - What, when, how

### Voting Mechanics

```python
voting_power = token_balance × phase_multiplier × hold_time_bonus

# Thresholds
approval_threshold = 61.8%  # Golden ratio
voting_duration = 3 days
```

**Phase multipliers boost early believers' governance power:**
- GENESIS tier: 2x governance weight
- Later tiers: proportionally less influence

### Seed Calculation

```python
seed_amount = min(
    funding_goal × 0.382,      # Up to 38.2% of goal
    allocation_pool × 0.10     # Max 10% of pool per child
)
```

This ensures:
- No single child PTO can drain the pool
- Creators must find additional funding (skin in the game)
- Pool regenerates as yields flow back

---

## Yield Cascade Mechanics

When child PTOs complete and generate value, yields cascade back to $TGF holders.

### The Flow

```
CHILD PTO COMPLETES
        │
        ▼
ACI evaluates coherence score (0-1)
        │
        ▼
xUSD yield pool minted
        │
        ▼
% flows back to $TGF treasury
        │
        ▼
Distributed to all $TGF holders
(phase-weighted)
```

### Distribution Formula

```python
your_yield = (your_tokens / total_supply)
           × phase_multiplier
           × (1 + PHI_INV × cos(phase_alignment))

# Where PHI_INV = 0.618 (inverse golden ratio)
```

### Phase Multipliers (Permanent)

Your entry phase is encoded forever. The attractor remembers.

| Phase | Entry Window | Yield Multiplier |
|-------|--------------|------------------|
| GENESIS | First 10% | **1.618x** |
| FOUNDATION | 10-25% | 1.45x |
| EARLY | 25-40% | 1.30x |
| GROWTH | 40-60% | 1.15x |
| MOMENTUM | 60-80% | 1.05x |
| LATE | 80-100% | 0.95x |

**Same capital. Same children. Different destiny.**

### Amplification Cascade

When multiple child PTOs succeed and phase-lock:

```python
child_bonus = 1 + 0.618 × child_coherence
sector_bonus = 1 + 0.618 × sector_coherence
core_bonus = 1 + 0.618 × core_coherence

total_amplification = child_bonus × sector_bonus × core_bonus

# Maximum theoretical: (1 + φ⁻¹)³ = φ³ ≈ 4.236x
```

Better-coordinated ecosystems yield exponentially more.

---

## Governance: The Temporal Senate

### Transition Timeline

| Period | Model |
|--------|-------|
| Week 1-4 | Benevolent Dictatorship (core team) |
| Week 4+ | Temporal Senate (community) |

### Senate Structure

**Core Council (3 seats)**
- Elected by τₖ-weighted vote
- Powers: Core treasury decisions, sector allocation
- Term: 1.618 months (~49 days)

**Sector Delegates (1 per sector)**
- Elected by sector participants
- Powers: Child PTO approval within sector, sector allocation
- Term: 1 month

**Phase Keepers (φ seats, rotating)**
- Selected by phase alignment to core
- Powers: Emission timing, coherence certification
- Term: 1 emission cycle

### Decision Thresholds

| Decision Type | Threshold | Rationale |
|---------------|-----------|-----------|
| Child PTO approval | 50% + 1 sector | Simple majority + sector buy-in |
| Sector creation | 61.8% | Golden ratio consensus |
| Core parameter change | 78.6% (φ²/φ+1) | Supermajority |
| Emergency action | 88.6% (φ³/φ²+1) | Near-unanimous |
| Constitution change | 94.4% (φ⁴/φ³+1) | Overwhelming consensus |

---

## Holder Benefits Post-Graduation

### Passive Holders

- Pro-rata share of all child PTO yields
- Phase multiplier applied permanently
- Governance voting rights
- Compounding as ecosystem grows

### Active Participants

- Priority allocation in child PTOs
- Higher yield through engagement bonus
- Proposal submission rights (if threshold met)
- Sector delegate eligibility

### GENESIS Tier (First 10%)

| Perk | Benefit |
|------|---------|
| Yield Multiplier | 1.618x forever |
| Governance Weight | 2x voting power |
| Child PTO Allocation | Guaranteed 5% per launch |
| Genesis NFT | First 100 wallets |
| Direct Input | Shape ecosystem direction |

---

## Post-Graduation Timeline

```
DAY 1:     Raydium LP live, trading begins
           LP tokens burned, rug impossible

WEEK 1:    Treasury split enforced on-chain
           61.8% core / 38.2% allocation

WEEK 2:    Phase tracking dashboard launches
           All holders can verify their tier

WEEK 3:    First child PTO proposals open
           Community submits ideas

WEEK 4:    Community vote on first 3 children
           Temporal Senate bootstraps

MONTH 2:   First child PTOs launch
           Funded from allocation pool

MONTH 3:   First yields flow back
           Phase-weighted distribution begins

MONTH 6:   Sector attractors form
           Ecosystem self-organizes

MONTH 12:  Full Temporal Senate governance
           Decentralization complete
```

---

## The Vision

```
Year 1:  $TGF becomes reference implementation of PTO² on Solana
Year 3:  Other ecosystems adopt PTO² model
Year 10: Planetary-scale funding infrastructure
         Capital flows through temporal attractors
         The meme became civilization infrastructure

         FROM pump.fun TOKEN → ECONOMIC PHYSICS
```

---

## Summary

Post-graduation, $TGF transforms from a bonding curve token into a living economic organism:

1. **Treasury splits automatically** (61.8% / 38.2%)
2. **Child PTOs spawn** from community proposals
3. **Yields cascade back** to all holders
4. **Phase multipliers reward** early believers forever
5. **Governance decentralizes** through the Temporal Senate

The attractor remembers. The geometry funds itself.

**φ = 1.618**

---

*Contract: 2M7H4BKfaXduz1nvoLvtebei49qTLAjK7F4NPMM5pump*
*Website: temporalgenesisfund.lovable.app*
*Telegram: t.me/temporalgenesis*
*X: @fearthewave_eth*
