from test_data.velora.mesh_payload import create_mesh_payload
from test_data.velora.system_payload import create_system_payload
from test_data.velora.source_payload import create_source_payload
from test_data.velora.object_payload import create_object_payload
from test_data.velora.product_payload import create_product_payload
from test_data.velora.connection_config_payload import create_connection_config_payload
from test_data.velora.connection_secret_payload import create_connection_secret_payload
from test_data.velora.schema_product_payload import schema_product_create_payload
from test_data.velora.product_transformation_payload import create_transformation_builder_payload_with_inputs

config = {
    "steps": [
        {
            "type": "create_mesh",
            "id": "mesh-abc",
            "input": create_mesh_payload(),
        },
        {
            "type": "create_system",
            "id": "system-abc",
            "input": create_system_payload(),
        },
        {
            "type": "create_product",
            "id": "product-a",
            "mesh_ref": "mesh-abc",
            "input": create_product_payload(),
        },
        {
            "type": "get_product",
            "input": {
                "product_ref": "product-a"
            }
        },
        {
            "type": "delete_product",
            "input": {
                "product_ref": "product-a"
            }
        },
           {
            "type": "delete_mesh",
            "input": {
                "mesh_ref": "mesh-abc"
            }
        },
        {
            "type": "get_mesh_list",
        },
    ],
}
