import os
from utils.common import makeid


def create_object_excavation_payload():
    owner_email = os.getenv("OWNER_EMAIL", "")
    owner_name = os.getenv("OWNER_NAME", "")
    name = f"Excavation {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "resource",
            "description": "This data object holds the excavation progress data linked to each daily report. It captures the planned volume of work for the day (planned_quantity), the actual volume completed (daily_quantity), and the running cumulative volume (cumulative_quantity) to assess overall project progress. Any corrections or adjustments applied to the figures (adjustments_delta) are also recorded, ensuring accuracy in reporting and performance tracking.",
            "label": "ECV",
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [owner_name],
            "links": [],
        },
    }


def configure_object_excavation_payload():
    return {
        "configuration": {
            "resource_type": "csv",
            "path": "/samples/construction_demo/excavation.csv",
            "has_header": True,
            "delimiter": ",",
            "quote_char": None,
            "escape_char": None,
            "multi_line": None,
        }
    }
