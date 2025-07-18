import os
import sys
import pytest
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError
import json
from dotenv import load_dotenv
from copy import deepcopy
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from test_data.shared.mesh_payload import create_mesh_payload
from utils.common import makeid

load_dotenv()

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")  # Get API token directly from .env
USERNAME = os.getenv("QA_USERNAME", "")  # Keep for fallback login
PASSWORD = os.getenv("QA_PASSWORD", "")  # Keep for fallback login
X_ACCOUNT = os.getenv("X_ACCOUNT", "")

@pytest.fixture(scope="session")
def api_context(playwright: Playwright):
    """Create API request context and get access token directly from environment variable,
    with fallback to login if token not provided."""
    context = playwright.request.new_context(base_url=BASE_URL)
    access_token = API_TOKEN

    # If API token is not set, try logging in
    if not access_token and USERNAME and PASSWORD:
        print("⚠️ API_TOKEN not found, attempting login with credentials...")
        try:
            login_payload = {"user": USERNAME, "password": PASSWORD}
            response = context.post("/api/iam/login",
                                   data=json.dumps(login_payload),
                                   headers={"Content-Type": "application/json"})
            access_token = response.json().get("access_token")
            print("✅ Successfully logged in and obtained access token")
            print(f"ℹ️ To avoid logging in next time, add to your .env file: API_TOKEN={access_token}")
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            access_token = None

    # Skip if we still don't have a token
    if not access_token:
        print("⚠️ Warning: No API token available. Tests requiring authentication will fail.")

    yield context, access_token
    context.dispose()

@pytest.fixture(scope="module")
def mesh_test_data():
    """Fixture to provide test data for mesh API tests."""
    return {
        "basic_mesh": {
            "name": "Basic Test Mesh",
            "description": "A mesh for basic testing",
            "purpose": "Testing purposes only"
        },
        "special_chars": [
            "!@#$%^&*()",
            "Test-with-hyphens",
            "Test_with_underscores",
            "Test with spaces"
        ],
        "invalid_inputs": {
            "empty_name": "",
            "too_long_name": "A" * 1000,
            "empty_description": "",
            "invalid_email": "not-an-email"
        }
    }

@pytest.fixture(scope="module")
def mesh_ids(api_context, request):
    """Fixture to store mesh IDs created during tests for cleanup."""
    context, access_token = api_context
    created_meshes = []

    # Create a node ID-based attribute to ensure unique storage per test module
    node_id = request.node.nodeid.split("::")[0]
    attr_name = f"_mesh_ids_{node_id.replace('/', '_').replace('.', '_')}"

    # Store on module level to ensure sharing between parallel processes
    if not hasattr(pytest, attr_name):
        setattr(pytest, attr_name, [])

    yield getattr(pytest, attr_name)

    # Cleanup - delete all created meshes
    mesh_ids_to_cleanup = getattr(pytest, attr_name)
    if access_token and mesh_ids_to_cleanup:
        print(f"\n=== Cleaning up {len(mesh_ids_to_cleanup)} mesh entities from {node_id}... ===")
        headers = get_headers(access_token)

        for mesh_id in mesh_ids_to_cleanup:
            try:
                # Using identifier query parameter as required by the API
                response = context.delete(f"/api/data/mesh?identifier={mesh_id}", headers=headers)
                if response.ok:
                    print(f"✅ Successfully deleted mesh: {mesh_id}")
                else:
                    print(f"❌ Failed to delete mesh {mesh_id}: {response.status} - {response.text()}")
            except Exception as e:
                print(f"❌ Error deleting mesh {mesh_id}: {str(e)}")
        print(f"=== Cleanup completed for {node_id} ===\n")

        # Clear the list after cleanup
        setattr(pytest, attr_name, [])

# Common helper functions for mesh tests
def get_headers(token):
    """Helper function to get request headers."""
    return {
        "Authorization": f"Bearer {token}",
        "x-account": os.getenv("X_ACCOUNT", ""),
        "Content-Type": "application/json"
    }

