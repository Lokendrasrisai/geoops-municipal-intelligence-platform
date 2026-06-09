# Readiness Scoring Framework

## Purpose

The Readiness Scoring Engine converts raw GIS quality findings into clear, decision-ready scores.

Instead of only listing issues, GeoOps produces readiness scores that help GIS analysts, project managers, and municipal clients understand whether a dataset is ready for operational use, Utility Network migration, asset management, reporting, or further cleanup.

The goal is to move from:

Raw GIS issues → prioritized intelligence → actionable readiness scores

---

## Core Scores

GeoOps produces four major scores:

1. Data Quality Score
2. Utility Network Readiness Score
3. Asset Management Readiness Score
4. Overall Municipal GIS Health Score

Each score ranges from 0 to 100.

---

## Score Interpretation

| Score Range | Readiness Level     | Meaning                                                               |
| ----------- | ------------------- | --------------------------------------------------------------------- |
| 90–100      | Production Ready    | Dataset is highly reliable with minor or no issues                    |
| 80–89       | Operationally Ready | Dataset is usable with limited cleanup recommended                    |
| 70–79       | Review Recommended  | Dataset is usable but contains meaningful issues                      |
| 60–69       | Cleanup Required    | Dataset requires structured remediation before major use              |
| 40–59       | High Risk           | Dataset has significant quality or readiness concerns                 |
| 0–39        | Not Ready           | Dataset should not be used for critical workflows without remediation |

---

## 1. Data Quality Score

### Purpose

Measures whether the GIS dataset is clean, complete, consistent, and usable.

### Evaluates

* Asset identity
* Missing values
* Duplicate records
* Geometry validity
* Attribute consistency
* Data completeness
* Inspection field quality

### Formula

Start with 100 points.

Apply weighted penalties based on issue severity:

| Severity | Penalty |
| -------- | ------: |
| Critical |    -5.0 |
| High     |    -3.0 |
| Medium   |    -1.5 |
| Low      |    -0.5 |

Final score:

Data Quality Score = 100 - total weighted penalties

The score is clamped between 0 and 100.

### Example

If a dataset has:

* 4 Critical issues
* 10 High issues
* 20 Medium issues
* 30 Low issues

Penalty:

* Critical: 4 × 5 = 20
* High: 10 × 3 = 30
* Medium: 20 × 1.5 = 30
* Low: 30 × 0.5 = 15

Total penalty = 95

Data Quality Score = 100 - 95 = 5

This indicates the dataset is not ready for operational use.

---

## 2. Utility Network Readiness Score

### Purpose

Measures whether utility asset data is ready for Utility Network migration, tracing, connectivity modeling, or advanced infrastructure workflows.

### Evaluates

* Required utility attributes
* Connectivity information
* Pipe/line endpoint quality
* Pressure zones
* Diameter fields
* Material fields
* Network consistency
* Orphan assets
* Disconnected features

### Key Factors

| Factor                                  | Weight |
| --------------------------------------- | -----: |
| Required asset fields                   |    25% |
| Geometry/network connectivity           |    30% |
| Attribute consistency                   |    20% |
| Inspection/condition completeness       |    15% |
| Spatial logic and service area validity |    10% |

### Scoring Logic

Utility Network Readiness Score is calculated from sub-scores:

UN Readiness Score =
0.25 × Required Fields Score +
0.30 × Connectivity Score +
0.20 × Attribute Consistency Score +
0.15 × Inspection Completeness Score +
0.10 × Spatial Validity Score

### Interpretation

| Score Range | Meaning                                        |
| ----------- | ---------------------------------------------- |
| 90–100      | Strong candidate for Utility Network workflows |
| 80–89       | Mostly ready with limited cleanup              |
| 70–79       | Needs review before migration                  |
| 60–69       | Cleanup required before Utility Network work   |
| Below 60    | High migration risk                            |

---

## 3. Asset Management Readiness Score

### Purpose

Measures whether assets are ready for maintenance planning, inspection prioritization, and operational decision-making.

### Evaluates

* Asset age
* Condition status
* Inspection recency
* Maintenance history
* Operational status
* Critical asset completeness
* Risk indicators

### Key Factors

| Factor                      | Weight |
| --------------------------- | -----: |
| Condition completeness      |    25% |
| Inspection recency          |    25% |
| Asset age validity          |    15% |
| Maintenance/repair history  |    15% |
| Operational status quality  |    10% |
| Risk indicator completeness |    10% |

### Scoring Logic

Asset Management Readiness Score =
0.25 × Condition Score +
0.25 × Inspection Recency Score +
0.15 × Asset Age Score +
0.15 × Maintenance History Score +
0.10 × Status Quality Score +
0.10 × Risk Indicator Score

