"""
Tests for scoring engine.
"""

import pytest

from app.scoring.engine import calculate_harmony_score, _generate_explanation


class TestHarmonyScore:
    def test_perfect_scores(self):
        """All 100s → harmony should be 100."""
        result = calculate_harmony_score(100, 100, 100, 100, 100)
        assert result.harmony_score == pytest.approx(100.0)

    def test_zero_scores(self):
        """All 0s → harmony should be 0."""
        result = calculate_harmony_score(0, 0, 0, 0, 0)
        assert result.harmony_score == pytest.approx(0.0)

    def test_weighted_calculation(self):
        """Verify the weighted sum is correct."""
        # Default weights: sym=0.35, prop=0.25, gold=0.20, thirds=0.10, fifths=0.10
        result = calculate_harmony_score(80, 70, 60, 50, 40)
        expected = 0.35 * 80 + 0.25 * 70 + 0.20 * 60 + 0.10 * 50 + 0.10 * 40
        assert result.harmony_score == pytest.approx(expected, abs=0.1)

    def test_has_explanations(self):
        """Every component gets an explanation."""
        result = calculate_harmony_score(80, 70, 60, 50, 40)
        assert len(result.explanations) == 5
        components = {e.component for e in result.explanations}
        assert "Symmetry" in components
        assert "Proportion" in components
        assert "Golden Ratio" in components
        assert "Facial Thirds" in components
        assert "Facial Fifths" in components

    def test_scores_stored_correctly(self):
        result = calculate_harmony_score(90, 85, 80, 75, 70)
        assert result.symmetry_score == 90.0
        assert result.proportion_score == 85.0
        assert result.golden_ratio_score == 80.0
        assert result.facial_thirds_score == 75.0
        assert result.facial_fifths_score == 70.0


class TestExplanations:
    def test_high_symmetry(self):
        text = _generate_explanation("Symmetry", 95)
        assert "very low" in text.lower() or "high" in text.lower()

    def test_low_golden_ratio(self):
        text = _generate_explanation("Golden Ratio", 30)
        assert "aesthetic judgment" in text.lower() or "differ" in text.lower()

    def test_unknown_component(self):
        text = _generate_explanation("Unknown", 50)
        assert "50" in text  # Falls back to generic
