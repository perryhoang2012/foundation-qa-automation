import os
from utils.common import makeid


def create_product_excavation_progress_payload():
    owner_email = os.getenv("OWNER_EMAIL", "")
    name = f"Excavation progress {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "product",
            "label": "EP",
            "description": "Aggregates excavation performance data, including daily and planned excavation volumes, variances, and cumulative progress metrics for tracking excavation project efficiency.",
        },
        "host_mesh_identifier": "",
        "mesh_ref": "mesh-1",
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
