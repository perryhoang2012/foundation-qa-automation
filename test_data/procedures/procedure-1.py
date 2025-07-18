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
        # Mesh
        {
            "type": "create_mesh",
            "id": "mesh-1",
            "input": create_mesh_payload(),
        },
        # System
        {
            "type": "create_system",
            "id": "system-1",
            "input": create_system_payload(),
        },
        # Source
        {
            "type": "create_source",
            "id": "source-1",
            "input": create_source_payload(),
        },
        {
            "type": "link_system_to_source",
            "input": {
                "system_ref": "system-1",
                "source_ref": "source-1",
            },
        },
        {
            "type": "configure_source",
            "ref": "source-1",
            "input": create_connection_config_payload(),
        },
        {
            "type": "set_source_secret",
            "ref": "source-1",
            "input": create_connection_secret_payload(),
        },
        {
            "type": "get_source_by_id",
            "input": {
                "source_ref": "source-1",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "source-1",
            "max_retries": 10,
            "retry_interval": 20,
        },
        # Object 1
        {
            "type": "create_object",
            "id": "object-1",
            "input": create_object_daily_reports_payload(),
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-1",
                "object_ref": "object-1",
            },
        },
        {
            "type": "configure_object_details",
            "ref": "object-1",
            "input": configure_object_daily_reports_payload(),
        },
        {
            "type": "get_object_by_id",
            "input": {
                "object_ref": "object-1",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "object-1",
            "max_retries": 10,
            "retry_interval": 20,
        },
        # Object 2
        {
            "type": "create_object",
            "id": "object-2",
            "input": create_object_excavation_payload(),
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-1",
                "object_ref": "object-2",
            },
        },
        {
            "type": "link_object_to_source",
            "input": {
                "source_ref": "source-1",
                "object_ref": "object-2",
            },
        },
        {
            "type": "configure_object_details",
            "ref": "object-2",
            "input": configure_object_excavation_payload(),
        },
        {
            "type": "get_object_by_id",
            "input": {
                "object_ref": "object-2",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "object-2",
            "max_retries": 10,
            "retry_interval": 20,
        },
        # SADP 1
        {
            "type": "create_product",
            "id": "sadp-1",
            "input": create_product_daily_reports_payload(),
        },
        {
            "type": "link_product_to_object",
            "input": {
                "object_ref": "object-1",
                "product_ref": "sadp-1",
            },
        },
        {
            "type": "define_product_schema",
            "ref": "sadp-1",
            "input": schema_product_daily_reports_payload(),
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "sadp-1",
                "transformations": product_daily_reports_builder_payload(),
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "sadp-1",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "sadp-1",
            "max_retries": 10,
            "retry_interval": 20,
        },
        # SADP 2
        {
            "type": "create_product",
            "id": "sadp-2",
            "input": create_product_excavation_payload(),
        },
        {
            "type": "link_product_to_object",
            "input": {
                "object_ref": "object-2",
                "product_ref": "sadp-2",
            },
        },
        {
            "type": "define_product_schema",
            "ref": "sadp-2",
            "input": schema_product_excavation_payload(),
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "sadp-2",
                "transformations": product_excavation_builder_payload(),
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "sadp-2",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "sadp-2",
            "max_retries": 10,
            "retry_interval": 20,
        },
        # CADP
        {
            "type": "create_product",
            "id": "cadp",
            "input": create_product_excavation_progress_payload(),
        },
        {
            "type": "define_product_schema",
            "ref": "cadp",
            "input": schema_product_excavation_progress_payload(),
        },
        {
            "type": "apply_product_transformation",
            "input": {
                "product_ref": "cadp",
                "transformations": product_excavation_progress_builder_payload(),
            },
        },
        {
            "type": "get_product_by_id",
            "input": {
                "product_ref": "cadp",
            },
        },
        {
            "type": "check_status_compute",
            "ref": "cadp",
            "max_retries": 10,
            "retry_interval": 20,
        },
    ],
}
