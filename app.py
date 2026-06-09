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


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f6fbff 0%, #edf5f8 100%);
    }
    .hero {
        padding: 30px;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #164e63 52%, #0f766e 100%);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.24);
    }
    .hero-title {
        font-size: 44px;
        font-weight: 850;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 18px;
        opacity: 0.94;
        line-height: 1.5;
    }
    .card {
        padding: 20px;
        border-radius: 18px;
        background: white;
        border: 1px solid #dbe7ee;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
        margin-bottom: 16px;
    }
    .small-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .big-value {
        font-size: 32px;
        font-weight: 850;
        color: #0f172a;
    }
    .soft-text {
        color: #475569;
        font-size: 15px;
    }
    .pill {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-weight: 800;
        font-size: 13px;
    }
    .warning-pill {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: #ffedd5;
        color: #9a3412;
        font-weight: 800;
        font-size: 13px;
    }
    .danger-pill {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: #fee2e2;
        color: #991b1b;
        font-weight: 800;
        font-size: 13px;
    }
    .stButton>button {
        border-radius: 14px;
        font-weight: 800;
        height: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        uploaded_file = st.sidebar.file_uploader("Upload municipal asset CSV", type=["csv"])
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
        metric_card("Overall GIS Health", readiness["overall_gis_health_score"], score_status(readiness["overall_gis_health_score"]))
    with c2:
        metric_card("Data Quality", readiness["data_quality_score"], score_status(readiness["data_quality_score"]))
    with c3:
        metric_card("Utility Readiness", readiness["utility_network_readiness_score"], score_status(readiness["utility_network_readiness_score"]))
    with c4:
        metric_card("Asset Readiness", readiness["asset_management_readiness_score"], score_status(readiness["asset_management_readiness_score"]))


def main():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">GeoOps Municipal Intelligence Platform</div>
            <div class="hero-subtitle">
                Municipal decision intelligence for GIS quality, utility asset risk,
                spatial hotspots, readiness scoring, and ArcGIS-aligned review workflows.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Control Center")
        data_source = st.radio(
            "Select Data Source",
            ["Demo Utility Dataset", "Upload CSV", "ArcGIS Feature Layer"],
        )
        st.markdown("---")
        st.caption("Pipeline")
        st.caption("Intake → GeoQA → Readiness → Utility Intelligence → Spatial Intelligence → Reporting")

    df = load_selected_data(data_source)

    if df is None:
        st.info("Choose a data source from the sidebar to begin.")
        return

    tabs = st.tabs(
        [
            "Overview",
            "Assessment",
            "Issue Intelligence",
            "Utility Intelligence",
            "Spatial Intelligence",
            "ArcGIS Fit",
            "Exports",
            "Roadmap",
        ]
    )

    with tabs[0]:
        st.subheader("Platform Overview")
        st.markdown(
            """
            GeoOps is an **operational intelligence layer** above existing GIS workflows.

            It helps municipalities and GIS consulting teams understand:
            - What is wrong with the GIS dataset
            - Which assets require review first
            - Where operational risk is concentrated
            - Whether data is ready for Utility Network or asset management workflows
            """
        )
        st.markdown("### Dataset Profile")
        render_dataset_profile(df)
        st.markdown("### Dataset Preview")
        st.dataframe(df.head(50), use_container_width=True)

    with tabs[1]:
        st.subheader("Municipal GIS Health Assessment")
        if st.button("Run Full GeoOps Assessment", type="primary", use_container_width=True):
            with st.spinner("Running complete GeoOps decision intelligence pipeline..."):
                result = run_geoops_pipeline(df)
                st.session_state["geoops_result"] = result

        if "geoops_result" in st.session_state:
            result = st.session_state["geoops_result"]
            readiness = result["readiness_summary"]
            issue_summary = result["issue_summary"]

            st.markdown("### Executive Readiness Scores")
            render_score_cards(readiness)
            st.markdown(f"### Readiness Level: {readiness_badge(readiness['readiness_level'])}", unsafe_allow_html=True)

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
                        {"Severity": list(severity_breakdown.keys()), "Count": list(severity_breakdown.values())}
                    )
                    fig = px.pie(severity_df, names="Severity", values="Count", title="Issue Severity Distribution", hole=0.45)
                    st.plotly_chart(fig, use_container_width=True)

            with right:
                if category_breakdown:
                    category_df = pd.DataFrame(
                        {"Category": list(category_breakdown.keys()), "Count": list(category_breakdown.values())}
                    ).sort_values("Count", ascending=False)
                    fig = px.bar(category_df.head(12), x="Count", y="Category", orientation="h", title="Top Issue Categories")
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Recommended Actions")
            for rec in result["recommendations"]:
                st.success(rec)

    with tabs[2]:
        st.subheader("Issue Intelligence")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            issues_df = pd.read_csv(outputs["issues_csv"])
            priorities_df = pd.read_csv(outputs["priorities_csv"])

            f1, f2 = st.columns(2)
            with f1:
                severities = sorted(issues_df["severity"].dropna().unique())
                selected_severities = st.multiselect("Filter by Severity", severities, default=severities)
            with f2:
                categories = sorted(issues_df["issue_category"].dropna().unique())
                selected_categories = st.multiselect("Filter by Issue Category", categories, default=categories)

            filtered = issues_df[
                issues_df["severity"].isin(selected_severities)
                & issues_df["issue_category"].isin(selected_categories)
            ]

            st.markdown("### Flagged Issue Records")
            st.dataframe(filtered, use_container_width=True)

            st.markdown("### Review Priority Ranking")
            st.dataframe(priorities_df, use_container_width=True)

    with tabs[3]:
        st.subheader("Utility Intelligence")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            utility_df = pd.read_csv(outputs["utility_intelligence_csv"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Highest Risk Score", int(utility_df["utility_risk_score"].max()))
            c2.metric("Critical Priority Assets", int((utility_df["maintenance_priority"] == "Critical Priority").sum()))
            c3.metric("High Priority Assets", int((utility_df["maintenance_priority"] == "High Priority").sum()))

            priority_counts = utility_df["maintenance_priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]

            fig = px.bar(priority_counts, x="Priority", y="Count", title="Maintenance Priority Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Top Highest-Risk Assets")
            st.dataframe(utility_df.head(25), use_container_width=True)

    with tabs[4]:
        st.subheader("Spatial Intelligence")
        if "geoops_result" not in st.session_state:
            st.warning("Run the assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]
            hotspots_path = outputs["spatial_hotspots_csv"]

            if not hotspots_path or not os.path.exists(hotspots_path):
                st.info("No spatial hotspot output available. Dataset may not contain pressure_zone.")
            else:
                hotspots_df = pd.read_csv(hotspots_path)

                if hotspots_df.empty:
                    st.info("No hotspot patterns detected.")
                else:
                    st.markdown("### Pressure Zone Risk Hotspots")
                    st.dataframe(hotspots_df, use_container_width=True)

                    fig = px.bar(
                        hotspots_df,
                        x="pressure_zone",
                        y="avg_risk_score",
                        title="Average Utility Risk by Pressure Zone",
                        text="avg_risk_score",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("### Hotspot Insights")
                    for insight in st.session_state["geoops_result"]["hotspot_insights"]:
                        st.warning(insight)

    with tabs[5]:
        st.subheader("How GeoOps Fits ArcGIS Workflows")
        st.markdown(
            """
            **Existing GIS workflow**

            ArcGIS Data → Manual Review → Cleanup → Delivery

            **GeoOps-enhanced workflow**

            ArcGIS Feature Layer / CSV  
            → GeoOps Intake  
            → GeoQA Engine  
            → Readiness Scoring  
            → Utility + Spatial Intelligence  
            → Issue Layer Export  
            → Analyst Review in ArcGIS  

            ArcGIS remains the system of record. GeoOps provides decision intelligence around it.
            """
        )

    with tabs[6]:
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

    with tabs[7]:
        st.subheader("Product Roadmap")
        st.markdown(
            """
            ### Phase 1 — Foundation
            - Data Intake
            - GeoQA
            - Readiness Scoring
            - Reporting
            - Issue Layer Export

            ### Phase 2 — Decision Intelligence
            - Utility Intelligence
            - Spatial Hotspots
            - Operational Risk Summaries

            ### Phase 3 — ArcGIS Integration
            - Authenticated ArcGIS Online Access
            - Hosted Issue Layer Publishing
            - Dashboard Integration

            ### Phase 4 — GeoOps Copilot
            - Natural-language GIS analysis
            - Automated QA summaries
            - Analyst decision assistant
            """
        )


if __name__ == "__main__":
    main()
