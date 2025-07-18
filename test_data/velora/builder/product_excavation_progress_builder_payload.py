import os


def product_excavation_progress_builder_payload():

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
        "input_refs": ["sadp-1", "sadp-2"],
        "transformations": [
            {
                "transform": "join_rename_select",
                "input_ref": "sadp-1",
                "output": "joined_data",
                "other_ref": "sadp-2",
                "join": "inner",
                "conditions": [
                    {"left": "report_id", "operator": "eq", "right": "report_id"}
                ],
                "select_columns": [
                    "contractor_id",
                    "project",
                    "report_date",
                    "planned_quantity",
                    "daily_quantity",
                    "cumulative_quantity",
                    "shift",
                ],
                "select_all_columns": False,
                "rename_columns": {
                    "left_contractor_id": "contractor_id",
                    "left_project": "project",
                    "left_report_date": "report_date",
                    "right_planned_quantity": "planned_quantity",
                    "right_daily_quantity": "daily_quantity",
                    "right_cumulative_quantity": "cumulative_quantity",
                    "left_shift": "shift",
                },
            },
            {
                "transform": "select_expression",
                "input": "joined_data",
                "output": "final_output",
                "expressions": [
                    "contractor_id",
                    "project",
                    "to_date(report_date) as date",
                    "shift",
                    "daily_quantity as daily_excavation_volume",
                    "planned_quantity as planned_excavation",
                    "daily_quantity - planned_quantity as excavation_variance",
                    "cumulative_quantity as cumulative_excavation_progress",
                    "CAST(daily_quantity/planned_quantity*100 as DOUBLE) as schedule_adherence",
                ],
            },
        ],
        "finalisers": {
            "input": "final_output",
            "enable_quality": True,
            "write_config": {"mode": "overwrite"},
            "enable_profiling": True,
            "enable_classification": False,
        },
        "preview": False,
    }
