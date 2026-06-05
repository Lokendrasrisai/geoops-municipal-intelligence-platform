import pandas as pd
import streamlit as st
import plotly.express as px

from src.pipeline.geoops_pipeline import run_geoops_pipeline


st.set_page_config(
    page_title="GeoOps Municipal Intelligence Platform",
    page_icon="🛰️",
    layout="wide",
)


def create_demo_utility_data() -> pd.DataFrame:
    rows = []
    for i in range(1, 151):
        rows.append(
            {
                "asset_id": f"HYD-{i:04d}" if i % 17 != 0 else "",
                "condition": ["Good", "Fair", "Poor", "Critical", "", "Broken"][i % 6],
                "install_year": 2035 if i % 29 == 0 else 1950 + (i % 70),
                "last_inspection_date": "" if i % 13 == 0 else "2024-05-01",
                "diameter_in": 999 if i % 31 == 0 else [4, 6, 8, 10, 12][i % 5],
                "pressure_zone": "" if i % 11 == 0 else f"Zone {chr(65 + (i % 4))}",
                "material": ["Cast Iron", "PVC", "Ductile Iron", "", "Steel"][i % 5],
                "status": ["Active", "Inactive", "Active", "Unknown"][i % 4],
                "SHAPE": None if i % 37 == 0 else {"x": -89.65 + i * 0.001, "y": 40.69 + i * 0.001},
            }
        )
    return pd.DataFrame(rows)


def score_color(score):
    if score >= 85:
        return "🟢"
    if score >= 70:
        return "🟡"
    if score >= 60:
        return "🟠"
    return "🔴"


