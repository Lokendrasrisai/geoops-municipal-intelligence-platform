import os
import pandas as pd
import streamlit as st
import plotly.express as px

from src.pipeline.geoops_pipeline import run_geoops_pipeline
from src.arcgis.feature_layer_loader import load_arcgis_feature_layer


st.set_page_config(
    page_title="GeoOps Municipal Intelligence Platform",
    page_icon="🛰️",
    layout="wide",
)


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #eef4f8 100%);
    }

    .hero {
        padding: 28px;
        border-radius: 22px;
        background: linear-gradient(135deg, #102A43 0%, #145374 55%, #1C7C89 100%);
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(16, 42, 67, 0.22);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 18px;
        opacity: 0.92;
        line-height: 1.5;
    }

    .card {
        padding: 20px;
        border-radius: 18px;
        background: white;
        border: 1px solid #dbe5ec;
        box-shadow: 0 6px 18px rgba(16, 42, 67, 0.06);
        margin-bottom: 16px;
    }

    .small-label {
        color: #627d98;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .big-value {
        font-size: 32px;
        font-weight: 800;
        color: #102A43;
    }

    .soft-text {
        color: #486581;
        font-size: 15px;
    }

    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #d9f99d;
        color: #365314;
        font-weight: 700;
        font-size: 13px;
    }

    .warning-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #ffedd5;
        color: #9a3412;
        font-weight: 700;
        font-size: 13px;
    }

    .danger-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #fee2e2;
        color: #991b1b;
        font-weight: 700;
        font-size: 13px;
    }

    .stButton>button {
        border-radius: 14px;
        font-weight: 700;
        height: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Demo Data
# -----------------------------
def create_demo_utility_data() -> pd.DataFrame:
    rows = []

    for i in range(1, 501):
        rows.append(
            {
                "asset_id": f"HYD-{i:05d}" if i % 19 != 0 else "",
                "condition": ["Good", "Fair", "Poor", "Critical", "", "Broken"][i % 6],
                "install_year": 2035 if i % 41 == 0 else 1945 + (i % 78),
                "last_inspection_date": "" if i % 12 == 0 else "2024-05-01",
                "diameter_in": 999 if i % 37 == 0 else [4, 6, 8, 10, 12, 16][i % 6],
                "pressure_zone": "" if i % 14 == 0 else f"Zone {chr(65 + (i % 5))}",
                "material": ["Cast Iron", "PVC", "Ductile Iron", "", "Steel"][i % 5],
                "status": ["Active", "Inactive", "Active", "Unknown"][i % 4],
                "SHAPE": None
                if i % 43 == 0
                else {"x": -89.70 + (i % 50) * 0.004, "y": 40.62 + (i // 50) * 0.006},
            }
        )

    return pd.DataFrame(rows)


# -----------------------------
# Helpers
# -----------------------------
def readiness_badge(level: str) -> str:
    if level in ["Production Ready", "Operationally Ready"]:
        return f'<span class="pill">{level}</span>'
    if level in ["Review Recommended", "Cleanup Required"]:
        return f'<span class="warning-pill">{level}</span>'
    return f'<span class="danger-pill">{level}</span>'


def score_status(score: float) -> str:
    if score >= 85:
        return "Strong"
    if score >= 70:
        return "Review"
    if score >= 60:
        return "Cleanup"
    return "Risk"


def metric_card(label: str, value, helper: str = ""):
    st.markdown(
        f"""
        <div class="card">
            <div class="small-label">{label}</div>
            <div class="big-value">{value}</div>
            <div class="soft-text">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_selected_data(data_source: str):
    df = None

    if data_source == "Demo Utility Dataset":
        df = create_demo_utility_data()
        st.sidebar.success("Loaded demo municipal utility dataset.")

    elif data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Upload municipal asset CSV",
            type=["csv"],
        )
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("CSV uploaded successfully.")

    elif data_source == "ArcGIS Feature Layer":
        st.sidebar.markdown("Paste a public ArcGIS Feature Layer URL.")
        st.sidebar.caption("Example: https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3")

        layer_url = st.sidebar.text_area(
            "ArcGIS Feature Layer URL",
            height=120,
            placeholder="https://.../FeatureServer/0 or https://.../MapServer/3",
        )

        max_records = st.sidebar.number_input(
            "Max records to load",
            min_value=100,
            max_value=50000,
            value=5000,
            step=500,
        )

        if st.sidebar.button("Load ArcGIS Layer", use_container_width=True):
            if not layer_url.strip():
                st.sidebar.error("Please paste a valid ArcGIS layer URL.")
            else:
                with st.spinner("Connecting to ArcGIS Feature Layer..."):
                    try:
                        df = load_arcgis_feature_layer(layer_url.strip(), max_records=max_records)
                        st.session_state["loaded_arcgis_df"] = df
                        st.sidebar.success(f"Loaded {len(df)} records from ArcGIS.")
                    except Exception as exc:
                        st.sidebar.error(f"ArcGIS load failed: {exc}")

        if "loaded_arcgis_df" in st.session_state:
            df = st.session_state["loaded_arcgis_df"]

    return df


def render_dataset_profile(df: pd.DataFrame):
    safe_df = df.drop(columns=["SHAPE", "geometry", "geom"], errors="ignore")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Records", f"{len(df):,}", "Features loaded into GeoOps")
    with c2:
        metric_card("Total Fields", len(df.columns), "Attributes available for review")
    with c3:
        metric_card("Missing Values", f"{int(safe_df.isna().sum().sum()):,}", "Blank cells detected")
    with c4:
        metric_card("Duplicate Rows", int(safe_df.duplicated().sum()), "Exact duplicate records")


def render_score_cards(readiness: dict):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Overall GIS Health",
            readiness["overall_gis_health_score"],
            score_status(readiness["overall_gis_health_score"]),
        )

    with c2:
        metric_card(
            "Data Quality",
            readiness["data_quality_score"],
            score_status(readiness["data_quality_score"]),
        )

    with c3:
        metric_card(
            "Utility Readiness",
            readiness["utility_network_readiness_score"],
            score_status(readiness["utility_network_readiness_score"]),
        )

    with c4:
        metric_card(
            "Asset Readiness",
            readiness["asset_management_readiness_score"],
            score_status(readiness["asset_management_readiness_score"]),
        )


# -----------------------------
# App
# -----------------------------
def main():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">GeoOps Municipal Intelligence Platform</div>
            <div class="hero-subtitle">
                ArcGIS-aligned operational intelligence for municipal GIS QA, readiness scoring,
                analyst review prioritization, and utility asset decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Control Center")

        data_source = st.radio(
            "Select Data Source",
            [
                "Demo Utility Dataset",
                "Upload CSV",
                "ArcGIS Feature Layer",
            ],
        )

        st.markdown("---")
        st.caption("GeoOps Pipeline")
        st.caption("Intake → GeoQA → Readiness → Reporting → Issue Layer")

    df = load_selected_data(data_source)

    if df is None:
        st.info("Choose a data source from the sidebar to begin.")
        return

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Overview",
            "Assessment",
            "Issue Intelligence",
            "ArcGIS Fit",
            "Exports",
            "Roadmap",
        ]
    )

    with tab1:
        st.subheader("Platform Overview")

        st.markdown(
            """
            GeoOps is designed as an **operational intelligence layer** above existing GIS workflows.

            It does not replace ArcGIS Pro, ArcGIS Online, or GIS analysts.  
            It helps teams quickly understand:

            - What is wrong with a GIS dataset
            - Which records should be reviewed first
            - Whether a dataset is ready for operational workflows
            - What issue layer or report should be created for analyst review
            """
        )

        st.markdown("### Dataset Profile")
        render_dataset_profile(df)

        st.markdown("### Dataset Preview")
        st.dataframe(df.head(40), use_container_width=True)

    with tab2:
        st.subheader("Municipal GIS Health Assessment")

        st.markdown(
            """
            Run the complete GeoOps pipeline on the loaded dataset.  
            The assessment generates readiness scores, issue summaries, recommendations, and ArcGIS-ready outputs.
            """
        )

        if st.button("Run Full GeoOps Assessment", type="primary", use_container_width=True):
            with st.spinner("Running GeoOps Intelligence Pipeline..."):
                result = run_geoops_pipeline(df)
                st.session_state["geoops_result"] = result

        if "geoops_result" in st.session_state:
            result = st.session_state["geoops_result"]
            readiness = result["readiness_summary"]
            issue_summary = result["issue_summary"]

            st.markdown("### Executive Readiness Scores")
            render_score_cards(readiness)

            st.markdown(
                f"### Readiness Level: {readiness_badge(readiness['readiness_level'])}",
                unsafe_allow_html=True,
            )

            st.markdown("### Issue Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Issues", issue_summary["total_issues"])
            c2.metric("Critical Issues", issue_summary.get("severity_breakdown", {}).get("Critical", 0))
            c3.metric("High Issues", issue_summary.get("severity_breakdown", {}).get("High", 0))

            severity_breakdown = issue_summary.get("severity_breakdown", {})
            category_breakdown = issue_summary.get("category_breakdown", {})

            left, right = st.columns(2)

            with left:
                if severity_breakdown:
                    severity_df = pd.DataFrame(
                        {
                            "Severity": list(severity_breakdown.keys()),
                            "Count": list(severity_breakdown.values()),
                        }
                    )
                    fig = px.pie(
                        severity_df,
                        names="Severity",
                        values="Count",
                        title="Issue Severity Distribution",
                        hole=0.45,
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with right:
                if category_breakdown:
                    category_df = pd.DataFrame(
                        {
                            "Category": list(category_breakdown.keys()),
                            "Count": list(category_breakdown.values()),
                        }
                    ).sort_values("Count", ascending=False)

                    fig = px.bar(
                        category_df.head(12),
                        x="Count",
                        y="Category",
                        orientation="h",
                        title="Top Issue Categories",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Recommended Actions")
            for rec in result["recommendations"]:
                st.success(rec)

    with tab3:
        st.subheader("Issue Intelligence")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]

            issues_df = pd.read_csv(outputs["issues_csv"])
            priorities_df = pd.read_csv(outputs["priorities_csv"])

            st.markdown(
                """
                This section is designed for analysts.  
                It shows the flagged records, issue categories, severity, and review priority.
                """
            )

            f1, f2 = st.columns(2)

            with f1:
                severities = sorted(issues_df["severity"].dropna().unique())
                selected_severities = st.multiselect(
                    "Filter by Severity",
                    severities,
                    default=severities,
                )

            with f2:
                categories = sorted(issues_df["issue_category"].dropna().unique())
                selected_categories = st.multiselect(
                    "Filter by Issue Category",
                    categories,
                    default=categories,
                )

            filtered = issues_df[
                issues_df["severity"].isin(selected_severities)
                & issues_df["issue_category"].isin(selected_categories)
            ]

            st.markdown("### Flagged Issue Records")
            st.dataframe(filtered, use_container_width=True)

            st.markdown("### Review Priority Ranking")
            st.dataframe(priorities_df, use_container_width=True)

    with tab4:
        st.subheader("How GeoOps Fits ArcGIS Workflows")

        st.markdown(
            """
            ### Existing Workflow

            ArcGIS Data → Manual Review → Cleanup → Delivery

            ### GeoOps-Enhanced Workflow

            ArcGIS Feature Layer / CSV  
            → GeoOps Intake  
            → GeoQA Engine  
            → Readiness Scoring  
            → Issue Layer Export  
            → Analyst Review in ArcGIS  

            ### Why This Matters

            ArcGIS remains the system of record and editing environment.

            GeoOps provides a separate intelligence layer that helps answer:

            - Which records require review first?
            - Which issue categories are most common?
            - Is this dataset ready for Utility Network workflows?
            - What should the analyst or project manager prioritize?
            - What can be exported back as an issue layer?
            """
        )

    with tab5:
        st.subheader("Generated Outputs")

        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            st.json(outputs)

            for name, path in outputs.items():
                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button(
                            label=f"Download {name}",
                            data=f,
                            file_name=os.path.basename(path),
                            use_container_width=True,
                        )

    with tab6:
        st.subheader("Product Roadmap")

        st.markdown(
            """
            ### Phase 1 — Foundation
            - Data Intake Engine
            - GeoQA Engine
            - Readiness Scoring
            - Reporting Engine
            - Issue Layer Export
            - Streamlit Platform UI

            ### Phase 2 — ArcGIS Integration
            - Public Feature Layer Input
            - Authenticated ArcGIS Online Access
            - Hosted Issue Layer Publishing
            - ArcGIS Dashboard Integration

            ### Phase 3 — Utility Intelligence
            - Asset risk scoring
            - Inspection prioritization
            - Maintenance priority ranking
            - Budget-aware decision support

            ### Phase 4 — GeoOps Copilot
            - Natural-language questions over GIS datasets
            - Automated QA summaries
            - Analyst guidance
            - Executive reporting assistant
            """
        )


if __name__ == "__main__":
    main()