"""
Mesh step operations for API testing.

This module provides functions to interact with mesh-related API endpoints
including creating, reading, and deleting mesh resources.
"""

import json

from config import API_ENDPOINTS
from utils.common import record_api_info, get_headers


def get_all_mesh(context, access_token, request):
    """
    Retrieve all mesh resources from the API.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing all mesh resources
    """
    url = API_ENDPOINTS["MESH"]
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def create_mesh(context, payload, access_token, request):
    """
    Create a new mesh resource via API.

    Args:
        context: The API request context
        payload: The mesh data to create
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing the created mesh resource
    """
    url = API_ENDPOINTS["MESH"]
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response


def delete_mesh(context, mesh_id, access_token, request):
    """
    Delete a mesh resource by its identifier.

    Args:
        context: The API request context
        mesh_id: The identifier of the mesh to delete
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the deletion result
    """
    url = f"{API_ENDPOINTS['MESH']}/?identifier={mesh_id}"
    headers = get_headers(access_token)

    response = context.delete(url, headers=headers)
    record_api_info(request, "DELETE", url, {}, response)

    return response
