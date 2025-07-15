"""
System step operations for API testing.

This module provides functions to interact with system-related API endpoints
including creating, reading, and deleting system resources.
"""

import json

from constants import API_ENDPOINTS
from utils import record_api_info, get_headers


def get_all_system(context, access_token, request):
    """
    Retrieve all system resources from the API.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing all system resources
    """
    url = API_ENDPOINTS["SYSTEM"]
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def create_system(context, payload, access_token, request):
    """
    Create a new system resource via API.

    Args:
        context: The API request context
        payload: The system data to create
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing the created system resource
    """
    url = API_ENDPOINTS["SYSTEM"]
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response


def delete_system(context, system_id, access_token, request):
    """
    Delete a system resource by its identifier.

    Args:
        context: The API request context
        system_id: The identifier of the system to delete
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the deletion result
    """
    url = API_ENDPOINTS["SYSTEM"]
    headers = get_headers(access_token)
    params = {"identifier": system_id}

    response = context.delete(url, params=params, headers=headers)
    record_api_info(request, "DELETE", url, {}, response)

    return response
