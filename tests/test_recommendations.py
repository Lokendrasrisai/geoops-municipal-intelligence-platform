"""
tests/test_recommendations.py
Unit tests for the recommendation engine.
"""

import pandas as pd
import pytest
from src.intelligence.recommendations import (
    generate_asset_recommendation,
    generate_dataset_recommendations,
)


# ── generate_asset_recommendation ────────────────────────────────────────────

def test_high_risk_score_escalates():
    result = generate_asset_recommendation(80)
    assert result["action"] == "Escalate"


def test_medium_risk_inspects():
    result = generate_asset_recommendation(38)
    assert result["action"] == "Inspect"


def test_low_risk_routine():
    result = generate_asset_recommendation(5)
    assert result["action"] == "Routine"


def test_missing_geometry_triggers_validate():
    result = generate_asset_recommendation(15, issues=["Missing Geometry"])
    assert result["action"] == "Validate Data"


def test_result_has_rationale():
    result = generate_asset_recommendation(55)
    assert "rationale" in result
    assert isinstance(result["rationale"], str)
    assert len(result["rationale"]) > 10


# ── generate_dataset_recommendations ─────────────────────────────────────────

def test_empty_issues_returns_clean_message():
    empty = pd.DataFrame(columns=["issue_category", "severity"])
    results = generate_dataset_recommendations(empty)
    assert isinstance(results, list)
    assert len(results) == 1
    assert "No significant" in results[0]


def test_critical_issues_appear_first(minimal_issues_df):
    results = generate_dataset_recommendations(minimal_issues_df)
    assert isinstance(results, list)
    # First recommendation should mention critical issues
    combined = " ".join(results[:2]).lower()
    assert any(kw in combined for kw in ["critical", "identifier", "missing"])


def test_recommendations_are_strings(minimal_issues_df):
    results = generate_dataset_recommendations(minimal_issues_df)
    for r in results:
        assert isinstance(r, str)
        assert len(r) > 10


def test_large_dirty_dataset_generates_multiple_recs(sample_assets):
    from src.geoqa.engine import run_geoqa
    from src.utility_intelligence.risk_engine import build_utility_intelligence
    issues = run_geoqa(sample_assets)
    utility = build_utility_intelligence(sample_assets)
    recs = generate_dataset_recommendations(issues, utility)
    assert len(recs) >= 3, "Dirty dataset should generate multiple recommendations"
