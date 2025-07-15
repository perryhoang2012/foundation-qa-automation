import os
from utils.common import makeid


def create_product_payload(mesh_id=None, custom_name=None):
    owner_email = os.getenv("OWNER_EMAIL", "")
    name = f"{custom_name} {makeid(2)}" if custom_name else f"Product {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "product",
            "label": "EP",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt aliqua."
            ),
        },
        "host_mesh_identifier": mesh_id,
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
