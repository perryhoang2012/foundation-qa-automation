"""
Source step operations for API testing.

This module provides functions to interact with source-related API endpoints
including creating, reading, deleting, linking, and configuring source resources.
"""

import json

from constants import API_ENDPOINTS
from utils import record_api_info, get_headers


def get_all_source(context, access_token, request):
    """
    Retrieve all source resources from the API.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing all source resources
    """
    url = API_ENDPOINTS["SOURCE"]
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def get_source_by_id(context, source_id, access_token, request):
    """
    Retrieve a source resource by its identifier.

    Args:
        context: The API request context
        source_id: The identifier of the source to retrieve

    Returns:
        API response containing the source resource
    """
    url = f"{API_ENDPOINTS['SOURCE']}/{source_id}"
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def create_source(context, payload, access_token, request):
    """
    Create a new source resource via API.

    Args:
        context: The API request context
        payload: The source data to create
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing the created source resource
    """
    url = API_ENDPOINTS["SOURCE"]
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response


def delete_source(context, source_id, access_token, request):
    """
    Delete a source resource by its identifier.

    Args:
        context: The API request context
        source_id: The identifier of the source to delete
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the deletion result
    """
    url = f"{API_ENDPOINTS['SOURCE']}/?identifier={source_id}"
    headers = get_headers(access_token)

    response = context.delete(url, headers=headers)
    record_api_info(request, "DELETE", url, {}, response)

    return response


def link_system_to_source(
    context,
    system_entity,
    source_entity,
    access_token,
    request,
):
    """
    Link a system entity to a source entity.

    Args:
        context: The API request context
        system_entity: The system entity to link
        source_entity: The source entity to link to
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the linking result
    """
    url = API_ENDPOINTS["LINK_SYSTEM_TO_SOURCE"]
    headers = get_headers(access_token)
    params = {
        "identifier": system_entity["identifier"],
        "child_identifier": source_entity["identifier"],
    }

    response = context.post(url, params=params, headers=headers)
    record_api_info(request, "POST", url, params, response)

    return response


def config_connection_detail_source(
    context,
    source_entity,
    payload,
    access_token,
    request,
):
    """
    Configure connection details for a source entity.

    Args:
        context: The API request context
        source_entity: The source entity to configure
        payload: The connection configuration data
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the configuration result
    """
    url = f"{API_ENDPOINTS['CONFIG_CONNECTION_DETAIL_SOURCE']}/?identifier={source_entity['identifier']}"
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.put(url, data=data, headers=headers)
    record_api_info(request, "PUT", url, payload, response)

    return response


def set_connection_secret(
    context,
    source_entity,
    payload,
    access_token,
    request,
):
    """
    Set connection secrets for a source entity.

    Args:
        context: The API request context
        source_entity: The source entity to configure secrets for
        payload: The secret configuration data
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the secret setting result
    """
    url = f"{API_ENDPOINTS['SET_CONNECTION_SECRET']}/?identifier={source_entity['identifier']}"
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response
