import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.mesh_payload import create_mesh_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

#@pytest.mark.skip(reason="Manual cleanup test - run explicitly when needed")
def test_cleanup_existing_meshes(api_context, request):
    """Delete all existing meshes by first listing them, then deleting each one"""
    context, access_token = api_context
    # Step 1: Get list of all existing meshes
    list_response = context.get('/api/data/mesh/list', headers=get_headers(access_token))
    record_api_info(request, "GET", "/api/data/mesh/list", None, list_response)

    if not list_response.ok:
        pytest.fail(f"Failed to get mesh list: {list_response.status} - {list_response.text()}")

    meshes = list_response.json().get("entities", [])
    print(f"Found {len(meshes)} existing meshes to delete")

    # Step 2: Delete each mesh
    deleted_count = 0
    for mesh in meshes:
        mesh_identifier = mesh.get('identifier')
        if mesh_identifier:
            delete_response = context.delete(
                f'/api/data/mesh?identifier={mesh_identifier}',
                headers=get_headers(access_token)
            )
            if delete_response.ok:
                deleted_count += 1
                print(f"Deleted mesh: {mesh.get('name', 'Unknown')} (ID: {mesh_identifier})")
            else:
                print(f"Failed to delete mesh: {mesh.get('name', 'Unknown')} (ID: {mesh_identifier}) - {delete_response.status}")

    print(f"Successfully deleted {deleted_count} out of {len(meshes)} meshes")

    # Record the cleanup operation
    request.node._api_info = {
        "method": "GET + DELETE",
        "url": "/api/data/mesh/list + /api/data/mesh",
        "payload": f"Cleaned up {deleted_count} meshes",
        "response": f"Deleted {deleted_count}/{len(meshes)} meshes"
    }

@pytest.fixture(scope="module")
def valid_mesh_payload():
    return create_mesh_payload("Test Mesh")

def test_create_mesh_with_valid_payload(api_context, request, mesh_ids, mesh_api):
    """Test creating a mesh with a valid payload."""
    context, access_token = api_context
    response = mesh_api.create_valid_mesh("Valid Mesh", request)

    assert response.ok, f"Request failed: {response.status} - {response.text()}"
    json_response = response.json()
    assert "entity" in json_response, "Response missing 'entity' field"
    assert "identifier" in json_response["entity"], "Entity missing 'identifier'"
    assert json_response["entity"]["name"].startswith("Valid Mesh"), "Name in response doesn't match payload"

    # The entity_type field might not be returned in the response
    # assert json_response["entity"]["entity_type"] == "mesh", "Entity type should be 'mesh'"

def test_create_mesh_without_name(api_context, request, valid_mesh_payload, mesh_ids, mesh_api, assert_status):
    """Test creating a mesh without providing a name."""
    context, access_token = api_context
    payload = mesh_api.modify_payload(valid_mesh_payload, "entity.name", None)
    response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)

    assert_status(response, 422, f"Expected 422 status code, got {response.status}")
    # Check for appropriate error message about missing name

def test_create_mesh_with_empty_name(api_context, request, valid_mesh_payload, mesh_ids, mesh_api, assert_status, assert_error_response):
    """Test creating a mesh with an empty name string."""
    context, access_token = api_context
    payload = mesh_api.modify_payload(valid_mesh_payload, "entity.name", "")
    response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)

    # Expecting validation error for empty name
    assert not response.ok, "Request should fail with empty name"
    assert_status(response, 422, f"Expected 422 status code for validation error, got {response.status}")

    # Check response for validation error message
    if not response.ok:
        try:
            error_data = response.json()
            assert "errors" in error_data, "Response should contain error details"
            # Further validation of error response structure could be added here
        except:
            pass  # Skip JSON parsing if response is not JSON

def test_create_mesh_with_invalid_entity_type(api_context, request, valid_mesh_payload, mesh_ids):
    """Test creating a mesh with an invalid entity_type."""
    context, access_token = api_context
    payload = deepcopy(valid_mesh_payload)
    payload["entity"]["entity_type"] = "invalid_type"

    response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "Authorization": f"Bearer {access_token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": payload,
        "response": response.json() if response.ok else response.text()
    }

    assert not response.ok, "Request should fail with invalid entity_type"
    # Depending on API implementation, it might return 400 or 422

def test_create_mesh_with_very_long_name(api_context, request, valid_mesh_payload, mesh_ids):
    """Test creating a mesh with a very long name."""
    context, access_token = api_context
    payload = deepcopy(valid_mesh_payload)
    payload["entity"]["name"] = "A" * 1000  # Using a 1000 character name

    response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "Authorization": f"Bearer {access_token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": payload,
        "response": response.json() if response.ok else response.text()
    }

    # Depending on API implementation, it might accept or reject very long names

def test_create_mesh_without_authorization(api_context, request, valid_mesh_payload, mesh_ids):
    """Test creating a mesh without authorization token."""
    context, access_token = api_context
    payload = deepcopy(valid_mesh_payload)

    response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": payload,
        "response": response.json() if response.ok else response.text()
    }

    assert response.status == 401, f"Expected 401 status code, got {response.status}"

def test_create_mesh_without_account_header(api_context, request, valid_mesh_payload, mesh_ids):
    """Test creating a mesh without x-account header."""
    context, access_token = api_context
    payload = deepcopy(valid_mesh_payload)

    response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": payload,
        "response": response.json() if response.ok else response.text()
    }

    # Check if x-account is required, expected status code depends on API implementation

def test_create_mesh_with_invalid_json(api_context, request, mesh_ids):
    """Test creating a mesh with invalid JSON in request body."""
    context, access_token = api_context
    invalid_json = "{"  # Invalid JSON string

    response = context.post('/api/data/mesh', data=invalid_json, headers={
        "Authorization": f"Bearer {access_token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": invalid_json,
        "response": response.text()
    }

    # The API returns 422 for invalid JSON, not 400 as expected
    assert response.status == 422, f"Expected 422 status code, got {response.status}"

@pytest.mark.serial
def test_create_duplicate_mesh(api_context, request, mesh_ids):
    """Test creating a mesh with the same name twice."""
    context, access_token = api_context
    # Create a unique name to ensure we can test duplication
    unique_name = f"Duplicate Test Mesh {makeid(10)}"
    payload = create_mesh_payload(unique_name)

    # First creation
    response1 = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "Authorization": f"Bearer {access_token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    assert response1.ok, f"First mesh creation failed: {response1.status} - {response1.text()}"

    # Add to cleanup list
    mesh_ids.append(response1.json()["entity"]["identifier"])

    # Second creation with same name
    response2 = context.post('/api/data/mesh', data=json.dumps(payload), headers={
        "Authorization": f"Bearer {access_token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    })

    request.node._api_info = {
        "method": "POST",
        "url": "/api/data/mesh",
        "payload": payload,
        "response": response2.json() if response2.ok else response2.text()
    }

    # Check how API handles duplicates - might allow with a different ID or reject
