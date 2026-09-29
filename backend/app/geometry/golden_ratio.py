"""
Golden Ratio Analysis Module
==============================
Measures how close selected facial ratios are to φ (the Golden Ratio).

φ = (1 + √5) / 2 ≈ 1.618

IMPORTANT: This module does NOT claim that every facial measurement
should ideally equal φ. Only ratios explicitly listed in the configuration
are analyzed. The result is called "Golden-Ratio Proximity" — it is a
mathematical measurement, not an objective beauty score.

For each ratio:
  Deviation: D_i = |R_i - φ| / φ
  Score: S_i = max(0, 100 * (1 - D_i))
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.config import settings
from app.geometry.measurements import MeasurementResult
from app.geometry.utils import ratio, clamp


@dataclass
class RatioResult:
    """Analysis of a single ratio vs. φ."""
    name: str
    value: float       # Measured ratio
    target: float      # φ ≈ 1.618
    deviation: float   # Relative deviation from φ
    score: float       # Proximity score (0-100)


@dataclass
class GoldenRatioResult:
    """Complete golden ratio analysis."""
    ratios: list[RatioResult] = field(default_factory=list)
    overall_score: float = 0.0


def analyze_golden_ratio(measurements: MeasurementResult) -> GoldenRatioResult:
    """
    Analyze how close selected facial ratios are to the Golden Ratio.

    Only ratios configured in settings.golden_ratio.analyzed_ratios are
    analyzed. The configuration is easy to modify.

    Args:
        measurements: Normalized facial measurements.

    Returns:
        GoldenRatioResult with per-ratio breakdown and aggregate score.
    """
    phi = settings.golden_ratio.PHI
    meas_dict = measurements.to_dict()

    ratio_results: list[RatioResult] = []

    for config_entry in settings.golden_ratio.analyzed_ratios:
        name = config_entry["name"]
        numerator_key = config_entry["numerator"]
        denominator_key = config_entry["denominator"]

        numerator_val = meas_dict.get(numerator_key, 0.0)
        denominator_val = meas_dict.get(denominator_key, 0.0)

        if numerator_val <= 0 or denominator_val <= 0:
            continue

        measured_ratio = ratio(numerator_val, denominator_val)

        # Deviation from φ
        deviation = abs(measured_ratio - phi) / phi

        # Score: max(0, 100 * (1 - deviation))
        score = clamp(100.0 * (1.0 - deviation))

        ratio_results.append(
            RatioResult(
                name=name,
                value=round(measured_ratio, 4),
                target=round(phi, 4),
                deviation=round(deviation, 4),
                score=round(score, 1),
            )
        )

    # Overall score: average of individual ratio scores
    if ratio_results:
        overall = sum(r.score for r in ratio_results) / len(ratio_results)
    else:
        overall = 0.0

    return GoldenRatioResult(
        ratios=ratio_results,
        overall_score=round(clamp(overall), 1),
    )
