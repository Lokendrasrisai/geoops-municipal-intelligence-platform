"""
tests/test_explainability.py
Unit tests for the explainability layer.
"""

import pytest
from src.intelligence.explainability import explain_asset, explain_dataset
from src.utility_intelligence.risk_engine import build_utility_intelligence


# ── explain_asset ─────────────────────────────────────────────────────────────

def test_explain_asset_returns_required_keys():
    result = explain_asset(
        asset_id="WM-00001",
        install_year=1955,
        condition="Poor",
        last_inspection_date="2019-01-01",
        diameter_in=8,
        risk_score=72,
    )
    for key in ["asset_id", "risk_score", "action", "narrative", "drivers"]:
        assert key in result, f"Missing key: {key}"


def test_explain_asset_narrative_is_string():
    result = explain_asset("WM-00001", 1955, "Poor", "2019-01-01", 8, 72)
    assert isinstance(result["narrative"], str)
    assert len(result["narrative"]) > 20


def test_explain_asset_high_risk_action():
    result = explain_asset("WM-00001", 1940, "Critical", "", 16, 95)
    assert result["action"] in ("Escalate", "Replace")


def test_explain_asset_low_risk_action():
    result = explain_asset("WM-00001", 2018, "Excellent", "2024-01-01", 8, 5)
    assert result["action"] in ("Routine", "Monitor", "Validate Data")


def test_explain_asset_drivers_list():
    result = explain_asset("WM-00001", 1955, "Poor", "2019-01-01", 8, 72)
    assert isinstance(result["drivers"], list)
    assert len(result["drivers"]) >= 3


def test_explain_asset_missing_condition():
    result = explain_asset("WM-00001", 1975, "", "2021-01-01", 8, 40)
    driver_factors = [d["factor"] for d in result["drivers"]]
    assert "Condition" in driver_factors


def test_explain_asset_qa_penalties():
    result = explain_asset("WM-00001", 1975, "Fair", "2022-01-01", 8, 55,
                            qa_issue_count=3, critical_issue_count=1)
    driver_factors = [d["factor"] for d in result["drivers"]]
    assert "Data Quality Issues" in driver_factors or "Critical QA Flags" in driver_factors


# ── explain_dataset ───────────────────────────────────────────────────────────

def test_explain_dataset_returns_list(sample_assets):
    utility_df = build_utility_intelligence(sample_assets)
    results = explain_dataset(sample_assets, utility_df, top_n=5)
    assert isinstance(results, list)
    assert len(results) <= 5


def test_explain_dataset_top_n_respected(sample_assets):
    utility_df = build_utility_intelligence(sample_assets)
    results = explain_dataset(sample_assets, utility_df, top_n=3)
    assert len(results) == 3


def test_explain_dataset_each_has_required_keys(sample_assets):
    utility_df = build_utility_intelligence(sample_assets)
    results = explain_dataset(sample_assets, utility_df, top_n=5)
    for r in results:
        assert "asset_id" in r
        assert "risk_score" in r
        assert "narrative" in r
