"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { analyzeImage, ApiError } from "@/lib/api";
import { FaceMesh, SiteNav } from "@/components/ui";

type AnalysisState = "idle" | "analyzing" | "error";

const STEPS = [
  "Detecting face & landmarks",
  "Measuring proportions",
  "Comparing left & right symmetry",
  "Calculating harmony score",
];

const TIPS = ["Front-facing photo", "Good, even lighting", "Clear, sharp image", "One person only"];

export default function AnalyzePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [state, setState] = useState<AnalysisState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorIssues, setErrorIssues] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [step, setStep] = useState(0);

  // Advance the loading checklist while analysis is running
  useEffect(() => {
    if (state !== "analyzing") return;
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 1100);
    return () => clearInterval(id);
  }, [state]);

  const handleFile = useCallback((file: File) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError("Please upload a JPEG, PNG, or WebP image.");
      setErrorIssues([]);
      return;
    }
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum: 10 MB.`);
      setErrorIssues([]);
      return;
    }

    setSelectedFile(file);
    setError(null);
    setErrorIssues([]);
    setState("idle");

    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setState("analyzing");
    setStep(0);
    setError(null);
    setErrorIssues([]);

    try {
      const result = await analyzeImage(selectedFile);
      sessionStorage.setItem("faceometry_result", JSON.stringify(result));
      router.push("/results");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
        setErrorIssues(err.issues);
      } else {
        setError("Can't reach the analysis server. Check your connection and try again.");
      }
      setState("error");
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    setErrorIssues([]);
    setState("idle");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const busy = state === "analyzing";

  return (
    <div className="min-h-screen flex flex-col">
      <SiteNav action={{ href: "/", label: "Home" }} />

      <main className="flex-1 container-x pt-24 sm:pt-32 pb-14">
        <div className="mx-auto w-full max-w-2xl">
          <header className="text-center mb-8 sm:mb-10 animate-fadeInUp">
            <p className="eyebrow mb-3">Step 1 of 2</p>
            <h1 className="text-[length:var(--fs-h1)] font-bold mb-3">
              <span className="gradient-text">Analyze your face</span>
            </h1>
            <p className="text-muted max-w-md mx-auto">
              Upload a front-facing photograph to measure your facial geometry and proportions.
            </p>
          </header>

          {/* Error banner (also shown before a file is selected) */}
          {error && (
            <div
              role="alert"
              className="mb-5 rounded-2xl border border-rose-400/35 bg-rose-400/[0.07] p-4 sm:p-5 animate-fadeInUp"
            >
              <div className="flex items-start gap-3">
                <svg width="20" height="20" viewBox="0 0 18 18" fill="none" className="mt-0.5 shrink-0" aria-hidden="true">
                  <circle cx="9" cy="9" r="8" stroke="#fb7185" strokeWidth="1.5" />
                  <path d="M9 5v5M9 12.5v.5" stroke="#fb7185" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
                <div className="min-w-0">
                  <p className="font-medium text-rose-300">{error}</p>
                  {errorIssues.length > 0 && (
                    <ul className="mt-2 space-y-1.5">
                      {errorIssues.map((issue, i) => (
                        <li key={i} className="text-sm text-soft flex gap-2">
                          <span className="text-rose-300">•</span>
                          <span>{issue}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {!preview ? (
            <div
              role="button"
              tabIndex={0}
              aria-label="Upload a photo"
              className={`upload-zone animate-fadeInUp delay-1 ${dragOver ? "drag-over" : ""}`}
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  fileInputRef.current?.click();
                }
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />

              <div className="mx-auto mb-5 w-16 h-16 rounded-2xl grid place-items-center bg-cyan-400/10 border border-cyan-400/25 animate-float">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 16V4M7 9l5-5 5 5" />
                  <path d="M4 15v3a2 2 0 002 2h12a2 2 0 002-2v-3" />
                </svg>
              </div>

              <p className="font-[family-name:var(--font-display)] text-lg sm:text-xl font-semibold mb-1">
                Drop your photo here
              </p>
              <p className="text-soft mb-4">
                or <span className="text-[var(--color-accent-cyan)] underline underline-offset-4">browse files</span>
              </p>
              <p className="text-xs sm:text-sm text-muted">JPEG, PNG or WebP · up to 10 MB</p>
            </div>
          ) : (
            <div className="animate-fadeInUp">
              <div className="glass-card-static overflow-hidden mb-5">
                <div className={`relative flex items-center justify-center bg-black/30 h-[min(60vh,28rem)] ${busy ? "scanner" : ""}`}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={preview} alt="Selected photo preview" className="max-w-full max-h-full object-contain" />

                  {busy && (
                    <div className="absolute inset-0 bg-black/55 backdrop-blur-[2px] grid place-items-center p-4">
                      <div className="w-full max-w-xs text-center">
                        <FaceMesh className="w-20 h-20 mx-auto mb-4 animate-float" />
                        <ul className="text-left space-y-2.5">
                          {STEPS.map((label, i) => (
                            <li
                              key={label}
                              className={`flex items-center gap-3 text-sm transition-colors duration-300 ${
                                i <= step ? "text-white" : "text-muted"
                              }`}
                              style={i === step ? { animation: "step-in .4s ease both" } : undefined}
                            >
                              <span className="w-5 h-5 grid place-items-center shrink-0">
                                {i < step ? (
                                  <svg width="16" height="16" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                                    <path d="M2 6.5l2.5 2.5L10 3.5" stroke="#34d399" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                                  </svg>
                                ) : i === step ? (
                                  <span className="w-3 h-3 rounded-full border-2 border-cyan-300 border-t-transparent animate-spin" />
                                ) : (
                                  <span className="w-1.5 h-1.5 rounded-full bg-white/25" />
                                )}
                              </span>
                              {label}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4 sm:p-5 border-t border-[var(--color-border)] flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{selectedFile?.name}</p>
                    <p className="text-xs text-muted">
                      {selectedFile && (selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={handleReset}
                    disabled={busy}
                    className="text-sm text-muted hover:text-rose-300 transition-colors disabled:opacity-40 shrink-0"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <div className="flex flex-col-reverse sm:flex-row gap-3">
                <button type="button" onClick={handleReset} disabled={busy} className="btn-secondary sm:w-auto">
                  Choose another
                </button>
                <button type="button" onClick={handleAnalyze} disabled={busy} className="btn-primary flex-1">
                  {busy ? "Analyzing…" : "Analyze photo"}
                </button>
              </div>
            </div>
          )}

          {/* Tips */}
          <section className="mt-10 animate-fadeInUp delay-3" aria-label="Tips for best results">
            <p className="text-sm text-soft text-center mb-4 font-[family-name:var(--font-display)]">
              For the most accurate results
            </p>
            <ul className="grid grid-cols-1 min-[420px]:grid-cols-2 gap-3">
              {TIPS.map((tip) => (
                <li key={tip} className="glass-card-static flex items-center gap-3 px-4 py-3 text-sm text-soft">
                  <svg width="14" height="14" viewBox="0 0 12 12" fill="none" className="shrink-0" aria-hidden="true">
                    <path d="M2 6.5l2.5 2.5L10 3.5" stroke="#34d399" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  {tip}
                </li>
              ))}
            </ul>
            <p className="mt-6 text-xs text-muted text-center">
              🔒 Your photo is processed in memory and never stored.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
