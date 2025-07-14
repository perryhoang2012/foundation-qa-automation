import os

def create_transformation_builder_payload(data_object_id: str):
    input_key = f"input_{data_object_id.replace('-', '_')}"

    transformation_input = {
        "input_type": "resource",
        "identifier": data_object_id,
        "preview_limit": 10,
    }

    return {
        "config": {
            "docker_tag": os.getenv("DOCKER_TAG", ""),
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
        "inputs": {
            input_key: transformation_input,
        },
        "transformations": [
            {
                "transform": "cast",
                "input": input_key,
                "output": "casted_columns",
                "changes": [
                    {
                        "column": "report_id",
                        "data_type": "integer",
                        "kwargs": {},
                    },
                ],
            },
            {
                "transform": "select_columns",
                "input": "casted_columns",
                "output": "select_all",
                "columns": [
                    "report_id",
                    "contractor_id",
                    "project",
                    "report_date",
                    "shift",
                ],
            },
        ],
        "finalisers": {
            "input": "select_all",
            "enable_quality": True,
            "write_config": {
                "mode": "overwrite",
            },
            "enable_profiling": True,
            "enable_classification": False,
        },
        "preview": False,
    }
