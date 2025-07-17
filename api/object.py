"""
Object step operations for API testing.

This module provides functions to interact with object-related API endpoints
including creating, reading, deleting, linking, and configuring object resources.
"""

import json

from config import API_ENDPOINTS
from utils.common import record_api_info, get_headers


def get_all_object(context, access_token, request):
    """
    Retrieve all object resources from the API.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing all object resources
    """
    url = API_ENDPOINTS["OBJECT"]
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def get_object_by_id(context, object_id, access_token, request):
    """
    Retrieve a data object by its identifier.
    """
    url = f"{API_ENDPOINTS['OBJECT']}/?identifier={object_id}"
    headers = get_headers(access_token)
    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def create_object(context, payload, access_token, request):
    """
    Create a new object resource via API.

    Args:
        context: The API request context
        payload: The object data to create
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing the created object resource
    """
    url = API_ENDPOINTS["OBJECT"]
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response


def delete_object(context, object_id, access_token, request):
    """
    Delete an object resource by its identifier.

    Args:
        context: The API request context
        object_id: The identifier of the object to delete
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the deletion result
    """
    url = f"{API_ENDPOINTS['OBJECT']}/?identifier={object_id}"
    headers = get_headers(access_token)

    response = context.delete(url, headers=headers)
    record_api_info(request, "DELETE", url, {}, response)

    return response


def link_object_to_source(
    context,
    source_entity,
    object_entity,
    access_token,
    request,
):
    """
    Link an object entity to a source entity.

    Args:
        context: The API request context
        source_entity: The source entity to link to
        object_entity: The object entity to link
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the linking result
    """
    url = API_ENDPOINTS["LINK_OBJECT_TO_SOURCE"]
    headers = get_headers(access_token)
    params = {
        "identifier": source_entity["identifier"],
        "child_identifier": object_entity["identifier"],
    }

    response = context.post(url, params=params, headers=headers)
    record_api_info(request, "POST", url, params, response)

    return response


def config_object(
    context,
    object_entity,
    payload,
    access_token,
    request,
):
    """
    Configure an object entity with additional settings.

    Args:
        context: The API request context
        object_entity: The object entity to configure
        payload: The configuration data
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the configuration result
    """
    url = f"{API_ENDPOINTS['CONFIG_OBJECT']}/?identifier={object_entity['identifier']}"
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.put(url, data=data, headers=headers)
    record_api_info(request, "PUT", url, payload, response)

    return response
