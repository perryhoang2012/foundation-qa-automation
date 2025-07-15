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
            "type": "get_all_mesh",
        },
        {
            "type": "get_all_system"
        },
        {
            "type": "get_all_source"
        },
        {
            "type": "get_all_object"
        },
        {
            "type": "get_object_by_id", 
            "ref": "object-abc"
        },
        {
            "type": "get_all_product"
        },
        {
            "type": "get_product_by_id", "ref": "product-abc"
        },
    ],
}
