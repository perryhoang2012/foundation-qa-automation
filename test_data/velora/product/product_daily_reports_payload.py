import os
from utils.common import makeid


def create_product_daily_reports_payload():
    owner_email = os.getenv("OWNER_EMAIL", "")
    name = f"Daily Reports {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "product",
            "label": "DR",
            "description": "This data object aggregates all the daily reports submitted by the contractors. Each record is associated with a specific contractor and a report date. The report_id uniquely identifies each report, while the contractor_id (linked to the Contractors table) and report_date provide context for when and by whom the report was generated.",
        },
        "host_mesh_identifier": "",
        "mesh_ref": "mesh-1",
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
