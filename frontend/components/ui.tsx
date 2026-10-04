"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";

/** Ambient aurora + grid background, fixed behind all pages. */
export function Background() {
  return (
    <div className="bg-scene" aria-hidden="true">
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
      <div className="grid" />
    </div>
  );
}

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="logoGrad" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#22d3ee" />
          <stop offset="100%" stopColor="#a78bfa" />
        </linearGradient>
      </defs>
      <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" stroke="url(#logoGrad)" strokeWidth="1.6" />
      <circle cx="14" cy="14" r="4" stroke="url(#logoGrad)" strokeWidth="1.2" />
      <line x1="14" y1="2" x2="14" y2="26" stroke="url(#logoGrad)" strokeWidth="0.6" opacity="0.5" />
    </svg>
  );
}

/** Responsive top navigation with a mobile menu. */
export function SiteNav({
  links = [],
  action,
}: {
  links?: { href: string; label: string }[];
  action?: { href: string; label: string };
}) {
  const [open, setOpen] = useState(false);

  return (
    <header className="site-nav">
      <nav className="container-x flex items-center justify-between py-3.5" aria-label="Main">
        <Link href="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
          <Logo />
          <span className="font-[family-name:var(--font-display)] font-bold tracking-[0.18em] text-sm sm:text-base">
            FACEOMETRY
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="nav-link">
              {l.label}
            </a>
          ))}
          {action && (
            <Link href={action.href} className="btn-secondary !py-2 !px-5 !text-sm">
              {action.label}
            </Link>
          )}
        </div>

        {(links.length > 0 || action) && (
          <button
            type="button"
            className="md:hidden p-2 -mr-2 text-[var(--color-text-secondary)]"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
            </svg>
          </button>
        )}
      </nav>

      {open && (
        <div className="md:hidden container-x pb-4 flex flex-col gap-1 animate-fadeInUp">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="py-3 border-b border-[var(--color-border)] text-[var(--color-text-secondary)]"
              onClick={() => setOpen(false)}
            >
              {l.label}
            </a>
          ))}
          {action && (
            <Link href={action.href} className="btn-primary mt-3" onClick={() => setOpen(false)}>
              {action.label}
            </Link>
          )}
        </div>
      )}
    </header>
  );
}

/** Fades/slides children in once they scroll into view. */
export function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          io.disconnect();
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`reveal ${visible ? "is-visible" : ""} ${className}`}
      style={{ ["--reveal-delay" as string]: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

/** Animated count-up number. */
export function CountUp({
  value,
  duration = 1600,
  decimals = 0,
  delay = 300,
}: {
  value: number;
  duration?: number;
  decimals?: number;
  delay?: number;
}) {
  const [n, setN] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      const id = requestAnimationFrame(() => setN(value));
      return () => cancelAnimationFrame(id);
    }
    let raf = 0;
    const timer = setTimeout(() => {
      const start = performance.now();
      const tick = (now: number) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - t, 4);
        setN(value * eased);
        if (t < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, delay);
    return () => {
      clearTimeout(timer);
      cancelAnimationFrame(raf);
    };
  }, [value, duration, delay]);

  return <>{n.toFixed(decimals)}</>;
}

/** Stylised face-geometry illustration used in the hero and loading state. */
export function FaceMesh({ className = "" }: { className?: string }) {
  const nodes: [number, number][] = [
    [60, 22], [42, 34], [78, 34], [34, 56], [86, 56], [40, 82], [80, 82],
    [60, 104], [50, 52], [70, 52], [60, 66], [52, 84], [68, 84], [60, 40],
  ];
  const edges: [number, number][] = [
    [0, 1], [0, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7], [6, 7], [1, 13], [2, 13],
    [8, 9], [8, 10], [9, 10], [10, 11], [10, 12], [11, 12], [3, 8], [4, 9], [13, 8], [13, 9],
  ];
  return (
    <svg viewBox="0 0 120 124" fill="none" className={className} aria-hidden="true">
      <defs>
        <linearGradient id="meshGrad" x1="0" y1="0" x2="120" y2="124" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#22d3ee" />
          <stop offset="55%" stopColor="#a78bfa" />
          <stop offset="100%" stopColor="#fb7185" />
        </linearGradient>
      </defs>
      <ellipse cx="60" cy="62" rx="40" ry="50" stroke="url(#meshGrad)" strokeWidth="1" opacity="0.5" />
      <line x1="60" y1="8" x2="60" y2="116" stroke="#22d3ee" strokeWidth="0.6" strokeDasharray="3 4" opacity="0.5" />
      <line x1="16" y1="52" x2="104" y2="52" stroke="#fbbf24" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.4" />
      <line x1="16" y1="84" x2="104" y2="84" stroke="#fbbf24" strokeWidth="0.5" strokeDasharray="3 4" opacity="0.4" />
      {edges.map(([a, b], i) => (
        <line
          key={i}
          x1={nodes[a][0]} y1={nodes[a][1]} x2={nodes[b][0]} y2={nodes[b][1]}
          stroke="url(#meshGrad)" strokeWidth="0.8" opacity="0.7"
        />
      ))}
      {nodes.map(([x, y], i) => (
        <circle
          key={i}
          cx={x} cy={y} r="2"
          fill="#22d3ee"
          style={{
            transformOrigin: `${x}px ${y}px`,
            animation: `dot-pulse 2.6s ease-in-out ${(i % 7) * 0.25}s infinite`,
          }}
        />
      ))}
    </svg>
  );
}
