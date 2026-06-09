# src/reporting/executive_summary.py

def generate_executive_summary(summary):

    return f"""
GeoOps Municipal Intelligence Report

Overall GIS Health Score:
{summary['overall_gis_health_score']}

Readiness Level:
{summary['readiness_level']}

Data Quality Score:
{summary['data_quality_score']}

Utility Network Readiness:
{summary['utility_network_readiness_score']}

Asset Management Readiness:
{summary['asset_management_readiness_score']}
"""