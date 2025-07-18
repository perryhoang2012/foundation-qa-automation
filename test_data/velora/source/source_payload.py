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
            "description": "Mobile app-generated logs capturing comprehensive daily field activities, including work progress, crew attendance, and various on-site operations.",
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
