import os
import sys
import pytest
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError
import json
from dotenv import load_dotenv
from copy import deepcopy
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from test_data.shared.system_payload import create_system_payload
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
def system_test_data():
    """Fixture to provide test data for system API tests."""
    return {
        "basic_system": {
            "name": "Basic Test System",
            "description": "A data system for basic testing",
            "label": "DSS"
        },
        "special_chars": [
            "!@#$%^&*()",
            "System-with-hyphens",
            "System_with_underscores",
            "System with spaces"
        ],
        "invalid_inputs": {
            "empty_name": "",
            "too_long_name": "A" * 1000,
            "empty_description": "",
            "invalid_email": "not-an-email",
            "invalid_entity_type": "invalid_type"
        }
    }

@pytest.fixture(scope="module")
def system_ids(api_context, request):
    """Fixture to store system IDs created during tests for cleanup."""
    context, access_token = api_context
    created_systems = []

    # Create a node ID-based attribute to ensure unique storage per test module
    node_id = request.node.nodeid.split("::")[0]
    attr_name = f"_system_ids_{node_id.replace('/', '_').replace('.', '_')}"

    # Store on module level to ensure sharing between parallel processes
    if not hasattr(pytest, attr_name):
        setattr(pytest, attr_name, [])

    yield getattr(pytest, attr_name)

    # Cleanup - delete all created systems
    system_ids_to_cleanup = getattr(pytest, attr_name)
    if access_token and system_ids_to_cleanup:
        print(f"\n=== Cleaning up {len(system_ids_to_cleanup)} system entities from {node_id}... ===")
        headers = get_headers(access_token)

        for system_id in system_ids_to_cleanup:
            try:
                # Using identifier query parameter as required by the API
                response = context.delete(f"/api/data/data_system?identifier={system_id}", headers=headers)
                if response.ok:
                    print(f"✅ Successfully deleted system: {system_id}")
                else:
                    print(f"❌ Failed to delete system {system_id}: {response.status} - {response.text()}")
            except Exception as e:
                print(f"❌ Error deleting system {system_id}: {str(e)}")
        print(f"=== Cleanup completed for {node_id} ===\n")

        # Clear the list after cleanup
        setattr(pytest, attr_name, [])

# Common helper functions for system tests
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

class SystemApiHelper:
    """Helper class for system API operations."""

    def __init__(self, context, access_token, system_ids):
        self.context = context
        self.access_token = access_token
        self.system_ids = system_ids  # This is now a shared list across parallel tests
        self.base_url = "/api/data/data_system"

    def create_system(self, payload, request=None, add_to_cleanup=True):
        """Create a system with the given payload."""
        response = self.context.post(
            self.base_url,
            data=json.dumps(payload) if isinstance(payload, dict) else payload,
            headers=get_headers(self.access_token)
        )

        # Record API info if request object is provided
        if request:
            record_api_info(request, "POST", self.base_url, payload, response)

        # Add system ID to cleanup list if successful and cleanup is requested
        if response.ok and add_to_cleanup:
            try:
                system_id = response.json()["identifier"]
                # Append to the shared list in a thread-safe way
                if system_id not in self.system_ids:
                    self.system_ids.append(system_id)
            except (KeyError, json.JSONDecodeError):
                pass

        return response

    def create_valid_system(self, name=None, request=None):
        """Create a system with valid payload."""
        payload = create_system_payload(name or f"Test System {makeid(5)}")
        return self.create_system(payload, request)

    def add_system_to_cleanup(self, system_identifier):
        """Manually add a system identifier to cleanup list."""
        if system_identifier and system_identifier not in self.system_ids:
            self.system_ids.append(system_identifier)

    def cleanup_system(self, system_identifier):
        """Manually cleanup a specific system."""
        try:
            response = self.context.delete(f"{self.base_url}?identifier={system_identifier}", headers=get_headers(self.access_token))
            if response.ok:
                print(f"✅ Manually cleaned up system: {system_identifier}")
                # Remove from cleanup list if it's there
                if system_identifier in self.system_ids:
                    self.system_ids.remove(system_identifier)
                return True
            else:
                print(f"❌ Failed to manually cleanup system {system_identifier}: {response.status}")
                return False
        except Exception as e:
            print(f"❌ Error manually cleaning up system {system_identifier}: {str(e)}")
            return False

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
def valid_system_payload():
    """Fixture to provide a valid system payload."""
    return create_system_payload("Test System")

@pytest.fixture(scope="module")
def system_api(api_context, system_ids, request):
    """Fixture to provide a SystemApiHelper instance."""
    context, access_token = api_context
    return SystemApiHelper(context, access_token, system_ids)

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

@pytest.fixture(scope="function")
def cleanup_created_systems(api_context):
    """Function-scoped fixture for immediate cleanup of systems created in a test."""
    created_system_ids = []

    def add_for_cleanup(system_id):
        """Add a system ID to be cleaned up at the end of this test."""
        if system_id and system_id not in created_system_ids:
            created_system_ids.append(system_id)

    yield add_for_cleanup

    # Cleanup all systems created in this test
    context, access_token = api_context
    if access_token and created_system_ids:
        headers = get_headers(access_token)
        for system_id in created_system_ids:
            try:
                response = context.delete(f"/api/data/data_system?identifier={system_id}", headers=headers)
                if response.ok:
                    print(f"🧹 Function cleanup: Successfully deleted system {system_id}")
                else:
                    print(f"🧹 Function cleanup: Failed to delete system {system_id}: {response.status}")
            except Exception as e:
                print(f"🧹 Function cleanup: Error deleting system {system_id}: {str(e)}")
