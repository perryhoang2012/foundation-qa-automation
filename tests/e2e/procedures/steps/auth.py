import json
from config import API_ENDPOINTS


def login(context, payload):
    """
    Login to the API.

    Args:
        context: The API request context
        payload: The login payload
        access_token: Authentication token for API access
        request: The test request object for logging
    """
    url = API_ENDPOINTS["LOGIN"]

    response = context.post(
        url, data=json.dumps(payload), headers=({"Content-Type": "application/json"})
    )

    return response
