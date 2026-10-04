"use client";

import Link from "next/link";
import { FaceMesh, Reveal, SiteNav } from "@/components/ui";

const NAV_LINKS = [
  { href: "#features", label: "What we measure" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#privacy", label: "Privacy" },
];

const FEATURES = [
  { icon: "◇", title: "Proportions", color: "#22d3ee", text: "Face width and height, eye spacing, nose and mouth ratios — all normalized so photo size never matters." },
  { icon: "⬡", title: "Symmetry", color: "#a78bfa", text: "Left and right landmarks are mirrored across your facial midline and compared region by region." },
  { icon: "φ", title: "Golden Ratio", color: "#fbbf24", text: "See how close selected facial ratios sit to φ ≈ 1.618, with the exact deviation shown." },
  { icon: "÷3", title: "Facial Thirds", color: "#34d399", text: "Hairline, brows, nose base and chin divide the face vertically into three bands." },
  { icon: "÷5", title: "Facial Fifths", color: "#fb7185", text: "Five horizontal sections from ear to ear, compared against equal widths." },
  { icon: "i", title: "Explainable", color: "#38bdf8", text: "Every score comes with a plain-English explanation and the raw numbers behind it." },
];

const STEPS = [
  { n: "01", title: "Upload a photo", text: "A clear, front-facing photo with good lighting works best." },
  { n: "02", title: "Landmarks detected", text: "MediaPipe maps 468 points on your face — right in memory." },
  { n: "03", title: "Geometry computed", text: "Distances, ratios and mirror errors are calculated and normalized." },
  { n: "04", title: "Understand the results", text: "Get a Facial Harmony Score with a transparent breakdown." },
];

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteNav links={NAV_LINKS} action={{ href: "/analyze", label: "Analyze" }} />

      <main className="flex-1">
        {/* ---------- Hero ---------- */}
        <section className="container-x pt-28 sm:pt-36 pb-14 sm:pb-20">
          <div className="grid lg:grid-cols-[1.15fr_0.85fr] items-center gap-12 lg:gap-8">
            <div className="text-center lg:text-left">
              <p className="eyebrow mb-5 animate-fadeInUp">Facial geometry analysis</p>
              <h1 className="text-[length:var(--fs-hero)] font-bold mb-5 animate-fadeInUp delay-1">
                <span className="gradient-text">Faceometry</span>
              </h1>
              <p className="text-[length:var(--fs-lead)] text-soft font-[family-name:var(--font-display)] mb-5 animate-fadeInUp delay-2">
                The Geometry Behind Your Face.
              </p>
              <p className="text-muted max-w-xl mx-auto lg:mx-0 mb-9 text-base sm:text-lg animate-fadeInUp delay-2">
                Measure your facial proportions, symmetry and classical ratios with computer
                vision and mathematics — transparent, explainable, and private.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center lg:justify-start gap-3 sm:gap-4 animate-fadeInUp delay-3">
                <Link href="/analyze" className="btn-primary">
                  Analyze your face
                  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </Link>
                <a href="#how-it-works" className="btn-secondary">See how it works</a>
              </div>

              <ul className="mt-9 flex flex-wrap justify-center lg:justify-start gap-x-6 gap-y-2 text-sm text-muted animate-fadeInUp delay-4">
                {["No sign-up", "Photos never stored", "Results in seconds"].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <svg width="14" height="14" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                      <path d="M2 6.5l2.5 2.5L10 3.5" stroke="#34d399" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    {t}
                  </li>
                ))}
              </ul>
            </div>

            <div className="relative mx-auto w-full max-w-[22rem] lg:max-w-none animate-fadeInUp delay-2">
              <div className="absolute inset-0 -z-10 rounded-full bg-[radial-gradient(circle,rgba(34,211,238,0.25),transparent_65%)] blur-2xl" />
              <div className="glass-card-static scanner p-6 sm:p-8 animate-float">
                <FaceMesh className="w-full h-auto" />
                <div className="mt-4 grid grid-cols-3 gap-2 text-center font-[family-name:var(--font-mono)] text-[11px] text-muted">
                  <span><b className="block text-[var(--color-accent-cyan)] text-sm">468</b>landmarks</span>
                  <span><b className="block text-[var(--color-accent-violet)] text-sm">5</b>analyses</span>
                  <span><b className="block text-[var(--color-accent-amber)] text-sm">φ 1.618</b>reference</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- Features ---------- */}
        <section id="features" className="section">
          <div className="container-x">
            <Reveal className="text-center max-w-2xl mx-auto mb-12 sm:mb-14">
              <p className="eyebrow mb-3">What we measure</p>
              <h2 className="text-[length:var(--fs-h2)] font-bold mb-4">Six lenses on facial structure</h2>
              <p className="text-muted">Each analysis is a deterministic calculation on your landmarks — no black box.</p>
            </Reveal>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
              {FEATURES.map((f, i) => (
                <Reveal key={f.title} delay={(i % 3) * 90}>
                  <article className="glass-card h-full p-6 sm:p-7">
                    <div
                      className="w-12 h-12 rounded-2xl grid place-items-center text-xl font-bold mb-5"
                      style={{ background: `${f.color}1f`, color: f.color, border: `1px solid ${f.color}40` }}
                    >
                      {f.icon}
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                    <p className="text-sm sm:text-[0.95rem] text-muted leading-relaxed">{f.text}</p>
                  </article>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- How it works ---------- */}
        <section id="how-it-works" className="section">
          <div className="container-x">
            <Reveal className="text-center max-w-2xl mx-auto mb-12 sm:mb-14">
              <p className="eyebrow mb-3">How it works</p>
              <h2 className="text-[length:var(--fs-h2)] font-bold">From photo to insight in four steps</h2>
            </Reveal>

            <ol className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6">
              {STEPS.map((s, i) => (
                <Reveal key={s.n} delay={i * 100}>
                  <li className="glass-card-static h-full p-6">
                    <span className="font-[family-name:var(--font-mono)] text-3xl font-bold gradient-text">{s.n}</span>
                    <h3 className="text-lg font-semibold mt-3 mb-2">{s.title}</h3>
                    <p className="text-sm text-muted leading-relaxed">{s.text}</p>
                  </li>
                </Reveal>
              ))}
            </ol>
          </div>
        </section>

        {/* ---------- Privacy + CTA ---------- */}
        <section id="privacy" className="section">
          <div className="container-x grid lg:grid-cols-2 gap-6">
            <Reveal>
              <div className="glass-card-static h-full p-7 sm:p-9">
                <div className="flex items-center gap-3 mb-4">
                  <span className="w-10 h-10 rounded-xl grid place-items-center bg-emerald-400/10 border border-emerald-400/30">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                      <rect x="4" y="8" width="12" height="10" rx="2" stroke="#34d399" strokeWidth="1.6" />
                      <path d="M7 8V6a3 3 0 016 0v2" stroke="#34d399" strokeWidth="1.6" />
                    </svg>
                  </span>
                  <h3 className="text-xl font-semibold">Privacy first</h3>
                </div>
                <p className="text-muted leading-relaxed">
                  Your image is processed in memory and discarded right after analysis. Nothing is
                  stored, and nothing is used for model training. Your face stays yours.
                </p>
              </div>
            </Reveal>

            <Reveal delay={120}>
              <div className="glass-card-static h-full p-7 sm:p-9 flex flex-col justify-center items-start gap-5">
                <h3 className="text-xl sm:text-2xl font-semibold">Ready to see your geometry?</h3>
                <p className="text-muted">It takes about ten seconds. No account required.</p>
                <Link href="/analyze" className="btn-primary">Start analysis</Link>
              </div>
            </Reveal>
          </div>

          <Reveal className="container-x mt-10">
            <p className="max-w-3xl mx-auto text-center text-xs sm:text-sm text-muted leading-relaxed">
              <strong className="text-soft">Scientific note:</strong> Faceometry is a geometric
              analysis tool. The Facial Harmony Score reflects measurements of proportion and
              symmetry — it is not an objective measure of beauty or attractiveness, and facial
              geometry varies naturally across people and populations.
            </p>
          </Reveal>
        </section>
      </main>

      <footer className="border-t border-[var(--color-border)] py-6">
        <div className="container-x flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted">
          <p>© {new Date().getFullYear()} Faceometry · The Geometry Behind Your Face.</p>
          <Link href="/analyze" className="nav-link !text-xs">Analyze</Link>
        </div>
      </footer>
    </div>
  );
}
