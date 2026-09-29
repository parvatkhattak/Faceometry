"""
Tests for golden ratio analysis.
"""

import pytest
import math

from app.geometry.golden_ratio import analyze_golden_ratio, RatioResult
from app.geometry.measurements import MeasurementResult


PHI = (1 + math.sqrt(5)) / 2


class TestGoldenRatio:
    def test_perfect_golden_ratio(self):
        """If all configured ratios equal φ, overall score should be very high."""
        # Set values so every configured ratio ≈ φ:
        # face_height/face_width = φ → face_width = 1/φ
        # face_width/inter_eye = φ → inter_eye = face_width/φ = 1/φ²
        # nose_length/nose_width = φ → nose_width = nose_length/φ
        # mouth_width/nose_width = φ → mouth_width = nose_width * φ = nose_length
        # face_height/hairline_to_nose = φ → hairline_to_nose = 1/φ
        fw = 1.0 / PHI
        ie = fw / PHI
        nl = 0.3
        nw = nl / PHI
        mw = nw * PHI  # = nl
        htn = 1.0 / PHI
        measurements = MeasurementResult(
            face_height=1.0,
            face_width=fw,
            face_aspect_ratio=PHI,
            nose_length=nl,
            nose_width=nw,
            nose_aspect_ratio=PHI,
            mouth_width=mw,
            inter_eye_distance=ie,
            hairline_to_nose_base=htn,
        )
        result = analyze_golden_ratio(measurements)
        assert result.overall_score > 95  # All ratios should be ≈ φ

    def test_far_from_golden_ratio(self):
        """Extreme proportions → low score."""
        measurements = MeasurementResult(
            face_height=1.0,
            face_width=1.0,  # height/width = 1.0 (far from φ)
            face_aspect_ratio=1.0,
            nose_length=0.1,
            nose_width=0.1,
            nose_aspect_ratio=1.0,
            mouth_width=0.1,
            inter_eye_distance=0.1,
            hairline_to_nose_base=0.5,
        )
        result = analyze_golden_ratio(measurements)
        assert result.overall_score < 80

    def test_returns_ratio_details(self):
        """Should return individual ratio analysis."""
        measurements = MeasurementResult(
            face_height=1.0,
            face_width=0.7,
            face_aspect_ratio=1.43,
            nose_length=0.3,
            nose_width=0.2,
            nose_aspect_ratio=1.5,
            mouth_width=0.25,
            inter_eye_distance=0.18,
            hairline_to_nose_base=0.6,
        )
        result = analyze_golden_ratio(measurements)
        assert len(result.ratios) > 0
        for r in result.ratios:
            assert r.target == pytest.approx(PHI, abs=0.001)
            assert 0 <= r.score <= 100
            assert r.deviation >= 0
