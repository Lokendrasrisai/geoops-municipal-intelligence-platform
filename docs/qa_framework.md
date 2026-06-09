# GeoQA Framework

## Purpose

GeoQA is the quality assessment module of the GeoOps Municipal Intelligence Platform.

Its purpose is to evaluate municipal GIS datasets and identify records that may require analyst review before publishing, migration, Utility Network work, dashboard creation, or client delivery.

GeoQA does not replace ArcGIS or GIS analysts. It creates a prioritized review layer that helps analysts focus on the records that matter most.

---

## Core Principle

GeoQA answers:

* What is wrong with this GIS dataset?
* Which issues matter most?
* Which records should be reviewed first?
* What action should the analyst take?
* Is this dataset ready for operational use?

---

## QA Categories

### 1. Asset Identity Checks

These checks verify that each asset can be uniquely identified.

| Check                  | Description                               | Severity |
| ---------------------- | ----------------------------------------- | -------- |
| Missing Asset ID       | Asset has no unique identifier            | Critical |
| Duplicate Asset ID     | Same ID appears more than once            | Critical |
| Invalid ID Format      | ID does not match expected naming pattern | Medium   |
| Missing Asset Type     | Asset type is blank or unknown            | High     |
| Conflicting Asset Type | Asset type conflicts with attributes      | High     |

---

### 2. Geometry and Location Checks

These checks verify whether features are spatially usable.

| Check                        | Description                                      | Severity |
| ---------------------------- | ------------------------------------------------ | -------- |
| Missing Geometry             | Feature has no geometry                          | Critical |
| Invalid Coordinates          | Latitude/longitude outside valid range           | Critical |
| Duplicate Location           | Multiple assets share same location unexpectedly | High     |
| Asset Outside Service Area   | Asset falls outside expected municipal boundary  | High     |
| Suspicious Spatial Outlier   | Asset is far away from the main service cluster  | Medium   |
| Zero-Length Line             | Pipe/main segment has zero length                | Critical |
| Extremely Short/Long Segment | Line feature has suspicious geometry length      | Medium   |

---

### 3. Attribute Completeness Checks

These checks verify whether required operational fields are populated.

| Check                        | Description                           | Severity |
| ---------------------------- | ------------------------------------- | -------- |
| Missing Condition            | Asset condition is blank              | High     |
| Missing Install Year         | Install year is missing               | Medium   |
| Missing Last Inspection Date | Inspection date is blank              | High     |
| Missing Material             | Material field is blank               | Medium   |
| Missing Diameter             | Diameter is missing for utility asset | High     |
| Missing Pressure Zone        | Pressure zone is missing              | High     |
| Missing Status               | Active/inactive status is missing     | Medium   |

---

### 4. Attribute Validity Checks

These checks verify whether field values are realistic.

| Check                    | Description                                  | Severity |
| ------------------------ | -------------------------------------------- | -------- |
| Future Install Year      | Install year is later than current year      | High     |
| Unrealistic Install Year | Install year is too old or impossible        | High     |
| Invalid Condition Value  | Condition does not match accepted categories | Medium   |
| Invalid Status Value     | Status does not match expected status list   | Medium   |
| Suspicious Diameter      | Diameter is unusually small or large         | Medium   |
| Invalid Material         | Material is not in accepted material list    | Medium   |

---

### 5. Inspection and Maintenance Checks

These checks identify assets that may require operational attention.

| Check                                  | Description                                   | Severity |
| -------------------------------------- | --------------------------------------------- | -------- |
| Inspection Overdue                     | Asset has not been inspected recently         | High     |
| Old Asset With No Recent Inspection    | Asset is old and inspection is stale          | High     |
| Poor Condition Asset                   | Asset condition indicates concern             | High     |
| Critical Asset With Missing Inspection | Important asset lacks inspection history      | Critical |
| Inactive Asset With Active Attributes  | Asset marked inactive but appears operational | Medium   |

---

### 6. Utility Readiness Checks

These checks support water, sewer, stormwater, and Utility Network readiness.

| Check                          | Description                                    | Severity |
| ------------------------------ | ---------------------------------------------- | -------- |
| Missing Connectivity Attribute | Required network connectivity field is missing | High     |
| Orphan Asset                   | Asset has no nearby related network feature    | High     |
| Missing From/To Node           | Line asset lacks connectivity endpoints        | Critical |
| Diameter-Material Mismatch     | Attribute combination appears inconsistent     | Medium   |
| Pressure Zone Inconsistency    | Nearby assets have conflicting pressure zones  | Medium   |
| Disconnected Segment           | Pipe/main is not connected to expected network | Critical |

---

### 7. Operational Risk Checks

These checks combine multiple signals into review priority.

| Check                | Description                                 | Severity |
| -------------------- | ------------------------------------------- | -------- |
| High-Risk Asset      | Old + poor condition + stale inspection     | Critical |
| Medium-Risk Asset    | Multiple moderate issues present            | High     |
| Review Cluster       | Several issues occur in same area           | High     |
| Data Quality Hotspot | Localized region has concentrated QA issues | Medium   |

---

## Severity Levels

| Severity | Meaning                                             |
| -------- | --------------------------------------------------- |
| Critical | Must be reviewed before delivery or migration       |
| High     | Likely to affect analysis, reporting, or operations |
| Medium   | Should be reviewed when time allows                 |
| Low      | Minor issue or informational warning                |

---

## Review Priority Logic

Each feature receives a review priority based on issue severity and issue count.

| Priority        | Meaning                               |
| --------------- | ------------------------------------- |
| Critical Review | Immediate analyst review required     |
| High Review     | Strong candidate for near-term review |
| Medium Review   | Review recommended                    |
| Low Review      | Minor concern                         |
| Clean           | No major issue detected               |

---

## Scoring Approach

Each dataset receives a Data Quality Score from 0 to 100.

Suggested penalties:

* Critical issue: -5 points
* High issue: -3 points
* Medium issue: -1.5 points
* Low issue: -0.5 points

The final score is clamped between 0 and 100.

---

## Output Artifacts

GeoQA should produce:

1. Issue table
2. Enriched asset dataset
3. ArcGIS-ready issue layer
4. Severity summary
5. Data quality score
6. Analyst recommendations
7. Executive QA report

---

## ArcGIS Integration

GeoQA should support this workflow:

ArcGIS Feature Layer
→ GeoOps Data Intake
→ GeoQA Engine
→ Issue Detection
→ Review Priority Scoring
→ ArcGIS Issue Layer
→ Analyst Review

The original ArcGIS layer should remain unchanged. GeoQA should create a separate review layer.

---

## Design Philosophy

GeoQA is not designed to replace GIS analysts.

It is designed to reduce manual review effort, standardize quality checks, and help analysts focus on the highest-value review tasks first.
