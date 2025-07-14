import os
from utils.common import makeid

def create_object_payload(custom_name=None):
    owner_email = os.getenv("OWNER_EMAIL", "")
    owner_name = os.getenv("OWNER_NAME", "")
    name = f"{custom_name} {makeid(2)}" if custom_name else f"Object {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "resource",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt aliqua."
            ),
            "label": "DR",
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [owner_name],
            "links": [],
        },
    }

def configure_object_payload():
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