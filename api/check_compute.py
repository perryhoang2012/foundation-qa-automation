from config import API_ENDPOINTS
from utils.common import record_api_info, get_headers


def check_status_compute(context, identifier, access_token, request):
    """
    Check the compute status.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging
    """
    url = f"{API_ENDPOINTS['CHECK_COMPUTE']}/?identifier={identifier}"
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response
