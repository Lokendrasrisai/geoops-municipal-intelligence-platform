"""
tests/test_risk.py
Unit tests for readiness scoring and utility risk engine.
"""

import pandas as pd
import pytest

from src.readiness.scoring import (
    calculate_data_quality_score,
    build_readiness_summary,
    assign_feature_review_priorities,
    classify_readiness,
)
from src.utility_intelligence.risk_engine import (
    build_utility_intelligence,
    map_risk_to_priority,
    calculate_asset_age_score,
    calculate_condition_score,
)


# ── Readiness scoring ─────────────────────────────────────────────────────────

def test_data_quality_score_empty_issues():
    empty = pd.DataFrame(columns=["severity"])
    assert calculate_data_quality_score(empty) == 100.0


def test_data_quality_score_decreases_with_issues(minimal_issues_df):
    score = calculate_data_quality_score(minimal_issues_df)
    assert score < 100.0
    assert score >= 0.0


def test_readiness_summary_keys(minimal_issues_df):
    summary = build_readiness_summary(minimal_issues_df)
    for key in [
        "data_quality_score",
        "utility_network_readiness_score",
        "asset_management_readiness_score",
        "overall_gis_health_score",
        "readiness_level",
    ]:
        assert key in summary, f"Missing key: {key}"


def test_readiness_scores_are_bounded(minimal_issues_df):
    summary = build_readiness_summary(minimal_issues_df)
    for key in ["data_quality_score", "utility_network_readiness_score",
                "asset_management_readiness_score", "overall_gis_health_score"]:
        assert 0.0 <= summary[key] <= 100.0


def test_classify_readiness_thresholds():
    assert classify_readiness(95) == "Production Ready"
    assert classify_readiness(82) == "Operationally Ready"
    assert classify_readiness(74) == "Review Recommended"
    assert classify_readiness(62) == "Cleanup Required"
    assert classify_readiness(45) == "High Risk"
    assert classify_readiness(20) == "Not Ready"


# ── Asset age score ───────────────────────────────────────────────────────────

def test_age_score_old_pipe():
    score = calculate_asset_age_score(1945)
    assert score == 25   # > 75 years


def test_age_score_new_pipe():
    score = calculate_asset_age_score(2020)
    assert score == 0    # < 10 years


def test_age_score_invalid():
    score = calculate_asset_age_score("not_a_year")
    assert score == 10   # default fallback


# ── Condition score ───────────────────────────────────────────────────────────

def test_condition_score_critical():
    assert calculate_condition_score("Critical") == 40


def test_condition_score_good():
    assert calculate_condition_score("Good") == 5


def test_condition_score_missing():
    assert calculate_condition_score("") == 15
    assert calculate_condition_score(None) == 15


# ── Risk priority mapping ─────────────────────────────────────────────────────

def test_risk_priority_mapping():
    assert map_risk_to_priority(80) == "Critical Priority"
    assert map_risk_to_priority(60) == "High Priority"
    assert map_risk_to_priority(40) == "Medium Priority"
    assert map_risk_to_priority(20) == "Low Priority"
    assert map_risk_to_priority(5)  == "Routine"


# ── build_utility_intelligence (integration) ──────────────────────────────────

def test_utility_intelligence_returns_dataframe(sample_assets):
    result = build_utility_intelligence(sample_assets)
    assert isinstance(result, pd.DataFrame)
    assert "utility_risk_score" in result.columns
    assert "maintenance_priority" in result.columns


def test_utility_intelligence_scores_bounded(sample_assets):
    result = build_utility_intelligence(sample_assets)
    assert result["utility_risk_score"].between(0, 100).all()


def test_utility_intelligence_sorted_descending(sample_assets):
    result = build_utility_intelligence(sample_assets)
    scores = result["utility_risk_score"].tolist()
    assert scores == sorted(scores, reverse=True)
