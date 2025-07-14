import os
from utils.common import makeid

def create_source_payload(custom_name=None):
    owner_email = os.getenv("OWNER_EMAIL", "")
    name = f"{custom_name} {makeid(2)}" if custom_name else f"Source {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "origin",
            "label": "SCD",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt aliqua."
            ),
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
