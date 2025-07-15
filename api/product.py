import json

from config import API_ENDPOINTS
from utils.common import record_api_info, get_headers


def get_all_product(context, access_token, request):
    """
    Retrieve all product resources from the API.

    Args:
        context: The API request context
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing all product resources
    """
    url = API_ENDPOINTS["PRODUCT"]
    headers = get_headers(access_token)

    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)

    return response


def get_product_by_id(context, product_id, access_token, request):
    """
    Retrieve a product resource by its identifier.
    """
    url = f"{API_ENDPOINTS['PRODUCT']}/?identifier={product_id}"
    headers = get_headers(access_token)
    response = context.get(url, headers=headers)
    record_api_info(request, "GET", url, {}, response)
    return response


def create_product(context, payload, access_token, request):
    """
    Create a new product resource via API.

    Args:
        context: The API request context
        payload: The product data to create
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response containing the created product resource
    """
    url = API_ENDPOINTS["PRODUCT"]
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.post(url, data=data, headers=headers)
    record_api_info(request, "POST", url, payload, response)

    return response


def delete_product(context, product_id, access_token, request):
    """
    Delete a product resource by its identifier.

    Args:
        context: The API request context
        product_id: The identifier of the product to delete
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the deletion result
    """
    url = f"{API_ENDPOINTS['PRODUCT']}/?identifier={product_id}"
    headers = get_headers(access_token)

    response = context.delete(url, headers=headers)
    record_api_info(request, "DELETE", url, {}, response)

    return response


def link_product_to_object(
    context,
    product_entity,
    object_entity,
    access_token,
    request,
):
    """
    Link a product entity to an object entity.

    Args:
        context: The API request context
        product_entity: The product entity to link
        object_entity: The object entity to link to
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the linking result
    """
    url = API_ENDPOINTS["LINK_PRODUCT_TO_OBJECT"]
    headers = get_headers(access_token)
    params = {
        "identifier": product_entity["identifier"],
        "child_identifier": object_entity["identifier"],
    }

    response = context.post(url, params=params, headers=headers)
    record_api_info(request, "POST", url, params, response)

    return response


def link_product_to_product(
    context,
    product_entity,
    product_child_entity,
    access_token,
    request,
):
    """
    Link a product entity to another product entity (parent-child relationship).

    Args:
        context: The API request context
        product_entity: The parent product entity
        product_child_entity: The child product entity to link
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the linking result
    """
    url = API_ENDPOINTS["LINK_PRODUCT_TO_PRODUCT"]
    headers = get_headers(access_token)
    params = {
        "identifier": product_entity["identifier"],
        "child_identifier": product_child_entity["identifier"],
    }

    response = context.post(url, params=params, headers=headers)
    record_api_info(request, "POST", url, params, response)

    return response


def create_data_product_schema(
    context,
    product_entity,
    payload,
    access_token,
    request,
):
    """
    Create a data product schema for a product entity.

    Args:
        context: The API request context
        product_entity: The product entity to create schema for
        payload: The schema configuration data
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the schema creation result
    """
    url = (
        f"{API_ENDPOINTS['SCHEMA_PRODUCT']}/?identifier={product_entity['identifier']}"
    )
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.put(url, data=data, headers=headers)
    record_api_info(request, "PUT", url, payload, response)

    return response


def create_transformation_builder(
    context,
    product_entity,
    payload,
    access_token,
    request,
):
    """
    Create a transformation builder for a product entity.

    Args:
        context: The API request context
        product_entity: The product entity to create transformation for
        payload: The transformation configuration data
        access_token: Authentication token for API access
        request: The test request object for logging

    Returns:
        API response indicating the transformation builder creation result
    """
    url = f"{API_ENDPOINTS['TRANSFORMATION_BUILDER']}/?identifier={product_entity['identifier']}"
    headers = get_headers(access_token)
    data = json.dumps(payload)

    response = context.put(url, data=data, headers=headers)
    record_api_info(request, "PUT", url, payload, response)

    return response
