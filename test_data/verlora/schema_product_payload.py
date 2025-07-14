def schema_product_create_payload():
    return {
        "details": {
            "product_type": "stored",
            "fields": [
                {
                    "name": "report_id",
                    "description": None,
                    "primary": True,
                    "optional": False,
                    "data_type": {
                        "meta": {},
                        "column_type": "INTEGER",
                    },
                    "classification": "internal",
                    "sensitivity": None,
                    "tags": [],
                },
                {
                    "name": "contractor_id",
                    "description": None,
                    "primary": False,
                    "optional": False,
                    "data_type": {
                        "meta": {},
                        "column_type": "VARCHAR",
                    },
                    "classification": "internal",
                    "sensitivity": None,
                    "tags": [],
                },
                {
                    "name": "project",
                    "description": None,
                    "primary": False,
                    "optional": False,
                    "data_type": {
                        "meta": {},
                        "column_type": "VARCHAR",
                    },
                    "classification": "internal",
                    "sensitivity": None,
                    "tags": [],
                },
                {
                    "name": "report_date",
                    "description": None,
                    "primary": False,
                    "optional": False,
                    "data_type": {
                        "meta": {},
                        "column_type": "VARCHAR",
                    },
                    "classification": "internal",
                    "sensitivity": None,
                    "tags": [],
                },
                {
                    "name": "shift",
                    "description": None,
                    "primary": False,
                    "optional": False,
                    "data_type": {
                        "meta": {},
                        "column_type": "VARCHAR",
                    },
                    "classification": "internal",
                    "sensitivity": None,
                    "tags": [],
                },
            ],
        },
    }
