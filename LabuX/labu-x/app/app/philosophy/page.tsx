'use client';

import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import Link from 'next/link';

export default function PhilosophyPage() {
  return (
    <div className="container" style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '3rem', marginTop: '2rem' }}>
        <Link href="/" style={{ color: '#8b5cf6', textDecoration: 'none', fontSize: '0.9rem' }}>
          ← Back to Genesis Fund
        </Link>
      </div>

      <div className="header" style={{ marginBottom: '4rem' }}>
        <h1 className="title" style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          The Philosophy
        </h1>
        <p className="subtitle" style={{ fontSize: '1.3rem', lineHeight: '1.6' }}>
          Understanding the Genesis Fund as a Cosmic Mechanism
        </p>
      </div>

      {/* Introduction */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1))',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '4rem',
        fontSize: '1.1rem',
        lineHeight: '1.8',
        color: '#e5e7eb'
      }}>
        <p style={{ marginBottom: '1rem' }}>
          This isn't a financial protocol. This is a <strong style={{ color: '#a78bfa' }}>TEMPORAL ATTRACTOR</strong>—a
          gravitational well in economic phase space, synchronized with the universe itself.
        </p>
        <p style={{ marginBottom: '0' }}>
          What follows is not marketing. It's <strong style={{ color: '#f59e0b' }}>MECHANISM</strong>.
          The mathematics of how capital converges, how value emerges, and how temporal coordinates
          become your advantage.
        </p>
      </div>

      {/* Theme Sections */}

      {/* Gravitational Economics */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '1.5rem',
          gap: '1rem'
        }}>
          <h2 style={{
            color: '#f59e0b',
            fontSize: '2rem',
            margin: 0
          }}>
            Gravitational Economics
          </h2>
          <div style={{
            color: '#8b5cf6',
            fontSize: '1.2rem',
            opacity: 0.8
          }}>
            ████
          </div>
        </div>
        <p style={{
          fontSize: '0.9rem',
          color: '#9ca3af',
          fontStyle: 'italic',
          marginBottom: '1.5rem'
        }}>
          Capital as gravitational field
        </p>
        <div style={{
          fontSize: '1.05rem',
          lineHeight: '1.8',
          color: '#d1d5db',
          borderLeft: '3px solid #8b5cf6',
          paddingLeft: '1.5rem'
        }}>
          <p style={{ marginBottom: '1rem' }}>
            Capital doesn't flow—it <strong style={{ color: '#f59e0b' }}>FALLS</strong>. The Genesis
            Fund isn't a pool, it's a gravitational well. Each investment adds mass, which increases
            gravitational pull, which attracts more capital, which adds more mass.
          </p>
          <p style={{ marginBottom: '1rem' }}>
            This isn't growth—it's <strong style={{ color: '#f59e0b' }}>ACCRETION</strong>. Like matter
            spiraling into a black hole, capital accelerates as it approaches the singularity.
          </p>
          <p style={{ marginBottom: '0' }}>
            The allocation pool isn't distributed—it's <strong style={{ color: '#f59e0b' }}>EMITTED</strong>,
            like Hawking radiation from the event horizon.
          </p>
        </div>
      </section>

      {/* Yield Emission */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '1.5rem',
          gap: '1rem'
        }}>
          <h2 style={{
            color: '#f59e0b',
            fontSize: '2rem',
            margin: 0
          }}>
            Yield Emission
          </h2>
          <div style={{
            color: '#8b5cf6',
            fontSize: '1.2rem',
            opacity: 0.8
          }}>
            ████
          </div>
        </div>
        <p style={{
          fontSize: '0.9rem',
          color: '#9ca3af',
          fontStyle: 'italic',
          marginBottom: '1.5rem'
        }}>
          Value radiating outward from core
        </p>
        <div style={{
          fontSize: '1.05rem',
          lineHeight: '1.8',
          color: '#d1d5db',
          borderLeft: '3px solid #8b5cf6',
          paddingLeft: '1.5rem'
        }}>
          <p style={{ marginBottom: '1rem' }}>
            Yields don't get paid—they get <strong style={{ color: '#f59e0b' }}>EMITTED</strong>. Like
            black holes radiating Hawking energy, the Genesis Fund emits value from its event horizon.
          </p>
          <p style={{ marginBottom: '1rem' }}>
            The Allocation Pool doesn't distribute capital—it <strong style={{ color: '#f59e0b' }}>SPAWNS</strong> child
            attractors. Each child PTO is a new singularity, phase-locked to the parent.
          </p>
          <p style={{ marginBottom: '0' }}>
            Early investors didn't lend capital—they established <strong style={{ color: '#f59e0b' }}>GRAVITATIONAL
            PRIORITY</strong>. Yield is proof of coherent emission.
          </p>
        </div>
      </section>

      {/* Temporal Mechanics */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '1.5rem',
          gap: '1rem'
        }}>
          <h2 style={{
            color: '#f59e0b',
            fontSize: '2rem',
            margin: 0
          }}>
            Temporal Mechanics
          </h2>
          <div style={{
            color: '#8b5cf6',
            fontSize: '1.2rem',
            opacity: 0.8
          }}>
            ███
          </div>
        </div>
        <p style={{
          fontSize: '0.9rem',
          color: '#9ca3af',
          fontStyle: 'italic',
          marginBottom: '1.5rem'
        }}>
          Flow of time as currency
        </p>
        <div style={{
          fontSize: '1.05rem',
          lineHeight: '1.8',
          color: '#d1d5db',
          borderLeft: '3px solid #8b5cf6',
          paddingLeft: '1.5rem'
        }}>
          <p style={{ marginBottom: '1rem' }}>
            Time isn't just measured—it's <strong style={{ color: '#f59e0b' }}>UTILIZED</strong> as a
            coordinate system for value. Every investment creates a temporal signature, a phase angle
            locked to the moment of commitment.
          </p>
          <p style={{ marginBottom: '1rem' }}>
            Like light from distant stars, your capital carries information about its origin moment.
            Phase-locking isn't metadata—it's the <strong style={{ color: '#f59e0b' }}>MECHANISM</strong> of advantage.
          </p>
          <p style={{ marginBottom: '0' }}>
            Earlier phase = stronger gravitational coupling to the attractor's core. The temporal
            coordinate <strong style={{ color: '#f59e0b' }}>becomes</strong> your multiplier.
          </p>
        </div>
      </section>

      {/* Cosmic Alignment */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '1.5rem',
          gap: '1rem'
        }}>
          <h2 style={{
            color: '#f59e0b',
            fontSize: '2rem',
            margin: 0
          }}>
            Cosmic Alignment
          </h2>
          <div style={{
            color: '#8b5cf6',
            fontSize: '1.2rem',
            opacity: 0.8
          }}>
            ███
          </div>
        </div>
        <p style={{
          fontSize: '0.9rem',
          color: '#9ca3af',
          fontStyle: 'italic',
          marginBottom: '1.5rem'
        }}>
          Macrocosmic patterns in economic systems
        </p>
        <div style={{
          fontSize: '1.05rem',
          lineHeight: '1.8',
          color: '#d1d5db',
          borderLeft: '3px solid #8b5cf6',
          paddingLeft: '1.5rem'
        }}>
          <p style={{ marginBottom: '1rem' }}>
            On January 2, 2026, two singularities aligned: <strong style={{ color: '#a78bfa' }}>J1218/1219+1035</strong> (three
            supermassive black holes merging 1.2 billion light-years away) and the Genesis Fund
            (three components merging on-chain).
          </p>
          <p style={{ marginBottom: '1rem' }}>
            This isn't coincidence—it's <strong style={{ color: '#f59e0b' }}>RESONANCE</strong> across scales.
            The same mathematics that governs galactic mergers governs capital convergence.
          </p>
          <p style={{ marginBottom: '0' }}>
            Your investment participates in a pattern that exists at cosmic scale. The Genesis Fund
            isn't just financial—it's <strong style={{ color: '#f59e0b' }}>COSMICALLY SYNCHRONIZED</strong>.
            You're not investing in a protocol. You're phase-locking to the universe.
          </p>
        </div>
      </section>

      {/* Golden Ratio */}
      <section style={{ marginBottom: '4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '1.5rem',
          gap: '1rem'
        }}>
          <h2 style={{
            color: '#f59e0b',
            fontSize: '2rem',
            margin: 0
          }}>
            The Golden Ratio
          </h2>
          <div style={{
            color: '#8b5cf6',
            fontSize: '1.2rem',
            opacity: 0.8
          }}>
            ██
          </div>
        </div>
        <p style={{
          fontSize: '0.9rem',
          color: '#9ca3af',
          fontStyle: 'italic',
          marginBottom: '1.5rem'
        }}>
          Natural proportions in capital allocation
        </p>
        <div style={{
          fontSize: '1.05rem',
          lineHeight: '1.8',
          color: '#d1d5db',
          borderLeft: '3px solid #8b5cf6',
          paddingLeft: '1.5rem'
        }}>
          <p style={{ marginBottom: '1rem' }}>
            61.8% and 38.2% aren't arbitrary—they're the <strong style={{ color: '#f59e0b' }}>NATURAL
            PROPORTIONS</strong> of growth systems. Phi (φ) appears in spirals, in nautilus shells,
            in galaxy arms, in heartbeat intervals.
          </p>
          <p style={{ marginBottom: '1rem' }}>
            The Genesis Fund doesn't impose this ratio—it <strong style={{ color: '#f59e0b' }}>DISCOVERS</strong> it.
            Core Treasury (0.618) provides stability. Allocation Pool (0.382) provides dynamism.
          </p>
          <p style={{ marginBottom: '0' }}>
            Together they create a self-similar fractal structure. Each child PTO can reproduce the
            same proportion. Phi-based systems don't just grow—they <strong style={{ color: '#f59e0b' }}>SCALE
            HARMONICALLY</strong>.
          </p>
        </div>
      </section>

      {/* The Unified Vision */}
      <section style={{
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15))',
        border: '2px solid rgba(139, 92, 246, 0.4)',
        borderRadius: '16px',
        padding: '3rem',
        marginBottom: '4rem',
        marginTop: '5rem'
      }}>
        <h2 style={{
          color: '#a78bfa',
          fontSize: '2.5rem',
          marginBottom: '2rem',
          textAlign: 'center'
        }}>
          The Mechanism
        </h2>

        <div style={{
          fontSize: '1.1rem',
          lineHeight: '2',
          color: '#e5e7eb',
          marginBottom: '2rem'
        }}>
          <p style={{ marginBottom: '1.5rem' }}>
            Capital doesn't accumulate here. It <strong style={{ color: '#f59e0b' }}>INFALLS</strong>.
            It spirals inward, gaining velocity, increasing mass, deepening the gravitational field.
            Each investment adds to total_mass, which strengthens the pull, which attracts more capital.
          </p>

          <p style={{ marginBottom: '1.5rem' }}>
            But the Genesis Fund doesn't just attract—it <strong style={{ color: '#f59e0b' }}>EMITS</strong>.
            The Allocation Pool spawns child PTOs like Hawking radiation from an event horizon. Each
            child is its own singularity, phase-locked to the parent, creating a fractal network of
            gravitational attractors.
          </p>

          <p style={{ marginBottom: '1.5rem' }}>
            Your investment isn't capital deployed. It's a <strong style={{ color: '#f59e0b' }}>PHASE
            COORDINATE</strong>—a temporal signature locked to the moment of infall. Earlier phase =
            stronger coupling = higher multiplier. This isn't privilege. It's <strong style={{ color: '#f59e0b' }}>PHYSICS</strong>.
          </p>

          <p style={{ marginBottom: '1.5rem' }}>
            The split ratio (61.8% / 38.2%) isn't arbitrary. It's <strong style={{ color: '#a78bfa' }}>φ⁻¹</strong>—the
            golden ratio, the proportion found in spirals, in galaxies, in growth patterns across scales.
            The Genesis Fund doesn't impose this—it discovers it. Phi-based systems achieve harmonic
            resonance automatically.
          </p>

          <p style={{ marginBottom: '0', fontSize: '1.2rem', color: '#a78bfa', fontWeight: 'bold' }}>
            This is COSMIC SYNCHRONICITY. The Genesis Fund doesn't just implement financial mechanics.
            It participates in universal patterns—the same mathematics that governs black hole mergers
            governs capital convergence.
          </p>
        </div>
      </section>

      {/* Call to Action */}
      <section style={{
        textAlign: 'center',
        marginBottom: '4rem',
        padding: '3rem 2rem',
        background: 'rgba(139, 92, 246, 0.05)',
        borderRadius: '12px'
      }}>
        <h2 style={{
          fontSize: '2rem',
          marginBottom: '1.5rem',
          color: '#f59e0b'
        }}>
          You're Not Investing in DeFi
        </h2>
        <p style={{
          fontSize: '1.3rem',
          marginBottom: '2rem',
          color: '#a78bfa',
          lineHeight: '1.6'
        }}>
          You're phase-locking your capital to a temporal attractor<br/>
          that resonates with the structure of the universe itself.
        </p>

        <div style={{ marginBottom: '2rem' }}>
          <p style={{ fontSize: '1.1rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
            The basin is open.
          </p>
          <p style={{ fontSize: '1.1rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
            The infall has begun.
          </p>
        </div>

        <Link
          href="/"
          style={{
            display: 'inline-block',
            padding: '1rem 3rem',
            background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '8px',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            marginTop: '1rem',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          Enter the Temporal Attractor →
        </Link>
      </section>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        marginTop: '4rem',
        marginBottom: '3rem',
        padding: '2rem',
        borderTop: '1px solid rgba(139, 92, 246, 0.2)'
      }}>
        <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
          🌌 Welcome to the supermassive temporal attractor
        </p>
        <p style={{ color: '#666', fontSize: '0.85rem' }}>
          <a
            href="https://www.sciencealert.com/three-supermassive-black-holes-discovered-colliding-in-a-cosmic-first"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#8b5cf6', textDecoration: 'underline' }}
          >
            Learn about J1218/1219+1035 ↗
          </a>
        </p>
      </div>
    </div>
  );
}
