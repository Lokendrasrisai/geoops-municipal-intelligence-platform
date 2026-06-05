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
from src.reporting.recommendations import generate_recommendations


def run_geoops_pipeline(
    df: pd.DataFrame,
    output_dir: str = "outputs",
    export_issue_layer: bool = True,
) -> dict:

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    issues_df = run_geoqa(df)

    issue_summary = summarize_issues(
        issues_df
    )

    priorities_df = (
        assign_feature_review_priorities(
            issues_df
        )
    )

    readiness_summary = (
        build_readiness_summary(
            issues_df
        )
    )

    report = build_report(
        readiness_summary,
        issues_df,
        priorities_df,
    )

    recommendations = (
        generate_recommendations(
            issues_df
        )
    )

    issues_csv = (
        output_path /
        "geoops_issues.csv"
    )

    priorities_csv = (
        output_path /
        "geoops_review_priorities.csv"
    )

    issues_df.to_csv(
        issues_csv,
        index=False,
    )

    priorities_df.to_csv(
        priorities_csv,
        index=False,
    )

    issue_layer_path: Optional[
        Path
    ] = None

    if (
        export_issue_layer
        and not issues_df.empty
    ):

        try:

            issue_layer_path = (
                export_issue_geojson(
                    issues_df,
                    df,
                    output_path /
                    "geoops_issue_layer.geojson",
                )
            )

        except Exception as exc:

            print(
                f"Warning: {exc}"
            )

    return {
        "issue_summary":
            issue_summary,
        "readiness_summary":
            readiness_summary,
        "report":
            report,
        "recommendations":
            recommendations,
        "outputs": {
            "issues_csv":
                str(issues_csv),
            "priorities_csv":
                str(priorities_csv),
            "issue_layer_geojson":
                str(issue_layer_path)
                if issue_layer_path
                else None,
        },
    }
