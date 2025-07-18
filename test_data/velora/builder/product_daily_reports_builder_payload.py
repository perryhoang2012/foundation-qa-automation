import os


def product_daily_reports_builder_payload():

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
        "input_refs": ["object-abc"],
        "transformations": [
            {
                "transform": "cast",
                "input_ref": "object-abc",
                "output": "casted_columns",
                "changes": [
                    {"column": "report_id", "data_type": "integer", "kwargs": {}}
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
            "write_config": {"mode": "overwrite"},
            "enable_profiling": True,
            "enable_classification": False,
        },
        "preview": False,
    }
