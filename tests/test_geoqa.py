"""
tests/test_geoqa.py
Unit tests for the GeoQA engine and individual checks.
"""

import pandas as pd
import pytest

from src.geoqa.checks import (
    check_missing_asset_id,
    check_duplicate_asset_id,
    check_missing_geometry,
    check_missing_condition,
    check_invalid_condition,
    check_invalid_install_year,
    check_missing_inspection_date,
    check_suspicious_diameter,
)
from src.geoqa.engine import run_geoqa, summarize_issues


# ── check_missing_asset_id ────────────────────────────────────────────────────

def test_missing_asset_id_detects_empty_string():
    df = pd.DataFrame([{"asset_id": ""}])
    issues = check_missing_asset_id(df)
    assert len(issues) == 1
    assert issues[0].severity == "Critical"


def test_missing_asset_id_detects_nan():
    df = pd.DataFrame([{"asset_id": None}])
    issues = check_missing_asset_id(df)
    assert len(issues) == 1


def test_missing_asset_id_passes_valid():
    df = pd.DataFrame([{"asset_id": "WM-00001"}])
    issues = check_missing_asset_id(df)
    assert len(issues) == 0


def test_missing_asset_id_no_column():
    df = pd.DataFrame([{"other_col": "x"}])
    issues = check_missing_asset_id(df)
    assert issues == []


# ── check_duplicate_asset_id ──────────────────────────────────────────────────

def test_duplicate_asset_id_detects():
    df = pd.DataFrame([{"asset_id": "WM-001"}, {"asset_id": "WM-001"}])
    issues = check_duplicate_asset_id(df)
    assert len(issues) == 2


def test_duplicate_asset_id_passes_unique():
    df = pd.DataFrame([{"asset_id": "WM-001"}, {"asset_id": "WM-002"}])
    issues = check_duplicate_asset_id(df)
    assert len(issues) == 0


# ── check_invalid_install_year ────────────────────────────────────────────────

def test_future_install_year():
    df = pd.DataFrame([{"asset_id": "WM-001", "install_year": 2099}])
    issues = check_invalid_install_year(df)
    assert len(issues) == 1
    assert issues[0].issue_category == "Future Install Year"


def test_unrealistic_install_year():
    df = pd.DataFrame([{"asset_id": "WM-001", "install_year": 1800}])
    issues = check_invalid_install_year(df)
    assert len(issues) == 1
    assert issues[0].issue_category == "Unrealistic Install Year"


def test_valid_install_year():
    df = pd.DataFrame([{"asset_id": "WM-001", "install_year": 1975}])
    issues = check_invalid_install_year(df)
    assert len(issues) == 0


# ── check_invalid_condition ───────────────────────────────────────────────────

def test_invalid_condition_detects_bad_value():
    df = pd.DataFrame([{"asset_id": "WM-001", "condition": "Broken"}])
    issues = check_invalid_condition(df)
    assert len(issues) == 1


def test_valid_condition_passes():
    for cond in ["Excellent", "Good", "Fair", "Poor", "Critical", "Unknown"]:
        df = pd.DataFrame([{"asset_id": "WM-001", "condition": cond}])
        assert check_invalid_condition(df) == [], f"Failed for condition: {cond}"


# ── check_suspicious_diameter ─────────────────────────────────────────────────

def test_suspicious_diameter_detects_999():
    df = pd.DataFrame([{"asset_id": "WM-001", "diameter_in": 999}])
    issues = check_suspicious_diameter(df)
    assert len(issues) == 1


def test_valid_diameter_passes():
    df = pd.DataFrame([{"asset_id": "WM-001", "diameter_in": 8}])
    issues = check_suspicious_diameter(df)
    assert len(issues) == 0


# ── run_geoqa (integration) ───────────────────────────────────────────────────

def test_run_geoqa_returns_dataframe(sample_assets):
    result = run_geoqa(sample_assets)
    assert isinstance(result, pd.DataFrame)
    assert "severity" in result.columns
    assert "issue_category" in result.columns


def test_run_geoqa_finds_issues_in_dirty_data(sample_assets):
    result = run_geoqa(sample_assets)
    assert len(result) > 0, "Should detect issues in synthetic dirty data"


def test_run_geoqa_clean_data_has_fewer_issues(clean_assets):
    result = run_geoqa(clean_assets)
    # Clean data may still flag stale inspection or missing inspection,
    # but should have dramatically fewer issues
    assert len(result) < 10


def test_summarize_issues_structure(sample_assets):
    issues = run_geoqa(sample_assets)
    summary = summarize_issues(issues)
    assert "total_issues" in summary
    assert "severity_breakdown" in summary
    assert "category_breakdown" in summary
    assert summary["total_issues"] == len(issues)
