"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card-static px-6 py-4"
           style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none" className="animate-float" style={{ animationDuration: '4s' }}>
              <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" stroke="url(#navGrad)" strokeWidth="1.5" fill="none" />
              <circle cx="14" cy="14" r="4" stroke="url(#navGrad)" strokeWidth="1" fill="none" />
              <defs>
                <linearGradient id="navGrad" x1="0" y1="0" x2="28" y2="28">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            <span className="font-[family-name:var(--font-display)] font-bold text-lg tracking-wider">
              FACEOMETRY
            </span>
          </div>
          <div className="hidden md:flex items-center gap-6">
            <Link href="/analyze" className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent-cyan)] transition-colors">
              Analyze
            </Link>
            <a href="#how-it-works" className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent-cyan)] transition-colors">
              How It Works
            </a>
            <a href="#privacy" className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent-cyan)] transition-colors">
              Privacy
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center pt-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          {/* Geometric decoration */}
          <div className="relative mb-8 animate-fadeInUp">
            <svg width="120" height="120" viewBox="0 0 120 120" fill="none" className="mx-auto animate-float">
              {/* Outer hexagon */}
              <polygon
                points="60,5 110,30 110,90 60,115 10,90 10,30"
                stroke="url(#heroGrad)" strokeWidth="1" fill="none" opacity="0.3"
              />
              {/* Inner hexagon */}
              <polygon
                points="60,20 95,40 95,80 60,100 25,80 25,40"
                stroke="url(#heroGrad)" strokeWidth="1" fill="none" opacity="0.5"
              />
              {/* Face oval */}
              <ellipse cx="60" cy="58" rx="22" ry="30" stroke="url(#heroGrad)" strokeWidth="1.5" fill="none" />
              {/* Eyes */}
              <ellipse cx="50" cy="50" rx="5" ry="3" stroke="#00d4ff" strokeWidth="1" fill="none" />
              <ellipse cx="70" cy="50" rx="5" ry="3" stroke="#00d4ff" strokeWidth="1" fill="none" />
              {/* Nose */}
              <line x1="60" y1="48" x2="60" y2="62" stroke="#8b5cf6" strokeWidth="0.8" opacity="0.6" />
              {/* Mouth */}
              <path d="M52 70 Q60 75 68 70" stroke="#8b5cf6" strokeWidth="1" fill="none" opacity="0.6" />
              {/* Symmetry line */}
              <line x1="60" y1="20" x2="60" y2="100" stroke="#00d4ff" strokeWidth="0.5" opacity="0.2" strokeDasharray="4 4" />
              {/* Measurement lines */}
              <line x1="38" y1="50" x2="82" y2="50" stroke="#f59e0b" strokeWidth="0.5" opacity="0.2" strokeDasharray="3 3" />
              <line x1="38" y1="70" x2="82" y2="70" stroke="#f59e0b" strokeWidth="0.5" opacity="0.2" strokeDasharray="3 3" />
              <defs>
                <linearGradient id="heroGrad" x1="0" y1="0" x2="120" y2="120">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="50%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#f43f5e" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* Tagline */}
          <p className="text-sm font-[family-name:var(--font-mono)] text-[var(--color-accent-cyan)] tracking-[0.3em] uppercase mb-4 animate-fadeInUp-delay-1">
            Facial Geometry Analysis
          </p>

          {/* Title */}
          <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl font-bold mb-4 animate-fadeInUp-delay-1">
            <span className="gradient-text">Faceometry</span>
          </h1>

          {/* Subtitle */}
          <p className="font-[family-name:var(--font-display)] text-xl md:text-2xl text-[var(--color-text-secondary)] mb-8 animate-fadeInUp-delay-2">
            The Geometry Behind Your Face.
          </p>

          {/* Description */}
          <p className="text-[var(--color-text-muted)] max-w-2xl mx-auto mb-10 leading-relaxed animate-fadeInUp-delay-2">
            Analyze your facial proportions, symmetry, and classical geometric ratios using
            computer vision and mathematics. Understand the mathematical structure of your face
            through transparent, explainable analysis.
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-fadeInUp-delay-3">
            <Link href="/analyze" className="btn-primary">
              <span>Analyze Your Face</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ position: 'relative', zIndex: 1 }}>
                <path d="M7 4L13 10L7 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
            <a href="#how-it-works" className="btn-secondary">
              Learn More
            </a>
          </div>

          {/* Feature cards */}
          <div id="how-it-works" className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16 animate-fadeInUp-delay-4">
            <FeatureCard
              icon="◇"
              title="Proportions"
              description="Face width, height, eye spacing, nose ratios, and more — all normalized and compared."
              color="var(--color-accent-cyan)"
            />
            <FeatureCard
              icon="⬡"
              title="Symmetry"
              description="Bilateral landmark comparison across the facial midline with per-region breakdown."
              color="var(--color-accent-violet)"
            />
            <FeatureCard
              icon="φ"
              title="Golden Ratio"
              description="Measure how close selected facial ratios are to φ ≈ 1.618 — the Golden Ratio."
              color="var(--color-accent-amber)"
            />
          </div>

          {/* Privacy section */}
          <div id="privacy" className="glass-card-static p-8 max-w-2xl mx-auto mb-16 animate-fadeInUp-delay-4">
            <div className="flex items-center gap-3 mb-4">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="4" y="8" width="12" height="10" rx="2" stroke="#10b981" strokeWidth="1.5" fill="none"/>
                <path d="M7 8V6C7 4.34 8.34 3 10 3C11.66 3 13 4.34 13 6V8" stroke="#10b981" strokeWidth="1.5" fill="none"/>
              </svg>
              <h3 className="font-[family-name:var(--font-display)] font-semibold text-lg">
                Privacy First
              </h3>
            </div>
            <p className="text-sm text-[var(--color-text-muted)] leading-relaxed">
              Your images are processed in memory and deleted immediately after analysis.
              No facial photographs are stored on our servers. We do not use uploaded images
              for model training. Your facial data stays yours.
            </p>
          </div>

          {/* Scientific disclaimer */}
          <div className="max-w-2xl mx-auto mb-16 px-4">
            <p className="text-xs text-[var(--color-text-muted)] text-center leading-relaxed border-t border-[var(--color-border)] pt-6">
              <strong className="text-[var(--color-text-secondary)]">Scientific Note:</strong>{" "}
              Faceometry is a geometric analysis tool. The Facial Harmony Score represents
              mathematical measurements of proportions and symmetry — it is not an objective
              measurement of beauty or attractiveness. Facial geometry varies naturally across
              individuals and demographics.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--color-border)] py-6 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-[var(--color-text-muted)]">
            © {new Date().getFullYear()} Faceometry. The Geometry Behind Your Face.
          </p>
          <div className="flex items-center gap-6">
            <Link href="/analyze" className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-accent-cyan)] transition-colors">
              Analyze
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: string;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div className="glass-card p-6 text-left">
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center text-xl mb-4"
        style={{ background: `${color}15`, color }}
      >
        {icon}
      </div>
      <h3 className="font-[family-name:var(--font-display)] font-semibold mb-2">
        {title}
      </h3>
      <p className="text-sm text-[var(--color-text-muted)] leading-relaxed">
        {description}
      </p>
    </div>
  );
}
