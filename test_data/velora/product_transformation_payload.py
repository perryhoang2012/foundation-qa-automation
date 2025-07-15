import os

def create_transformation_builder_payload(identifier = None):
    if(identifier is not None):
        input_key = f"input_{identifier.replace('-', '_')}"

        transformation_input = {
            "input_type": "resource",
            "identifier": identifier,
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

def create_transformation_builder_payload_with_inputs(input_entities = None):
    if(input_entities is not None):
        input_keys_dict = {}
        transformations = []
        for input_entity in input_entities:
            input_key = f"input_{input_entity['identifier'].replace('-', '_')}"
            input_keys_dict[input_key] = {
                "input_type": "resource",
                "identifier": input_entity["identifier"],
                "preview_limit": 10,
            }
            transformations.append({
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
            })

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
            "inputs": input_keys_dict,
            "transformations": transformations + [
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
