from test_data.velora import (
    create_mesh_payload,
    create_system_payload,
    create_source_payload,
    create_connection_config_payload,
    create_connection_secret_payload,
    create_object_daily_reports_payload,
    create_object_excavation_payload,
    configure_object_daily_reports_payload,
    configure_object_excavation_payload,
    create_product_daily_reports_payload,
    create_product_excavation_payload,
    create_product_excavation_progress_payload,
    schema_product_daily_reports_payload,
    schema_product_excavation_payload,
    schema_product_excavation_progress_payload,
    product_daily_reports_builder_payload,
    product_excavation_builder_payload,
    product_excavation_progress_builder_payload,
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
            "input": create_object_daily_reports_payload(),
        },
        {
            "type": "create_object",
            "id": "object-def",
            "input": create_object_excavation_payload(),
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-abc",
                "object_ref": "object-abc",
            },
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-abc",
                "object_ref": "object-def",
            },
        },
        {
            "type": "configure_object_details",
            "ref": "object-abc",
            "input": configure_object_daily_reports_payload(),
        },
        {
            "type": "configure_object_details",
            "ref": "object-def",
            "input": configure_object_excavation_payload(),
        },
        {
            "type": "get_object_by_id",
            "input": {
                "object_ref": "object-abc",
            },
        },
        {
            "type": "get_object_by_id",
            "input": {
                "object_ref": "object-def",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "object-abc",
            "max_retries": 5,
            "retry_interval": 15,
        },
        {
            "type": "check_status_compute",
            "ref": "object-def",
            "max_retries": 5,
            "retry_interval": 15,
        },
        {
            "type": "create_product",
            "id": "product-abc",
            "input": create_product_daily_reports_payload(),
        },
        {
            "type": "create_product",
            "id": "product-def",
            "input": create_product_excavation_payload(),
        },
        {
            "type": "create_product",
            "id": "product-gkh",
            "input": create_product_excavation_progress_payload(),
        },
        {
            "type": "link_product_to_object",
            "input": {
                "object_ref": "object-abc",
                "product_ref": "product-abc",
            },
        },
        {
            "type": "link_product_to_object",
            "input": {
                "object_ref": "object-def",
                "product_ref": "product-def",
            },
        },
        {
            "type": "link_product_to_product",
            "input": {
                "product_ref": "product-abc",
                "product_child_ref": "product-gkh",
            },
        },
        {
            "type": "link_product_to_product",
            "input": {
                "product_ref": "product-def",
                "product_child_ref": "product-gkh",
            },
        },
        {
            "type": "define_product_schema",
            "ref": "product-abc",
            "input": schema_product_daily_reports_payload(),
        },
        {
            "type": "define_product_schema",
            "ref": "product-def",
            "input": schema_product_excavation_payload(),
        },
        {
            "type": "define_product_schema",
            "ref": "product-gkh",
            "input": schema_product_excavation_progress_payload(),
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "product-abc",
                "transformations": product_daily_reports_builder_payload(),
            },
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "product-def",
                "transformations": product_excavation_builder_payload(),
            },
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "product-gkh",
                "transformations": product_excavation_progress_builder_payload(),
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "product-abc",
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "product-def",
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "product-gkh",
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
