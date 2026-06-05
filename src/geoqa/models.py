from dataclasses import dataclass


@dataclass
class GeoQAIssue:
    feature_index: int
    asset_id: str
    issue_category: str
    issue_description: str
    severity: str
    recommended_action: str