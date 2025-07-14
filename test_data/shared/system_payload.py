import os
from utils.common import makeid

def create_system_payload(custom_name=None):
    owner_email = os.getenv("OWNER_EMAIL", "")
    owner_name = os.getenv("OWNER_NAME", "")
    name = f"{custom_name} {makeid(2)}" if custom_name else f"System {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "data_system",
            "label": "DSS",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt aliqua."
            ),
            "owner_person": {
                "email": owner_email,
                "full_name": owner_name,
            },
        },
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