### Interpretation

| Score Range | Meaning                                 |
| ----------- | --------------------------------------- |
| 90–100      | Strong asset management dataset         |
| 80–89       | Good dataset with minor gaps            |
| 70–79       | Usable but needs targeted cleanup       |
| 60–69       | Limited asset management reliability    |
| Below 60    | Poor readiness for maintenance planning |

---

## 4. Overall Municipal GIS Health Score

### Purpose

Combines the major readiness dimensions into a single executive-level score.

This score helps project managers and municipal clients quickly understand the overall condition of their GIS data.

### Default Weights

| Score                            | Weight |
| -------------------------------- | -----: |
| Data Quality Score               |    40% |
| Utility Network Readiness Score  |    30% |
| Asset Management Readiness Score |    30% |

### Formula

Overall GIS Health Score =
0.40 × Data Quality Score +
0.30 × Utility Network Readiness Score +
0.30 × Asset Management Readiness Score

### Example

If:

* Data Quality Score = 82
* Utility Network Readiness Score = 74
* Asset Management Readiness Score = 88

Then:

Overall GIS Health Score =
0.40 × 82 +
0.30 × 74 +
0.30 × 88

Overall GIS Health Score = 81.4

Final rating: Operationally Ready

---

## Feature-Level Review Priority

Each individual asset receives a review priority.

### Review Priority Levels

| Priority        | Meaning                             |
| --------------- | ----------------------------------- |
| Critical Review | Must be reviewed immediately        |
| High Review     | Strong candidate for analyst review |
| Medium Review   | Review recommended                  |
| Low Review      | Minor concern                       |
| Clean           | No major issue detected             |

### Priority Score Logic

Each asset receives a feature-level score based on detected issues.

| Issue Severity | Points |
| -------------- | -----: |
| Critical       |    +10 |
| High           |     +6 |
| Medium         |     +3 |
| Low            |     +1 |

Additional risk boosters:

| Condition                            | Additional Points |
| ------------------------------------ | ----------------: |
| Asset is old and inspection is stale |                +5 |
| Asset is poor condition              |                +5 |
| Asset has duplicate ID               |                +8 |
| Asset is missing geometry            |               +10 |
| Asset is outside service area        |                +7 |
| Asset has multiple issue categories  |                +4 |

### Feature Priority Mapping

| Score | Priority        |
| ----- | --------------- |
| 20+   | Critical Review |
| 12–19 | High Review     |
| 6–11  | Medium Review   |
| 1–5   | Low Review      |
| 0     | Clean           |

---

## Dataset-Level Risk Classification

GeoOps also classifies datasets into risk categories.

| Category      | Criteria                                  |
| ------------- | ----------------------------------------- |
| Low Risk      | High scores, few critical issues          |
| Moderate Risk | Some high issues, limited critical issues |
| High Risk     | Many high/critical issues                 |
| Severe Risk   | Dataset not safe for production workflows |

Suggested logic:

* Severe Risk: Overall score below 50 or more than 10% of records have critical issues
* High Risk: Overall score below 70 or more than 20% of records require review
* Moderate Risk: Overall score 70–84
* Low Risk: Overall score 85+

---

## Executive Output

The scoring engine should generate a summary like:

Dataset: Hydrant Asset Inventory
Total Assets: 48,250
Total Issues: 3,412
Critical Issues: 214
High Review Assets: 1,126

Data Quality Score: 82
Utility Network Readiness Score: 74
Asset Management Readiness Score: 88
Overall GIS Health Score: 81

Readiness Level: Operationally Ready
Recommended Action: Targeted cleanup recommended before Utility Network migration or client delivery.

---

## Analyst Output

For GIS analysts, GeoOps should provide:

1. Ranked issue table
2. Feature-level review priority
3. Issue category breakdown
4. Recommended action per record
5. ArcGIS-ready issue layer
6. Exportable CSV/GeoJSON

---

## Project Manager Output

For project managers, GeoOps should provide:

1. Overall readiness score
2. Cleanup effort estimate
3. High-priority issue count
4. Dataset risk classification
5. Recommended next steps
6. Before/after comparison after remediation

---

## Design Philosophy

Readiness scoring should be:

* Explainable
* Transparent
* Adjustable
* Conservative
* Analyst-friendly
* Client-readable

GeoOps should never hide the reasoning behind a score.

Every score should connect back to specific issues, severity levels, and recommended actions.

---

## Future Enhancements

Future scoring versions may include:

1. Client-specific scoring profiles
2. Utility-specific readiness templates
3. Utility Network schema validation
4. Historical cleanup progress tracking
5. AI-assisted remediation suggestions
6. Benchmark comparison across municipalities
7. Confidence scores for automated recommendations
