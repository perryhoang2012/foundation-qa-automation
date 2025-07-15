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
            "type": "create_source",
            "id": "source-abc",
            "input": create_source_payload(),
        },
        {
            "type": "link_system_to_source",
            "input": {
                "system_ref": "system-abc",
                "source_ref": "source-abc",
            },
        },
        {
            "type": "configure_source",
            "ref": "source-abc",
            "input": create_connection_config_payload(),
        },
        {
            "type": "set_source_secret",
            "ref": "source-abc",
            "input": create_connection_secret_payload(),
        },
        {
            "type": "create_object",
            "id": "object-abc",
            "input": create_object_payload(),
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-abc",
                "object_ref": "object-abc",
            },
        },
          {
            "type": "create_object",
            "id": "object-def",
            "input": create_object_payload(),
        },
         {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-abc",
                "object_ref": "object-def",
            },
        },
        {
            "type": "create_product",
            "id": "product-abc",
            "mesh_ref": "mesh-abc",
            "input": create_product_payload(),
        },
        {
            "type": "link_product_to_object",
            "input": {
                "object_ref": "object-abc",
                "product_ref": "product-abc",
            },
        },
        {
            "type": "define_product_schema",
            "ref": "product-abc",
            "input": schema_product_create_payload(),
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "product-abc",
                "input_refs": ["object-abc", "object-def"],
                "transformation": create_transformation_builder_payload_with_inputs(),
            },
        },
    ],
}
