from test_data.velora import (
    create_mesh_payload,
    create_system_payload,
    create_source_payload,
    create_object_payload,
    create_product_payload,
    create_connection_config_payload,
    create_connection_secret_payload,
    schema_product_create_payload,
    create_transformation_builder_payload_with_inputs,
    configure_object_payload,
)

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
            "type": "get_source_by_id",
            "input": {
                "source_ref": "source-abc",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "source-abc",
            "max_retries": 5,
            "retry_interval": 20,
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
            "type": "configure_object_details",
            "ref": "object-abc",
            "input": configure_object_payload(),
        },
        {
            "type": "get_object_by_id",
            "input": {
                "object_ref": "object-abc",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "object-abc",
            "max_retries": 5,
            "retry_interval": 15,
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
                "input_refs": ["object-abc"],
                "transformation": create_transformation_builder_payload_with_inputs(),
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "product-abc",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "product-abc",
            "max_retries": 5,
            "retry_interval": 30,
        },
    ],
}
