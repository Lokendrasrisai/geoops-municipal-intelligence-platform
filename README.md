# GeoOps Intelligence Layer

**AI-powered decision intelligence for GIS and infrastructure teams.**

GeoOps Intelligence Layer sits on top of existing GIS systems — ArcGIS Online, hosted feature layers, field inspection data, and asset records — and helps teams move from simply *viewing* asset data to *understanding risk*, *prioritizing action*, and making *explainable operational decisions*.

---

## What It Does

| Module | What It Delivers |
|---|---|
| **GeoQA Engine** | Detects missing IDs, invalid attributes, duplicate assets, stale inspections, geometry issues — 15 automated checks |
| **Asset Risk Scoring** | Scores every asset 0–100 based on age, condition, inspection currency, and data quality |
| **Explainability Layer** | Plain-English explanation for every score — *"This asset scored 78 because it is 67 years old, rated Poor condition, and hasn't been inspected in 4 years"* |
| **Recommendation Engine** | Per-asset action codes: Escalate / Replace / Repair / Inspect / Monitor / Validate Data / Routine |
| **Spatial Intelligence** | Risk hotspot analysis by pressure zone — identifies which zones need focused operational review |
| **Interactive Map** | Folium risk map — assets colored by score, clickable popups with full asset detail |
| **ArcGIS Integration** | Reads from public ArcGIS Feature Layers; exports issue layers as GeoJSON for ArcGIS import |
| **Readiness Dashboard** | Executive-level GIS health, data quality, utility readiness, and asset management scores |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-username/geoops-intelligence-platform.git
cd geoops-intelligence-platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`. Select **Sample Dataset (Water Mains)** in the sidebar, then click **▶ Run Full GeoOps Assessment**.

---

## Project Structure

```
geoops-intelligence-platform/
│
├── app.py                          # Streamlit entry point (~100 lines, thin by design)
├── requirements.txt                # Pinned dependencies
├── Dockerfile / docker-compose.yml
│
├── data/
│   └── sample_water_mains.csv      # 500-row realistic water main dataset
│
├── src/
│   ├── geoqa/          # GIS data quality check engine
│   ├── readiness/      # Dataset readiness scoring
│   ├── utility_intelligence/  # Asset risk scoring
│   ├── intelligence/   # Explainability + recommendation engine  ← NEW
│   ├── spatial/        # Pressure zone hotspot analysis
│   ├── arcgis/         # ArcGIS Feature Layer loader + GeoJSON exporter
│   ├── intake/         # CSV / GeoJSON loaders
│   ├── pipeline/       # End-to-end orchestration
│   ├── reporting/      # HTML report builder
│   └── ui/             # Styles, components, charts  ← NEW
│
├── pages/
│   └── 6_Map_View.py   # Interactive Folium risk map  ← NEW
│
└── tests/
    ├── conftest.py
    ├── test_geoqa.py           # 17 tests
    ├── test_risk.py            # 13 tests
    ├── test_explainability.py  # 12 tests
    └── test_recommendations.py # 9 tests
```

---

## Running Tests

```bash
pytest tests/test_geoqa.py tests/test_risk.py tests/test_explainability.py tests/test_recommendations.py -v
```

**51 tests — all passing.**

---

## Target Users

- GIS Analysts and Engineers
- Utility Network Teams
- Infrastructure Asset Managers
- Field Operations Teams
- Municipal Public Works Teams
- Decision Makers who need clear dashboards and reports

---

## Technology Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit |
| Data processing | Pandas, NumPy |
| Geospatial | GeoPandas, Shapely, Folium |
| Visualization | Plotly |
| ArcGIS integration | ArcGIS API for Python |
| Containerization | Docker |
| Testing | pytest |

---

## Product Positioning

GeoOps Intelligence Layer is **not** a machine learning experiment. It is a **GeoAI decision intelligence product** for infrastructure operations — designed to be shown to utility companies, municipal GIS teams, and infrastructure decision makers.

> *"GeoOps helps GIS and infrastructure teams move from simply viewing asset data to understanding risk, prioritizing action, and making explainable operational decisions."*

---

## Roadmap

| Phase | Status |
|---|---|
| Phase 1 — Clean MVP (QA, Risk, Explainability, Map) | ✅ Complete |
| Phase 2 — GeoAI Enrichment (Anomaly Detection, Copilot) | 🔄 Planned |
| Phase 3 — Platform Architecture (FastAPI + React + PostGIS) | 📋 Roadmap |
| Phase 4 — Enterprise Deployment (Multi-tenant, GovCloud) | 🔭 Future |

---

## License

MIT