def main():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 0px;
        }
        .subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 25px;
        }
        .section-card {
            padding: 18px;
            border-radius: 14px;
            background-color: #f7f9fc;
            border: 1px solid #e5e8ef;
            margin-bottom: 16px;
        }
        .big-number {
            font-size: 30px;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="main-title">GeoOps Municipal Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">ArcGIS-aligned operational intelligence for municipal GIS QA, readiness scoring, issue prioritization, and analyst review workflows.</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "GeoOps does not replace ArcGIS. It reads GIS data, evaluates quality and readiness, then produces issue layers and reports analysts can use inside existing GIS workflows."
    )

    with st.sidebar:
        st.header("GeoOps Control Center")
        data_source = st.radio("Data Source", ["Demo Utility Dataset", "Upload CSV"])
        st.markdown("---")
        st.caption("Current Version: MVP Platform Demo")
        st.caption("Modules: Intake → GeoQA → Readiness → Reporting → Issue Layer Export")

    df = None

    if data_source == "Demo Utility Dataset":
        df = create_demo_utility_data()
    else:
        uploaded_file = st.sidebar.file_uploader("Upload municipal asset CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

    if df is None:
        st.warning("Load a dataset to begin.")
        return

    tab_overview, tab_assessment, tab_issues, tab_workflow, tab_exports = st.tabs(
        [
            "Platform Overview",
            "Assessment",
            "Issue Intelligence",
            "ArcGIS Workflow Fit",
            "Outputs",
        ]
    )

    with tab_overview:
        st.subheader("What GeoOps Does")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                """
                <div class="section-card">
                <h4>1. GIS Data Intake</h4>
                Reads municipal GIS data from CSV today and ArcGIS Feature Layers in the integration roadmap.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                """
                <div class="section-card">
                <h4>2. Operational QA</h4>
                Detects missing IDs, invalid attributes, stale inspections, geometry issues, and utility-readiness gaps.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                """
                <div class="section-card">
                <h4>3. Decision Output</h4>
                Produces readiness scores, review priorities, recommendations, and ArcGIS-ready issue layers.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("Dataset Preview")
        st.dataframe(df.head(30), use_container_width=True)

        st.markdown("### Dataset Profile")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total Records", len(df))
        p2.metric("Total Fields", len(df.columns))
        p3.metric("Missing Values", int(df.isna().sum().sum()))
        p4.metric("Duplicate Rows", int(df.drop(columns=["SHAPE"], errors="ignore").duplicated().sum()))

    with tab_assessment:
        st.subheader("Run Municipal GIS Health Assessment")

        st.write(
            "This assessment runs GeoQA checks, calculates readiness scores, assigns review priorities, and creates exportable outputs."
        )

        run_button = st.button("Run GeoOps Assessment", type="primary", use_container_width=True)

        if run_button:
            result = run_geoops_pipeline(df)
            st.session_state["geoops_result"] = result

        if "geoops_result" in st.session_state:
            result = st.session_state["geoops_result"]
            readiness = result["readiness_summary"]
            issue_summary = result["issue_summary"]

            st.markdown("### Executive Readiness Scores")

            s1, s2, s3, s4 = st.columns(4)

            s1.metric(
                "Overall GIS Health",
                f"{score_color(readiness['overall_gis_health_score'])} {readiness['overall_gis_health_score']}",
            )
            s2.metric("Data Quality", readiness["data_quality_score"])
            s3.metric("Utility Readiness", readiness["utility_network_readiness_score"])
            s4.metric("Asset Readiness", readiness["asset_management_readiness_score"])

            st.success(f"Readiness Level: {readiness['readiness_level']}")

            st.markdown("### Issue Summary")
            i1, i2, i3 = st.columns(3)
            i1.metric("Total Issues", issue_summary["total_issues"])
            i2.metric("Critical Issues", issue_summary.get("severity_breakdown", {}).get("Critical", 0))
            i3.metric("High Issues", issue_summary.get("severity_breakdown", {}).get("High", 0))

            severity_breakdown = issue_summary.get("severity_breakdown", {})
            category_breakdown = issue_summary.get("category_breakdown", {})

            c1, c2 = st.columns(2)

            with c1:
                if severity_breakdown:
                    severity_df = pd.DataFrame(
                        {"Severity": list(severity_breakdown.keys()), "Count": list(severity_breakdown.values())}
                    )
                    st.plotly_chart(
                        px.bar(severity_df, x="Severity", y="Count", title="Issues by Severity"),
                        use_container_width=True,
                    )

            with c2:
                if category_breakdown:
                    category_df = pd.DataFrame(
                        {"Category": list(category_breakdown.keys()), "Count": list(category_breakdown.values())}
                    )
                    st.plotly_chart(
                        px.bar(category_df, x="Category", y="Count", title="Top Issue Categories"),
                        use_container_width=True,
                    )

            st.markdown("### Recommendations")
            for rec in result["recommendations"]:
                st.write(f"✅ {rec}")

    with tab_issues:
        st.subheader("Issue Intelligence")

        st.write(
            "This section is designed for GIS analysts. The purpose is to identify which records need review first and why."
        )

        if "geoops_result" not in st.session_state:
            st.warning("Run the GeoOps assessment first.")
        else:
            issues_path = st.session_state["geoops_result"]["outputs"]["issues_csv"]
            priorities_path = st.session_state["geoops_result"]["outputs"]["priorities_csv"]

            issues_df = pd.read_csv(issues_path)
            priorities_df = pd.read_csv(priorities_path)

            f1, f2 = st.columns(2)
            with f1:
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    sorted(issues_df["severity"].dropna().unique()),
                    default=list(sorted(issues_df["severity"].dropna().unique())),
                )
            with f2:
                category_filter = st.multiselect(
                    "Filter by Category",
                    sorted(issues_df["issue_category"].dropna().unique()),
                    default=list(sorted(issues_df["issue_category"].dropna().unique())),
                )

            filtered = issues_df[
                issues_df["severity"].isin(severity_filter)
                & issues_df["issue_category"].isin(category_filter)
            ]

            st.markdown("### Flagged Issues")
            st.dataframe(filtered, use_container_width=True)

            st.markdown("### Feature Review Priorities")
            st.dataframe(priorities_df, use_container_width=True)

    with tab_workflow:
        st.subheader("How This Fits Into ArcGIS Workflows")

        st.markdown(
            """
            ### Existing GIS Workflow

            Client GIS Data → ArcGIS Pro / ArcGIS Online → Manual QA → Cleanup → Delivery

            ### GeoOps-Enhanced Workflow

            Client GIS Data → ArcGIS / CSV Export → GeoOps Assessment → Issue Layer + Readiness Report → ArcGIS Analyst Review → Cleanup → Delivery

            ### Why This Matters

            ArcGIS remains the system of record and editing environment.  
            GeoOps adds review intelligence by answering:

            - Which records should be reviewed first?
            - Why are they risky?
            - What issues are most common?
            - Is the dataset ready for Utility Network or asset management workflows?
            - What should be fixed before client delivery?
            """
        )

    with tab_exports:
        st.subheader("Generated Outputs")

        if "geoops_result" not in st.session_state:
            st.warning("Run the GeoOps assessment first.")
        else:
            outputs = st.session_state["geoops_result"]["outputs"]

            st.json(outputs)

            for name, path in outputs.items():
                if path:
                    try:
                        with open(path, "rb") as f:
                            st.download_button(
                                label=f"Download {name}",
                                data=f,
                                file_name=path.split("/")[-1],
                            )
                    except FileNotFoundError:
                        st.warning(f"Output not found: {path}")


if __name__ == "__main__":
    main()