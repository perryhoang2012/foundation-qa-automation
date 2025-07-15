import os

X_ACCOUNT = os.getenv("X_ACCOUNT", "")


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "x-account": X_ACCOUNT,
        "Content-Type": "application/json",
    }
