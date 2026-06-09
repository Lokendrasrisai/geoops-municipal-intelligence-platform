"""
src/pipeline/geoops_pipeline.py
Orchestrates the full GeoOps analysis pipeline.

Order of operations:
    1. GeoQA        — detect data quality issues
    2. Readiness    — score dataset health
    3. Risk Engine  — score individual asset risk
    4. Hotspot      — spatial pressure-zone analysis
    5. Explainability — explain top-N high-risk assets
    6. Recommendations — per-dataset action items
    7. Export       — CSV, GeoJSON outputs
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.arcgis.issue_export import export_issue_geojson
from src.geoqa.engine import run_geoqa, summarize_issues
from src.readiness.scoring import (
    assign_feature_review_priorities,
    build_readiness_summary,
)
from src.reporting.report_builder import build_report
from src.utility_intelligence.risk_engine import build_utility_intelligence
from src.spatial.hotspot_engine import (
    build_pressure_zone_hotspots,
    generate_hotspot_insights,
)
from src.intelligence.explainability import explain_dataset
from src.intelligence.recommendations import generate_dataset_recommendations

logger = logging.getLogger(__name__)


def run_geoops_pipeline(
    df: pd.DataFrame,
    output_dir: str = "outputs",
    export_issue_layer: bool = True,
    explain_top_n: int = 10,
) -> dict:
    """
    Run the full GeoOps intelligence pipeline on a DataFrame of assets.

    Args:
        df:                 Input asset DataFrame
        output_dir:         Directory to write CSV/GeoJSON outputs
        export_issue_layer: Whether to export a GeoJSON issue layer
        explain_top_n:      Number of high-risk assets to explain

    Returns:
        A dict containing all analysis results and output file paths.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # ── 1. GeoQA ─────────────────────────────────────────────────────────────
    logger.info("Running GeoQA checks...")
    issues_df     = run_geoqa(df)
    issue_summary = summarize_issues(issues_df)

    # ── 2. Readiness scoring ──────────────────────────────────────────────────
    logger.info("Scoring dataset readiness...")
    priorities_df    = assign_feature_review_priorities(issues_df)
    readiness_summary = build_readiness_summary(issues_df)

    # ── 3. Utility risk engine ────────────────────────────────────────────────
    logger.info("Computing asset risk scores...")
    utility_df   = build_utility_intelligence(df, issues_df)
    utility_path = output_path / "geoops_utility_intelligence.csv"
    utility_df.to_csv(utility_path, index=False)

    # ── 4. Spatial hotspot analysis ───────────────────────────────────────────
    hotspots_df     = pd.DataFrame()
    hotspot_insights: list[str] = []

    if "pressure_zone" in df.columns:
        logger.info("Building pressure zone hotspots...")
        hotspots_df     = build_pressure_zone_hotspots(df, utility_df)
        hotspot_insights = generate_hotspot_insights(hotspots_df)

    hotspots_path = output_path / "geoops_spatial_hotspots.csv"
    hotspots_df.to_csv(hotspots_path, index=False)

    # ── 5. Explainability ─────────────────────────────────────────────────────
    logger.info("Generating asset explanations...")
    explanations: list[dict] = []
    try:
        explanations = explain_dataset(df, utility_df, issues_df, top_n=explain_top_n)
    except Exception as exc:
        logger.warning("Explainability failed: %s", exc)

    # ── 6. Recommendations ────────────────────────────────────────────────────
    logger.info("Generating dataset recommendations...")
    recommendations = generate_dataset_recommendations(issues_df, utility_df)

    # ── 7. Export ─────────────────────────────────────────────────────────────
    report = build_report(readiness_summary, issues_df, priorities_df)

    issues_csv    = output_path / "geoops_issues.csv"
    priorities_csv = output_path / "geoops_review_priorities.csv"
    issues_df.to_csv(issues_csv, index=False)
    priorities_df.to_csv(priorities_csv, index=False)

    issue_layer_path: Optional[Path] = None
    if export_issue_layer and not issues_df.empty:
        try:
            issue_layer_path = export_issue_geojson(
                issues_df, df, output_path / "geoops_issue_layer.geojson"
            )
        except Exception as exc:
            logger.warning("GeoJSON export failed: %s", exc)

    logger.info("Pipeline complete.")

    return {
        "issue_summary":     issue_summary,
        "readiness_summary": readiness_summary,
        "report":            report,
        "recommendations":   recommendations,
        "hotspot_insights":  hotspot_insights,
        "explanations":      explanations,
        "outputs": {
            "issues_csv":              str(issues_csv),
            "priorities_csv":          str(priorities_csv),
            "utility_intelligence_csv": str(utility_path),
            "spatial_hotspots_csv":    str(hotspots_path),
            "issue_layer_geojson":     str(issue_layer_path) if issue_layer_path else None,
        },
    }
