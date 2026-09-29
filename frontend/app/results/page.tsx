"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { AnalysisResponse } from "@/types/api";

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("faceometry_result");
    if (!stored) {
      router.push("/analyze");
      return;
    }
    try {
      setResult(JSON.parse(stored));
      setMounted(true);
    } catch {
      router.push("/analyze");
    }
  }, [router]);

  if (!result || !mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-[var(--color-accent-cyan)] border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-sm text-[var(--color-text-muted)]">Loading results...</p>
        </div>
      </div>
    );
  }

  const { scores, measurements, golden_ratio_analysis, symmetry_analysis, facial_thirds, facial_fifths, explanations, landmark_image_base64, face } = result;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card-static px-6 py-4"
           style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
              <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" stroke="url(#rNav)" strokeWidth="1.5" fill="none" />
              <circle cx="14" cy="14" r="4" stroke="url(#rNav)" strokeWidth="1" fill="none" />
              <defs>
                <linearGradient id="rNav" x1="0" y1="0" x2="28" y2="28">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            <span className="font-[family-name:var(--font-display)] font-bold tracking-wider">FACEOMETRY</span>
          </Link>
          <Link href="/analyze" className="btn-secondary text-xs">
            New Analysis
          </Link>
        </div>
      </nav>

      {/* Results */}
      <main className="flex-1 pt-24 pb-16 px-6">
        <div className="max-w-6xl mx-auto">

          {/* Header */}
          <div className="text-center mb-12 animate-fadeInUp">
            <p className="text-xs font-[family-name:var(--font-mono)] text-[var(--color-accent-cyan)] tracking-[0.3em] uppercase mb-2">
              Analysis Complete
            </p>
            <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold">
              Your <span className="gradient-text">Facial Geometry</span> Results
            </h1>
          </div>

          {/* Main Score + Face */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Harmony Score */}
            <div className="glass-card p-8 flex flex-col items-center justify-center animate-fadeInUp-delay-1">
              <p className="text-xs font-[family-name:var(--font-mono)] text-[var(--color-text-muted)] tracking-wider uppercase mb-6">
                Facial Harmony Score
              </p>
              <ScoreRing score={scores.harmony} size={180} />
              <p className="mt-6 text-sm text-[var(--color-text-muted)] max-w-xs text-center leading-relaxed">
                Based on symmetry, proportions, golden ratio proximity, facial thirds, and fifths.
              </p>
            </div>

            {/* Face with landmarks */}
            <div className="glass-card p-6 flex items-center justify-center animate-fadeInUp-delay-2">
              {landmark_image_base64 ? (
                <div className="relative">
                  <img
                    src={landmark_image_base64}
                    alt="Face with landmark annotations"
                    className="max-w-full max-h-[360px] object-contain rounded-lg"
                  />
                  <div className="absolute bottom-2 left-2 glass-card-static px-3 py-1.5 text-xs">
                    <span className="text-[var(--color-text-muted)]">Pose: </span>
                    <span className="font-[family-name:var(--font-mono)]">
                      {face.pose.yaw.toFixed(1)}° yaw · {face.pose.pitch.toFixed(1)}° pitch · {face.pose.roll.toFixed(1)}° roll
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-[var(--color-text-muted)]">Landmark image not available</p>
              )}
            </div>
          </div>

          {/* Sub-scores grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8 animate-fadeInUp-delay-2">
            <SubScoreCard title="Symmetry" score={scores.symmetry} color="#00d4ff" />
            <SubScoreCard title="Proportion" score={scores.proportion} color="#8b5cf6" />
            <SubScoreCard title="Golden Ratio" score={scores.golden_ratio} color="#f59e0b" />
            <SubScoreCard title="Thirds" score={scores.facial_thirds} color="#10b981" />
            <SubScoreCard title="Fifths" score={scores.facial_fifths} color="#f43f5e" />
          </div>

          {/* Explanations */}
          <div className="glass-card p-6 mb-8 animate-fadeInUp-delay-3">
            <h2 className="font-[family-name:var(--font-display)] font-semibold text-lg mb-4 flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="9" r="8" stroke="#00d4ff" strokeWidth="1.5" fill="none" />
                <path d="M9 5V10M9 12.5V13" stroke="#00d4ff" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              Score Explanations
            </h2>
            <div className="space-y-4">
              {explanations.map((exp) => (
                <div key={exp.component} className="flex items-start gap-4 py-3 border-b border-[var(--color-border)] last:border-0">
                  <div className="flex-shrink-0 w-14 text-right">
                    <span className="font-[family-name:var(--font-mono)] text-sm font-bold gradient-text-score">
                      {exp.score.toFixed(0)}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-0.5">{exp.component}</p>
                    <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">{exp.explanation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed analysis grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Symmetry Details */}
            <div className="glass-card p-6 animate-fadeInUp-delay-3">
              <h3 className="font-[family-name:var(--font-display)] font-semibold mb-4">Symmetry Analysis</h3>
              <div className="space-y-3">
                {symmetry_analysis.details.map((d) => (
                  <div key={d.region} className="flex items-center gap-3">
                    <span className="text-xs text-[var(--color-text-muted)] capitalize w-20">{d.region}</span>
                    <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${d.score}%`,
                          background: `linear-gradient(90deg, #00d4ff, #8b5cf6)`,
                        }}
                      />
                    </div>
                    <span className="text-xs font-[family-name:var(--font-mono)] w-10 text-right">{d.score.toFixed(0)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Golden Ratio Details */}
            <div className="glass-card p-6 animate-fadeInUp-delay-3">
              <h3 className="font-[family-name:var(--font-display)] font-semibold mb-4">
                Golden Ratio Analysis <span className="text-[var(--color-accent-amber)] text-sm">φ ≈ 1.618</span>
              </h3>
              <div className="space-y-3">
                {golden_ratio_analysis.ratios.map((r) => (
                  <div key={r.name} className="glass-card-static p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-[var(--color-text-secondary)]">{r.name}</span>
                      <span className="text-xs font-[family-name:var(--font-mono)] text-[var(--color-accent-amber)]">
                        {r.score.toFixed(0)}/100
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[var(--color-text-muted)]">
                      <span>Value: <span className="font-[family-name:var(--font-mono)]">{r.value.toFixed(3)}</span></span>
                      <span>Target: <span className="font-[family-name:var(--font-mono)]">{r.target.toFixed(3)}</span></span>
                      <span>Dev: <span className="font-[family-name:var(--font-mono)]">{(r.deviation * 100).toFixed(1)}%</span></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Thirds & Fifths */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Facial Thirds */}
            <div className="glass-card p-6 animate-fadeInUp-delay-4">
              <h3 className="font-[family-name:var(--font-display)] font-semibold mb-4">
                Facial Thirds
                <span className="text-xs text-[var(--color-text-muted)] ml-2">Vertical proportions</span>
              </h3>
              <div className="flex gap-2 h-32 items-end mb-4">
                <ThirdBar label="Upper" value={facial_thirds.upper_third} color="#00d4ff" />
                <ThirdBar label="Middle" value={facial_thirds.middle_third} color="#8b5cf6" />
                <ThirdBar label="Lower" value={facial_thirds.lower_third} color="#f43f5e" />
              </div>
              <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)]">
                <span>Score: <span className="font-[family-name:var(--font-mono)] text-[var(--color-text-secondary)]">{facial_thirds.score.toFixed(0)}/100</span></span>
                <span>Reference: 33.3% each</span>
              </div>
            </div>

            {/* Facial Fifths */}
            <div className="glass-card p-6 animate-fadeInUp-delay-4">
              <h3 className="font-[family-name:var(--font-display)] font-semibold mb-4">
                Facial Fifths
                <span className="text-xs text-[var(--color-text-muted)] ml-2">Horizontal proportions</span>
              </h3>
              <div className="flex gap-1 h-16 items-end mb-4">
                {facial_fifths.sections.map((s, i) => {
                  const colors = ["#f43f5e", "#00d4ff", "#8b5cf6", "#00d4ff", "#f43f5e"];
                  const labels = ["Left", "L Eye", "Inter", "R Eye", "Right"];
                  return (
                    <div
                      key={i}
                      className="flex-1 rounded-t-lg relative group"
                      style={{
                        height: `${Math.max(20, s * 100 * 3)}%`,
                        background: `linear-gradient(180deg, ${colors[i]}, ${colors[i]}44)`,
                      }}
                    >
                      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-[var(--color-text-muted)] whitespace-nowrap">
                        {labels[i]}
                      </div>
                      <div className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-[family-name:var(--font-mono)]">
                        {(s * 100).toFixed(0)}%
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)] mt-8">
                <span>Score: <span className="font-[family-name:var(--font-mono)] text-[var(--color-text-secondary)]">{facial_fifths.score.toFixed(0)}/100</span></span>
                <span>Reference: 20% each</span>
              </div>
            </div>
          </div>

          {/* Measurements table */}
          <div className="glass-card p-6 mb-8 animate-fadeInUp-delay-4">
            <h3 className="font-[family-name:var(--font-display)] font-semibold mb-4">
              Measurements
              <span className="text-xs text-[var(--color-text-muted)] ml-2">Normalized by face height</span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {Object.entries(measurements).map(([key, value]) => (
                <div key={key} className="glass-card-static p-3">
                  <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                    {key.replace(/_/g, " ")}
                  </p>
                  <p className="font-[family-name:var(--font-mono)] text-sm">
                    {typeof value === 'number' ? value.toFixed(4) : value}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="max-w-3xl mx-auto text-center border-t border-[var(--color-border)] pt-8">
            <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
              <strong className="text-[var(--color-text-secondary)]">Disclaimer:</strong>{" "}
              The Facial Harmony Score represents geometric analysis of proportions and symmetry.
              It is not an objective measurement of beauty or attractiveness. Facial geometry varies
              naturally across individuals, demographics, and cultures. This tool is for educational
              and entertainment purposes.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}


/* ========================================
   Sub-components
   ======================================== */

function ScoreRing({ score, size = 160 }: { score: number; size?: number }) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const center = size / 2;

  // Color based on score
  const getColor = (s: number) => {
    if (s >= 80) return ["#10b981", "#00d4ff"];
    if (s >= 60) return ["#00d4ff", "#8b5cf6"];
    if (s >= 40) return ["#f59e0b", "#f43f5e"];
    return ["#f43f5e", "#dc2626"];
  };
  const [c1, c2] = getColor(score);

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="scoreGradient" x1="0" y1="0" x2={String(size)} y2={String(size)}>
            <stop offset="0%" stopColor={c1} />
            <stop offset="100%" stopColor={c2} />
          </linearGradient>
        </defs>
        <circle
          cx={center} cy={center} r={radius}
          className="score-ring-bg"
        />
        <circle
          cx={center} cy={center} r={radius}
          className="score-ring-fill"
          stroke="url(#scoreGradient)"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ animation: 'score-fill 1.5s ease-out forwards' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-[family-name:var(--font-display)] text-5xl font-bold gradient-text-score"
          style={{ animation: 'score-count 0.8s ease-out 0.5s forwards', opacity: 0, transformOrigin: 'center' }}
        >
          {score.toFixed(0)}
        </span>
        <span className="text-xs text-[var(--color-text-muted)] mt-1">/ 100</span>
      </div>
    </div>
  );
}

function SubScoreCard({ title, score, color }: { title: string; score: number; color: string }) {
  return (
    <div className="glass-card p-4 text-center">
      <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2 font-[family-name:var(--font-display)]">
        {title}
      </p>
      <p className="font-[family-name:var(--font-display)] text-2xl font-bold" style={{ color }}>
        {score.toFixed(0)}
      </p>
      <div className="mt-2 h-1 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000"
          style={{ width: `${score}%`, background: color }}
        />
      </div>
    </div>
  );
}

function ThirdBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex-1 flex flex-col items-center gap-2">
      <span className="text-xs font-[family-name:var(--font-mono)]">{(value * 100).toFixed(1)}%</span>
      <div
        className="w-full rounded-t-lg transition-all duration-1000"
        style={{
          height: `${value * 100 * 2.5}%`,
          minHeight: '20px',
          background: `linear-gradient(180deg, ${color}, ${color}44)`,
        }}
      />
      <span className="text-[10px] text-[var(--color-text-muted)]">{label}</span>
    </div>
  );
}
