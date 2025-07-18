import os
import sys
import pytest
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError
import json
from dotenv import load_dotenv
from copy import deepcopy
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from test_data.shared.source_payload import create_source_payload
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

def get_headers(access_token):
    """Get standard headers for API requests."""
    return {
        "Authorization": f"Bearer {access_token}",
        "x-account": X_ACCOUNT,
        "Content-Type": "application/json"
    }

def record_api_info(request, method, url, payload, response):
    """Record API call information for test reporting."""
    request.node._api_info = {
        "method": method,
        "url": url,
        "payload": payload,
        "response": response.json() if response.ok else response.text()
    }

@pytest.fixture(scope="module")
def origin_ids():
    """Fixture to track origin IDs for cleanup."""
    ids = []
    yield ids
    # Cleanup at end of module
    print(f"\n🧹 Cleaning up {len(ids)} origins...")

class OriginApiHelper:
    """Helper class for origin API operations."""

    def __init__(self, context, access_token, origin_ids):
        self.context = context
        self.access_token = access_token
        self.origin_ids = origin_ids

    def create_origin(self, payload, request, add_to_cleanup=True):
        """Create an origin and optionally add to cleanup list."""
        headers = get_headers(self.access_token)
        response = self.context.post(
            "/api/data/origin",
            data=json.dumps(payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", payload, response)

        # Add to cleanup list if successful and requested
        if response.ok and add_to_cleanup:
            try:
                json_response = response.json()
                # Handle the nested response structure
                if "entity" in json_response and "identifier" in json_response["entity"]:
                    origin_id = json_response["entity"]["identifier"]
                    self.add_origin_to_cleanup(origin_id)
                    print(f"🧹 Added origin {origin_id} to cleanup list")
                elif "identifier" in json_response:
                    # Fallback for direct identifier
                    origin_id = json_response["identifier"]
                    self.add_origin_to_cleanup(origin_id)
                    print(f"🧹 Added origin {origin_id} to cleanup list (direct)")
                else:
                    print(f"⚠️ Warning: Could not find identifier in response for cleanup")
            except Exception as e:
                print(f"❌ Error adding origin to cleanup: {e}")

        return response

    def create_valid_origin(self, name_prefix, request):
        """Create a valid origin with a given name prefix."""
        payload = create_source_payload(name_prefix)
        return self.create_origin(payload, request)

    def add_origin_to_cleanup(self, origin_id):
        """Add origin ID to cleanup list."""
        if origin_id and origin_id not in self.origin_ids:
            self.origin_ids.append(origin_id)
            print(f"📝 Tracking origin {origin_id} for cleanup (total: {len(self.origin_ids)})")
        elif origin_id in self.origin_ids:
            print(f"ℹ️ Origin {origin_id} already tracked for cleanup")
        else:
            print(f"⚠️ Warning: Attempted to add empty/null origin ID to cleanup")

    def modify_payload(self, payload, field_path, value):
        """Modify a nested field in the payload."""
        modified_payload = deepcopy(payload)
        keys = field_path.split('.')
        current = modified_payload

        # Navigate to the parent of the target field
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the target field
        if value is None:
            if keys[-1] in current:
                del current[keys[-1]]
        else:
            current[keys[-1]] = value

        return modified_payload

@pytest.fixture(scope="module")
def valid_origin_payload():
    """Fixture to provide a valid origin payload."""
    return create_source_payload("Test Origin")

@pytest.fixture(scope="module")
def origin_api(api_context, origin_ids, request):
    """Fixture to provide an OriginApiHelper instance."""
    context, access_token = api_context
    return OriginApiHelper(context, access_token, origin_ids)

@pytest.fixture(scope="function")
def cleanup_created_origins():
    """Fixture to provide immediate cleanup function for origins."""
    created_origins = []

    def _cleanup_origin(origin_id):
        if origin_id not in created_origins:
            created_origins.append(origin_id)

    yield _cleanup_origin

    # Immediate cleanup of origins created in this test function
    # Note: This would require implementing delete functionality

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
                return error_response
            except:
                pytest.fail("Expected JSON error response")
        return None
    return _assert_error_response
