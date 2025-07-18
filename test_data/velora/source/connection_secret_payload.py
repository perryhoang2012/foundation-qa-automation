import os


def create_connection_secret_payload():
    return {
        "MY_S3_ACCESS": os.getenv("S3_ACCESS_KEY", ""),
        "MY_S3_SECRET": os.getenv("S3_SECRET_KEY", ""),
    }
