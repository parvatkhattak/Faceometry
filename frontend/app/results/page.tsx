"use client";

import { useEffect, useMemo, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { AnalysisResponse } from "@/types/api";
import { CountUp, Reveal, SiteNav } from "@/components/ui";

const noopSubscribe = () => () => {};

/** Score → label + colours */
function band(score: number) {
  if (score >= 85) return { label: "Highly balanced", colors: ["#34d399", "#22d3ee"] };
  if (score >= 70) return { label: "Well balanced", colors: ["#22d3ee", "#a78bfa"] };
  if (score >= 50) return { label: "Moderately balanced", colors: ["#fbbf24", "#fb7185"] };
  return { label: "Lower balance", colors: ["#fb7185", "#e11d48"] };
}

export default function ResultsPage() {
  const router = useRouter();
  const stored = useSyncExternalStore(
    noopSubscribe,
    () => sessionStorage.getItem("faceometry_result") ?? "",
    () => null
  );
  const result = useMemo<AnalysisResponse | null>(() => {
    if (!stored) return null;
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }, [stored]);

  useEffect(() => {
    if (stored !== null && !result) router.push("/analyze");
  }, [stored, result, router]);

  if (!result) {
    return (
      <div className="min-h-screen grid place-items-center">
        <div className="text-center">
          <div className="w-9 h-9 rounded-full border-2 border-cyan-300 border-t-transparent animate-spin mx-auto mb-4" />
          <p className="text-sm text-muted">Loading results…</p>
        </div>
      </div>
    );
  }

  const { scores, measurements, golden_ratio_analysis, symmetry_analysis, facial_thirds, facial_fifths, explanations, landmark_image_base64, face } = result;
  const harmonyBand = band(scores.harmony);

  const subScores = [
    { title: "Symmetry", score: scores.symmetry, color: "#22d3ee", weight: "35%" },
    { title: "Proportion", score: scores.proportion, color: "#a78bfa", weight: "25%" },
    { title: "Golden ratio", score: scores.golden_ratio, color: "#fbbf24", weight: "20%" },
    { title: "Facial thirds", score: scores.facial_thirds, color: "#34d399", weight: "10%" },
    { title: "Facial fifths", score: scores.facial_fifths, color: "#fb7185", weight: "10%" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <SiteNav action={{ href: "/analyze", label: "New analysis" }} />

      <main className="flex-1 container-x pt-24 sm:pt-32 pb-16">
        {/* Header */}
        <header className="text-center mb-10 sm:mb-14 animate-fadeInUp">
          <p className="eyebrow mb-3">Analysis complete</p>
          <h1 className="text-[length:var(--fs-h1)] font-bold">
            Your <span className="gradient-text">facial geometry</span> results
          </h1>
        </header>

        {/* Hero: score + photo */}
        <section className="grid lg:grid-cols-[0.9fr_1.1fr] gap-5 sm:gap-6 mb-6">
          <div className="glass-card-static p-6 sm:p-10 flex flex-col items-center justify-center text-center animate-fadeInUp delay-1">
            <p className="eyebrow !text-[var(--color-text-muted)] mb-6">Facial harmony score</p>
            <ScoreRing score={scores.harmony} colors={harmonyBand.colors} />
            <p
              className="mt-6 inline-block rounded-full px-4 py-1.5 text-sm font-medium border"
              style={{ color: harmonyBand.colors[0], borderColor: `${harmonyBand.colors[0]}55`, background: `${harmonyBand.colors[0]}14` }}
            >
              {harmonyBand.label}
            </p>
            <p className="mt-4 text-sm text-muted max-w-xs leading-relaxed">
              Combines symmetry, proportions, golden-ratio proximity, thirds and fifths.
            </p>
          </div>

          <div className="glass-card-static p-4 sm:p-6 flex items-center justify-center animate-fadeInUp delay-2">
            {landmark_image_base64 ? (
              <figure className="relative w-full">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={landmark_image_base64}
                  alt="Your photo with detected facial landmarks"
                  className="w-full max-h-[28rem] object-contain rounded-2xl bg-black/30"
                />
                <figcaption className="mt-3 sm:mt-0 sm:absolute sm:bottom-3 sm:left-3 glass-card-static !rounded-xl px-3 py-1.5 text-[11px] sm:text-xs font-[family-name:var(--font-mono)] text-soft w-fit">
                  yaw {face.pose.yaw.toFixed(1)}° · pitch {face.pose.pitch.toFixed(1)}° · roll {face.pose.roll.toFixed(1)}°
                </figcaption>
              </figure>
            ) : (
              <p className="text-sm text-muted py-16">Landmark image not available</p>
            )}
          </div>
        </section>

        {/* Sub-scores */}
        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6" aria-label="Score breakdown">
          {subScores.map((s, i) => (
            <Reveal key={s.title} delay={i * 70} className={i === 4 ? "col-span-2 sm:col-span-1" : ""}>
              <div className="glass-card h-full p-4 sm:p-5 text-center">
                <p className="text-xs uppercase tracking-wider text-muted mb-2">{s.title}</p>
                <p className="font-[family-name:var(--font-display)] text-3xl sm:text-4xl font-bold" style={{ color: s.color }}>
                  <CountUp value={s.score} delay={400 + i * 90} />
                </p>
                <div className="mt-3 h-1.5 rounded-full bg-white/10 overflow-hidden">
                  <div className="bar-x h-full rounded-full" style={{ width: `${s.score}%`, background: s.color, ["--bar-delay" as string]: `${0.3 + i * 0.08}s` }} />
                </div>
                <p className="mt-2 text-[11px] text-muted">weight {s.weight}</p>
              </div>
            </Reveal>
          ))}
        </section>

        {/* Explanations */}
        <Reveal className="mb-6">
          <section className="glass-card-static p-5 sm:p-8">
            <h2 className="text-xl font-semibold mb-5">What your scores mean</h2>
            <ul className="divide-y divide-[var(--color-border)]">
              {explanations.map((exp) => (
                <li key={exp.component} className="flex items-start gap-4 sm:gap-5 py-4 first:pt-0 last:pb-0">
                  <span className="shrink-0 w-12 sm:w-14 text-center font-[family-name:var(--font-display)] text-2xl font-bold gradient-text-score">
                    {exp.score.toFixed(0)}
                  </span>
                  <div className="min-w-0">
                    <p className="font-medium mb-0.5">{exp.component}</p>
                    <p className="text-sm text-muted leading-relaxed">{exp.explanation}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </Reveal>

        {/* Symmetry + Golden ratio */}
        <section className="grid lg:grid-cols-2 gap-5 sm:gap-6 mb-6">
          <Reveal>
            <div className="glass-card-static h-full p-5 sm:p-8">
              <h2 className="text-xl font-semibold mb-1">Symmetry by region</h2>
              <p className="text-sm text-muted mb-6">How closely each side mirrors the other.</p>
              <ul className="space-y-4">
                {symmetry_analysis.details.map((d, i) => (
                  <li key={d.region} className="grid grid-cols-[5.5rem_1fr_2.5rem] sm:grid-cols-[6.5rem_1fr_2.5rem] items-center gap-3">
                    <span className="text-sm text-soft capitalize">{d.region}</span>
                    <div className="h-2.5 rounded-full bg-white/10 overflow-hidden">
                      <div
                        className="bar-x h-full rounded-full"
                        style={{ width: `${d.score}%`, background: "linear-gradient(90deg,#22d3ee,#a78bfa)", ["--bar-delay" as string]: `${0.2 + i * 0.08}s` }}
                      />
                    </div>
                    <span className="text-sm font-[family-name:var(--font-mono)] text-right">{d.score.toFixed(0)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>

          <Reveal delay={100}>
            <div className="glass-card-static h-full p-5 sm:p-8">
              <h2 className="text-xl font-semibold mb-1">
                Golden ratio <span className="text-[var(--color-accent-amber)] text-base font-normal">φ ≈ 1.618</span>
              </h2>
              <p className="text-sm text-muted mb-6">Selected ratios compared against φ.</p>
              <ul className="space-y-3">
                {golden_ratio_analysis.ratios.map((r, i) => (
                  <li key={r.name} className="rounded-2xl border border-[var(--color-border)] bg-white/[0.02] p-4">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <span className="text-sm text-soft">{r.name}</span>
                      <span className="shrink-0 text-sm font-[family-name:var(--font-mono)] text-[var(--color-accent-amber)]">
                        {r.score.toFixed(0)}<span className="text-muted">/100</span>
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-white/10 overflow-hidden mb-2.5">
                      <div className="bar-x h-full rounded-full bg-[var(--color-accent-amber)]" style={{ width: `${r.score}%`, ["--bar-delay" as string]: `${0.2 + i * 0.08}s` }} />
                    </div>
                    <dl className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted font-[family-name:var(--font-mono)]">
                      <div><dt className="inline">value </dt><dd className="inline text-soft">{r.value.toFixed(3)}</dd></div>
                      <div><dt className="inline">target </dt><dd className="inline text-soft">{r.target.toFixed(3)}</dd></div>
                      <div><dt className="inline">dev </dt><dd className="inline text-soft">{(r.deviation * 100).toFixed(1)}%</dd></div>
                    </dl>
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </section>

        {/* Thirds + Fifths */}
        <section className="grid lg:grid-cols-2 gap-5 sm:gap-6 mb-6">
          <Reveal>
            <div className="glass-card-static h-full p-5 sm:p-8">
              <h2 className="text-xl font-semibold mb-1">Facial thirds</h2>
              <p className="text-sm text-muted mb-6">Vertical proportions · reference 33.3% each</p>
              <div className="flex gap-3 sm:gap-4 h-44 items-end mb-5">
                <Column label="Upper" value={facial_thirds.upper_third} max={0.5} color="#22d3ee" delay={0.2} />
                <Column label="Middle" value={facial_thirds.middle_third} max={0.5} color="#a78bfa" delay={0.3} />
                <Column label="Lower" value={facial_thirds.lower_third} max={0.5} color="#fb7185" delay={0.4} />
              </div>
              <p className="text-sm text-muted">
                Score <span className="font-[family-name:var(--font-mono)] text-soft">{facial_thirds.score.toFixed(0)}/100</span>
              </p>
            </div>
          </Reveal>

          <Reveal delay={100}>
            <div className="glass-card-static h-full p-5 sm:p-8">
              <h2 className="text-xl font-semibold mb-1">Facial fifths</h2>
              <p className="text-sm text-muted mb-6">Horizontal proportions · reference 20% each</p>
              <div className="flex gap-2 sm:gap-3 h-44 items-end mb-5">
                {facial_fifths.sections.map((s, i) => {
                  const colors = ["#fb7185", "#22d3ee", "#a78bfa", "#22d3ee", "#fb7185"];
                  const labels = ["Left", "L eye", "Between", "R eye", "Right"];
                  return <Column key={i} label={labels[i]} value={s} max={0.35} color={colors[i]} delay={0.2 + i * 0.07} small />;
                })}
              </div>
              <p className="text-sm text-muted">
                Score <span className="font-[family-name:var(--font-mono)] text-soft">{facial_fifths.score.toFixed(0)}/100</span>
              </p>
            </div>
          </Reveal>
        </section>

        {/* Measurements */}
        <Reveal className="mb-10">
          <section className="glass-card-static p-5 sm:p-8">
            <h2 className="text-xl font-semibold mb-1">Measurements</h2>
            <p className="text-sm text-muted mb-6">All distances normalized by face height.</p>
            <dl className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {Object.entries(measurements).map(([key, value]) => (
                <div key={key} className="rounded-2xl border border-[var(--color-border)] bg-white/[0.02] p-3.5 sm:p-4">
                  <dt className="text-[11px] uppercase tracking-wider text-muted mb-1.5 leading-snug">{key.replace(/_/g, " ")}</dt>
                  <dd className="font-[family-name:var(--font-mono)] text-base sm:text-lg">
                    {typeof value === "number" ? value.toFixed(3) : value}
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        </Reveal>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center mb-12">
          <Link href="/analyze" className="btn-primary">Analyze another photo</Link>
          <Link href="/" className="btn-secondary">Back to home</Link>
        </div>

        <p className="max-w-3xl mx-auto text-center text-xs sm:text-sm text-muted leading-relaxed border-t border-[var(--color-border)] pt-8">
          <strong className="text-soft">Disclaimer:</strong> The Facial Harmony Score is a geometric analysis of
          proportions and symmetry. It is not an objective measure of beauty or attractiveness. Facial
          geometry varies naturally across individuals, demographics and cultures. This tool is for
          educational and entertainment purposes.
        </p>
      </main>
    </div>
  );
}

/* ========================================
   Sub-components
   ======================================== */

function ScoreRing({ score, colors }: { score: number; colors: string[] }) {
  const size = 220;
  const stroke = 14;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative w-[min(70vw,14rem)] aspect-square">
      <svg viewBox={`0 0 ${size} ${size}`} className="w-full h-full" role="img" aria-label={`Harmony score ${score.toFixed(0)} out of 100`}>
        <defs>
          <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={colors[0]} />
            <stop offset="100%" stopColor={colors[1]} />
          </linearGradient>
          <filter id="ringGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={radius} strokeWidth={stroke} className="score-ring-bg" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={stroke}
          className="score-ring-fill"
          stroke="url(#ringGrad)"
          filter="url(#ringGlow)"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ ["--ring-len" as string]: circumference }}
        />
      </svg>
      <div className="absolute inset-0 grid place-content-center text-center">
        <span className="font-[family-name:var(--font-display)] text-6xl sm:text-7xl font-bold leading-none gradient-text-score">
          <CountUp value={score} duration={1800} />
        </span>
        <span className="text-sm text-muted mt-1">out of 100</span>
      </div>
    </div>
  );
}

function Column({
  label,
  value,
  max,
  color,
  delay,
  small = false,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
  delay: number;
  small?: boolean;
}) {
  const pct = Math.max(8, Math.min(100, (value / max) * 100));
  return (
    <div className="flex-1 h-full flex flex-col items-center justify-end gap-2 min-w-0">
      <span className={`font-[family-name:var(--font-mono)] ${small ? "text-[11px] sm:text-xs" : "text-xs sm:text-sm"} text-soft`}>
        {(value * 100).toFixed(small ? 0 : 1)}%
      </span>
      <div className="w-full flex-1 flex items-end">
        <div
          className="bar-y w-full rounded-t-xl"
          style={{ height: `${pct}%`, background: `linear-gradient(180deg, ${color}, ${color}33)`, ["--bar-delay" as string]: `${delay}s` }}
        />
      </div>
      <span className={`${small ? "text-[10px] sm:text-xs" : "text-xs"} text-muted truncate max-w-full`}>{label}</span>
    </div>
  );
}