def record_api_info(request, method, url, payload, response):
    """Helper function to record API call information for reporting."""
    request.node._api_info = {
        "method": method,
        "url": url,
        "payload": payload,
        "response": response.json() if hasattr(response, 'json') and callable(response.json) else response
    }

class MeshApiHelper:
    """Helper class for mesh API operations."""

    def __init__(self, context, access_token, mesh_ids):
        self.context = context
        self.access_token = access_token
        self.mesh_ids = mesh_ids  # This is now a shared list across parallel tests
        self.base_url = "/api/data/mesh"

    def create_mesh(self, payload, request=None, add_to_cleanup=True):
        """Create a mesh with the given payload."""
        response = self.context.post(
            self.base_url,
            data=json.dumps(payload) if isinstance(payload, dict) else payload,
            headers=get_headers(self.access_token)
        )

        # Record API info if request object is provided
        if request:
            record_api_info(request, "POST", self.base_url, payload, response)

        # Add mesh ID to cleanup list if successful and cleanup is requested
        if response.ok and add_to_cleanup:
            try:
                mesh_id = response.json()["entity"]["identifier"]
                # Append to the shared list in a thread-safe way
                if mesh_id not in self.mesh_ids:
                    self.mesh_ids.append(mesh_id)
            except (KeyError, json.JSONDecodeError):
                pass

        return response

    def create_valid_mesh(self, name=None, request=None):
        """Create a mesh with valid payload."""
        payload = create_mesh_payload(name or f"Test Mesh {makeid(5)}")
        return self.create_mesh(payload, request)

    def modify_payload(self, base_payload, field_path, value):
        """Modify a nested field in the payload."""
        payload = deepcopy(base_payload)
        parts = field_path.split('.')

        # Navigate to the nested field
        target = payload
        for i, part in enumerate(parts[:-1]):
            if part not in target:
                target[part] = {}
            target = target[part]

        # Set or delete the field
        if value is None:
            if parts[-1] in target:
                del target[parts[-1]]
        else:
            target[parts[-1]] = value

        return payload

# Decorator for tests requiring authentication
def requires_auth(func):
    """Decorator to skip tests if authentication is not available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract api_context from kwargs
        api_context = kwargs.get('api_context')

        # If not in kwargs, try to find it in args
        if api_context is None:
            for arg in args:
                if isinstance(arg, tuple) and len(arg) == 2:
                    # This might be api_context (context, token)
                    context, token = arg
                    if hasattr(context, 'post') and isinstance(token, str):
                        api_context = arg
                        break

        if api_context:
            context, access_token = api_context

        return func(*args, **kwargs)
    return wrapper

@pytest.fixture(scope="module")
def valid_mesh_payload():
    """Fixture to provide a valid mesh payload."""
    return create_mesh_payload("Test Mesh")

@pytest.fixture(scope="module")
def mesh_api(api_context, mesh_ids, request):
    """Fixture to provide a MeshApiHelper instance."""
    context, access_token = api_context
    return MeshApiHelper(context, access_token, mesh_ids)

@pytest.fixture(scope="function")
def assert_status():
    """Fixture to provide a function for asserting response status codes."""
    def _assert_status(response, expected_status, message=None):
        assert response.status == expected_status, message or f"Expected status {expected_status}, got {response.status}"
    return _assert_status

@pytest.fixture(scope="function")
def assert_error_response():
    """Fixture to provide a function for asserting error response structure."""
    def _assert_error_response(response):
        if not response.ok:
            try:
                error_response = response.json()
                assert "errors" in error_response, "Error response missing 'errors' field"
                assert "status" in error_response, "Error response missing 'status' field"
                assert "title" in error_response, "Error response missing 'title' field"
                assert isinstance(error_response["errors"], list), "'errors' field should be a list"
                return error_response
            except json.JSONDecodeError:
                pytest.fail("Error response is not valid JSON")
        else:
            pytest.fail("Response was successful, expected an error")
    return _assert_error_response
