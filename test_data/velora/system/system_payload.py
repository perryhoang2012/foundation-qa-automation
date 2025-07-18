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
            "description": "Procore is a comprehensive construction management platform that captures detailed daily field activities, including work progress, crew attendance, and material usage. It provides real-time insights into on-site operations and supports accurate daily reporting.",
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
