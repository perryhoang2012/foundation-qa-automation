import os
from utils.common import makeid


def create_product_excavation_payload():
    owner_email = os.getenv("OWNER_EMAIL", "")
    name = f"Excavation {makeid()}"
    return {
        "entity": {
            "name": name,
            "entity_type": "product",
            "label": "ECV",
            "description": "This data object holds the excavation progress data linked to each daily report. It captures the planned volume of work for the day (planned_quantity), the actual volume completed (daily_quantity), and the running cumulative volume (cumulative_quantity) to assess overall project progress. Any corrections or adjustments applied to the figures (adjustments_delta) are also recorded, ensuring accuracy in reporting and performance tracking.",
        },
        "host_mesh_identifier": "",
        "mesh_ref": "mesh-1",
        "entity_info": {
            "owner": owner_email,
            "contact_ids": [],
            "links": [],
        },
    }
