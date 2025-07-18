import os
from utils.common import makeid


def create_object_daily_reports_payload():
    owner_email = os.getenv("OWNER_EMAIL", "")
    owner_name = os.getenv("OWNER_NAME", "")
    name = f"Daily reports {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "resource",
            "description": "This data object aggregates all the daily reports submitted by the contractors. Each record is associated with a specific contractor and a report date. The report_id uniquely identifies each report, while the contractor_id (linked to the Contractors table) and report_date provide context for when and by whom the report was generated.",
            "label": "DR",
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [owner_name],
            "links": [],
        },
    }


def configure_object_daily_reports_payload():
    return {
        "configuration": {
            "resource_type": "csv",
            "path": "/samples/construction_demo/daily_reports.csv",
            "has_header": True,
            "delimiter": ",",
            "quote_char": None,
            "escape_char": None,
            "multi_line": None,
        }
    }
