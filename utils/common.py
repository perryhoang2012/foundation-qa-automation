import random
import string
import json
import os
import pytest

X_ACCOUNT = os.getenv("X_ACCOUNT", "")


def makeid(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "x-account": X_ACCOUNT,
        "Content-Type": "application/json",
    }


def register_entity(id_map, entity):
    key = entity.get("id") or entity.get("identifier")
    if key is not None:
        if key in id_map:
            id_map[key].update(entity)
        else:
            id_map[key] = entity
    else:
        raise ValueError("Entity must have 'id' or 'identifier'")


def find_entity(id_map, entity_id):
    return id_map.get(entity_id)


def record_api_info(request, method, url, payload, response):
    response_result = response if isinstance(response, str) else response.json() if response else None
    request.node._api_info = {
        "method": method,
        "url": url,
        "payload": payload,
        "response": response_result,
    }
    print(method, url)
    print('Payload:', json.dumps(payload, indent = 2))
    print('Response:', json.dumps(response_result, indent = 2))


def skip_if_no_token(access_token: str) -> None:
    """
    Skip test if no access token is available.

    Args:
        access_token: The access token to check
    """
    if not access_token:
        pytest.skip("Skipping test: Access token not found")


def assert_entity_created(response) -> str:
    """
    Assert that an entity was created and return its identifier.

    Args:
        response: The API response to check

    Returns:
        The identifier of the created entity

    Raises:
        pytest.fail: If the response indicates failure or missing data
    """
    try:
        if not response.ok:
            pytest.fail(f"Request failed: {response.status} - {response.text()}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")

    entity = response.json().get("entity")
    assert entity is not None, "Response missing 'entity'"
    identifier = entity.get("identifier")
    assert identifier is not None, "Entity missing 'identifier'"
    return identifier


def assert_success_response(response):
    """
    Assert that the response indicates success.

    Args:
        response: The API response to check

    Raises:
        pytest.fail: If the response indicates failure
    """
    try:
        if not response.ok:
            text = response.text()
            pytest.fail(f"Request failed: {response.status} - {text}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")
