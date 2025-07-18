import os


def product_excavation_builder_payload():

    return {
        "config": {
            "docker_tag": "0.0.23",
            "executor_core_request": "800m",
            "executor_core_limit": "1500m",
            "executor_instances": 1,
            "min_executor_instances": 1,
            "max_executor_instances": 1,
            "executor_memory": "5120m",
            "driver_core_request": "0.3",
            "driver_core_limit": "800m",
            "driver_memory": "2048m",
        },
        "inputs": ["object-def"],
        "transformations": [
            {
                "transform": "cast",
                "input_ref": "object-def",
                "output": "casted_columns",
                "changes": [
                    {"column": "excavation_id", "data_type": "integer", "kwargs": {}},
                    {"column": "report_id", "data_type": "integer", "kwargs": {}},
                    {"column": "planned_quantity", "data_type": "double", "kwargs": {}},
                    {"column": "daily_quantity", "data_type": "double", "kwargs": {}},
                    {
                        "column": "cumulative_quantity",
                        "data_type": "double",
                        "kwargs": {},
                    },
                    {
                        "column": "adjustments_delta",
                        "data_type": "double",
                        "kwargs": {},
                    },
                ],
            },
            {
                "transform": "select_columns",
                "input": "casted_columns",
                "output": "select_all",
                "columns": [
                    "excavation_id",
                    "report_id",
                    "planned_quantity",
                    "daily_quantity",
                    "cumulative_quantity",
                    "adjustments_delta",
                ],
            },
        ],
        "finalisers": {
            "input": "select_all",
            "enable_quality": True,
            "write_config": {"mode": "overwrite"},
            "enable_profiling": True,
            "enable_classification": False,
        },
        "preview": False,
    }
