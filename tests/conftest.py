"""
tests/conftest.py
Shared pytest fixtures for the GeoOps test suite.
"""

import pandas as pd
import pytest


@pytest.fixture
def sample_assets() -> pd.DataFrame:
    """500-row synthetic water main dataset mirroring data/sample_water_mains.csv."""
    rows = []
    for i in range(1, 501):
        rows.append({
            "asset_id":             f"WM-{i:05d}" if i % 20 != 0 else "",
            "install_year":         1945 + (i % 78) if i % 41 != 0 else 2099,
            "condition":            ["Excellent", "Good", "Fair", "Poor", "Critical", ""][i % 6],
            "material":             ["Cast Iron", "PVC", "Ductile Iron", "", "Steel"][i % 5],
            "diameter_in":          [4, 6, 8, 10, 12, 999][i % 6],
            "pressure_zone":        f"Zone {chr(65 + (i % 5))}" if i % 14 != 0 else "",
            "status":               ["Active", "Inactive", "Active", "Unknown"][i % 4],
            "last_inspection_date": "" if i % 12 == 0 else "2022-05-01",
            "latitude":             40.62 + (i // 50) * 0.006,
            "longitude":            -89.70 + (i % 50) * 0.004,
        })
    return pd.DataFrame(rows)


@pytest.fixture
def clean_assets() -> pd.DataFrame:
    """A small, perfectly clean DataFrame — should produce zero QA issues."""
    return pd.DataFrame([
        {
            "asset_id": f"WM-{i:05d}",
            "install_year": 2010,
            "condition": "Good",
            "material": "PVC",
            "diameter_in": 8,
            "pressure_zone": "Zone A",
            "status": "Active",
            "last_inspection_date": "2024-01-15",
            "latitude": 40.63,
            "longitude": -89.71,
        }
        for i in range(1, 21)
    ])


@pytest.fixture
def minimal_issues_df() -> pd.DataFrame:
    """A small issues DataFrame for testing readiness/scoring functions."""
    return pd.DataFrame([
        {"feature_index": 0, "asset_id": "WM-00001", "issue_category": "Missing Asset ID",      "severity": "Critical", "issue_description": "", "recommended_action": ""},
        {"feature_index": 1, "asset_id": "WM-00002", "issue_category": "Missing Inspection Date","severity": "High",     "issue_description": "", "recommended_action": ""},
        {"feature_index": 2, "asset_id": "WM-00003", "issue_category": "Invalid Condition",      "severity": "Medium",   "issue_description": "", "recommended_action": ""},
    ])
