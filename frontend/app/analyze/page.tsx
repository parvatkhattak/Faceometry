"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { analyzeImage, ApiError } from "@/lib/api";
import type { AnalysisResponse } from "@/types/api";

type AnalysisState = "idle" | "uploading" | "analyzing" | "error";

export default function AnalyzePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [state, setState] = useState<AnalysisState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorIssues, setErrorIssues] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback((file: File) => {
    // Client-side validation
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError("Please upload a JPEG, PNG, or WebP image.");
      return;
    }

    const maxSize = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxSize) {
      setError(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum: 10 MB.`);
      return;
    }

    setSelectedFile(file);
    setError(null);
    setErrorIssues([]);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setState("analyzing");
    setError(null);
    setErrorIssues([]);

    try {
      const result = await analyzeImage(selectedFile);

      // Store result in sessionStorage for the results page
      sessionStorage.setItem("faceometry_result", JSON.stringify(result));
      router.push("/results");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
        setErrorIssues(err.issues);
      } else {
        setError("An unexpected error occurred. Please try again.");
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

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card-static px-6 py-4"
           style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
              <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" stroke="url(#navG2)" strokeWidth="1.5" fill="none" />
              <circle cx="14" cy="14" r="4" stroke="url(#navG2)" strokeWidth="1" fill="none" />
              <defs>
                <linearGradient id="navG2" x1="0" y1="0" x2="28" y2="28">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            <span className="font-[family-name:var(--font-display)] font-bold tracking-wider">
              FACEOMETRY
            </span>
          </Link>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center pt-24 pb-12 px-6">
        <div className="w-full max-w-xl mx-auto">
          <div className="text-center mb-8 animate-fadeInUp">
            <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold mb-2">
              <span className="gradient-text">Analyze Your Face</span>
            </h1>
            <p className="text-[var(--color-text-muted)] text-sm">
              Upload a front-facing photograph to analyze facial geometry and proportions.
            </p>
          </div>

          {/* Upload zone */}
          {!preview ? (
            <div
              className={`upload-zone animate-fadeInUp-delay-1 ${dragOver ? "drag-over" : ""}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
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

              <div className="mb-4">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="mx-auto opacity-40">
                  <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <circle cx="18" cy="22" r="4" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <path d="M6 34L16 26L22 30L32 20L42 28" stroke="currentColor" strokeWidth="1.5" fill="none" />
                  <path d="M24 4V14M19 9L24 4L29 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" fill="none" />
                </svg>
              </div>

              <p className="font-[family-name:var(--font-display)] font-semibold mb-1">
                Drop your photo here
              </p>
              <p className="text-sm text-[var(--color-text-muted)] mb-3">
                or click to browse
              </p>
              <p className="text-xs text-[var(--color-text-muted)]">
                JPEG, PNG, or WebP · Max 10 MB · Front-facing photo recommended
              </p>
            </div>
          ) : (
            /* Preview + Analyze */
            <div className="animate-fadeInUp">
              <div className="glass-card-static overflow-hidden mb-4">
                <div className="relative aspect-[4/5] max-h-[400px] overflow-hidden flex items-center justify-center bg-black/20">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-w-full max-h-full object-contain"
                  />
                  {state === "analyzing" && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                      <div className="text-center">
                        <LoadingSpinner />
                        <p className="mt-4 font-[family-name:var(--font-display)] text-sm">
                          Analyzing facial geometry...
                        </p>
                        <p className="text-xs text-[var(--color-text-muted)] mt-1">
                          Detecting landmarks · Measuring proportions · Calculating scores
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4 border-t border-[var(--color-border)]">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium truncate max-w-[200px]">{selectedFile?.name}</p>
                      <p className="text-xs text-[var(--color-text-muted)]">
                        {selectedFile && (selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={handleReset}
                      className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-accent-rose)] transition-colors"
                      disabled={state === "analyzing"}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              {/* Error display */}
              {error && (
                <div className="glass-card-static p-4 mb-4 border-[var(--color-accent-rose)]" style={{ borderColor: 'rgba(244, 63, 94, 0.3)' }}>
                  <div className="flex items-start gap-3">
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" className="mt-0.5 flex-shrink-0">
                      <circle cx="9" cy="9" r="8" stroke="#f43f5e" strokeWidth="1.5" fill="none" />
                      <path d="M9 5V10M9 12.5V13" stroke="#f43f5e" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                    <div>
                      <p className="text-sm text-[var(--color-accent-rose)] font-medium">{error}</p>
                      {errorIssues.length > 0 && (
                        <ul className="mt-2 space-y-1">
                          {errorIssues.map((issue, i) => (
                            <li key={i} className="text-xs text-[var(--color-text-muted)]">• {issue}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={handleAnalyze}
                  disabled={state === "analyzing"}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <span>{state === "analyzing" ? "Analyzing..." : "Analyze"}</span>
                </button>
                <button
                  onClick={handleReset}
                  disabled={state === "analyzing"}
                  className="btn-secondary disabled:opacity-50"
                >
                  Reset
                </button>
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="mt-8 animate-fadeInUp-delay-3">
            <p className="text-xs text-[var(--color-text-muted)] text-center mb-3 font-[family-name:var(--font-display)]">
              For best results:
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                "Front-facing photo",
                "Good lighting",
                "Clear, sharp image",
                "One person only",
              ].map((tip) => (
                <div
                  key={tip}
                  className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] glass-card-static px-3 py-2"
                >
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6L5 9L10 3" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  {tip}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" className="animate-spin">
      <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
      <circle
          cx="24" cy="24" r="20" fill="none"
          stroke="url(#spinGrad)" strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="80 50"
        />
      <defs>
        <linearGradient id="spinGrad" x1="0" y1="0" x2="48" y2="48">
          <stop offset="0%" stopColor="#00d4ff" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
    </svg>
  );
}
