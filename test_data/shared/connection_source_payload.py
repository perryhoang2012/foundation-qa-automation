import os

def create_connection_source_payload():
    return {
        "connection": {
            "connection_type": "s3",
            "url": os.getenv("S3_URL", ""),
            "access_key": {"env_key": "MY_S3_ACCESS"},
            "access_secret": {"env_key": "MY_S3_SECRET"},
        }
    }
