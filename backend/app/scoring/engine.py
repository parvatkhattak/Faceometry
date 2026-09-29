"""
Scoring Engine
===============
Combines all analysis sub-scores into the Facial Harmony Score.

S_harmony = Σ w_i × S_i

Components and default weights (EXPERIMENTAL, configurable):
  - Symmetry:          35%
  - General Proportion: 25%
  - Golden Ratio:       20%
  - Facial Thirds:      10%
  - Facial Fifths:      10%

The score is labeled "Facial Harmony Score" — it is a geometric
measurement, NOT an objective measure of beauty or attractiveness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.config import settings
from app.geometry.utils import clamp


@dataclass
class ScoreExplanation:
    """Human-readable explanation for a score component."""
    component: str
    score: float
    explanation: str


@dataclass
class HarmonyResult:
    """Final scoring result with breakdown and explanations."""
    harmony_score: float = 0.0
    symmetry_score: float = 0.0
    proportion_score: float = 0.0
    golden_ratio_score: float = 0.0
    facial_thirds_score: float = 0.0
    facial_fifths_score: float = 0.0
    explanations: list[ScoreExplanation] = field(default_factory=list)


def _generate_explanation(component: str, score: float) -> str:
    """Generate a human-readable explanation for a score component."""
    if score >= 90:
        quality = "very high"
    elif score >= 75:
        quality = "high"
    elif score >= 60:
        quality = "moderate"
    elif score >= 40:
        quality = "below average"
    else:
        quality = "low"

    explanations = {
        "Symmetry": {
            "very high": "Your facial landmarks show very low left-right deviation, indicating high bilateral symmetry.",
            "high": "Your facial landmarks show relatively low left-right deviation.",
            "moderate": "Some asymmetry is detected between the left and right sides of your face. This is completely normal.",
            "below average": "Noticeable asymmetry is detected. Note that head pose and lighting can significantly affect this measurement.",
            "low": "Significant asymmetry is detected. This may be due to head angle, lighting conditions, or natural variation.",
        },
        "Proportion": {
            "very high": "Several measured facial proportions are very close to classical reference ranges.",
            "high": "Several measured facial proportions are close to the selected reference ranges.",
            "moderate": "Facial proportions show moderate alignment with classical reference ranges.",
            "below average": "Some facial proportions differ from classical reference ranges. This represents natural diversity.",
            "low": "Facial proportions differ notably from classical reference ranges. Proportions vary widely across individuals.",
        },
        "Golden Ratio": {
            "very high": "Multiple facial ratios are very close to φ ≈ 1.618.",
            "high": "Some selected facial ratios are close to φ ≈ 1.618.",
            "moderate": "Selected facial ratios show moderate proximity to the Golden Ratio.",
            "below average": "Selected facial ratios differ from φ. The Golden Ratio is just one of many geometric references.",
            "low": "Selected facial ratios differ significantly from φ. This is common and does not imply any aesthetic judgment.",
        },
        "Facial Thirds": {
            "very high": "Your facial vertical thirds (forehead, midface, lower face) are very evenly distributed.",
            "high": "Your facial vertical thirds show relatively balanced proportions.",
            "moderate": "Facial vertical thirds show moderate balance between the three zones.",
            "below average": "Some imbalance in vertical facial thirds is detected. This is normal variation.",
            "low": "Notable variation in facial vertical thirds proportions.",
        },
        "Facial Fifths": {
            "very high": "The five horizontal facial sections are very evenly proportioned.",
            "high": "The horizontal facial fifths show relatively balanced proportions.",
            "moderate": "Horizontal facial fifths show moderate balance.",
            "below average": "Some variation in horizontal facial fifths proportions.",
            "low": "Notable variation in horizontal facial fifths proportions.",
        },
    }

    component_explanations = explanations.get(component, {})
    return component_explanations.get(quality, f"{component} score: {score:.1f}/100.")


def calculate_harmony_score(
    symmetry_score: float,
    proportion_score: float,
    golden_ratio_score: float,
    facial_thirds_score: float,
    facial_fifths_score: float,
) -> HarmonyResult:
    """
    Calculate the Facial Harmony Score from component scores.

    S_harmony = Σ w_i × S_i

    All weights are from settings and are marked as experimental.

    Args:
        symmetry_score: Symmetry analysis score (0-100).
        proportion_score: General proportion score (0-100).
        golden_ratio_score: Golden ratio proximity score (0-100).
        facial_thirds_score: Facial thirds score (0-100).
        facial_fifths_score: Facial fifths score (0-100).

    Returns:
        HarmonyResult with overall score, breakdown, and explanations.
    """
    weights = settings.scoring.weights

    harmony = (
        weights["symmetry"] * symmetry_score
        + weights["proportion"] * proportion_score
        + weights["golden_ratio"] * golden_ratio_score
        + weights["facial_thirds"] * facial_thirds_score
        + weights["facial_fifths"] * facial_fifths_score
    )
    harmony = clamp(harmony)

    # Generate explanations
    components = [
        ("Symmetry", symmetry_score),
        ("Proportion", proportion_score),
        ("Golden Ratio", golden_ratio_score),
        ("Facial Thirds", facial_thirds_score),
        ("Facial Fifths", facial_fifths_score),
    ]

    explanations = [
        ScoreExplanation(
            component=name,
            score=round(score, 1),
            explanation=_generate_explanation(name, score),
        )
        for name, score in components
    ]

    return HarmonyResult(
        harmony_score=round(harmony, 1),
        symmetry_score=round(symmetry_score, 1),
        proportion_score=round(proportion_score, 1),
        golden_ratio_score=round(golden_ratio_score, 1),
        facial_thirds_score=round(facial_thirds_score, 1),
        facial_fifths_score=round(facial_fifths_score, 1),
        explanations=explanations,
    )
