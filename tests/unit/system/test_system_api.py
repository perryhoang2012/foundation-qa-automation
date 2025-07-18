import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.system_payload import create_system_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

class TestSystemAPI:
    """Test suite for POST /api/data/data_system endpoint"""

    def test_create_system_with_valid_payload(self, api_context, request, system_ids, system_api):
        """Test creating a data system with a valid payload."""
        context, access_token = api_context

        response = system_api.create_valid_system("Valid System", request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"
        json_response = response.json()
        assert "identifier" in json_response, "Response missing 'identifier' field"
        assert json_response["name"].startswith("Valid System"), "Name in response doesn't match payload"
        # Note: entity_type is not returned in the response, so we don't assert it

    def test_create_system_without_name(self, api_context, request, valid_system_payload, system_ids, system_api, assert_status):
        """Test creating a system without providing a name."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.name", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")
        # Check for appropriate error message about missing name
        error_response = response.json()
        assert "errors" in error_response, "Error response should contain 'errors' field"

    def test_create_system_with_empty_name(self, api_context, request, valid_system_payload, system_ids, system_api, assert_status, assert_error_response):
        """Test creating a system with an empty name string."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.name", "")
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        # Expecting validation error for empty name
        assert not response.ok, "Request should fail with empty name"
        assert_status(response, 422, f"Expected 422 status code for validation error, got {response.status}")

    def test_create_system_without_entity_type(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system without entity_type field."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.entity_type", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")

    def test_create_system_with_invalid_entity_type(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system with invalid entity_type."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.entity_type", "invalid_type")
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code for invalid entity type, got {response.status}")

    def test_create_system_without_owner_email(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system without owner email."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.owner_person.email", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")

    def test_create_system_with_invalid_email_format(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system with invalid email format."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.owner_person.email", "invalid-email")
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code for invalid email, got {response.status}")

    def test_create_system_without_owner_name(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system without owner full name."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.owner_person.full_name", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")

    def test_create_system_without_label(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system without label field."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity.label", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")

    def test_create_system_without_entity_info_owner(self, api_context, request, valid_system_payload, system_api, assert_status):
        """Test creating a system without entity_info.owner field."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity_info.owner", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert_status(response, 422, f"Expected 422 status code, got {response.status}")

    def test_create_system_without_x_account_header(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system without x-account header."""
        context, access_token = api_context

        # Create headers without x-account
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/data_system",
            data=json.dumps(valid_system_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", valid_system_payload, response)

        assert response.status == 422, f"Expected 422 status code for missing x-account header, got {response.status}"

        # No cleanup needed as the request should fail

    def test_create_system_with_invalid_authorization(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with invalid authorization token."""
        context, access_token = api_context

        headers = {
            "Authorization": "Bearer invalid_token",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/data_system",
            data=json.dumps(valid_system_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", valid_system_payload, response)

        assert response.status == 401, f"Expected 401 status code for invalid token, got {response.status}"

        # No cleanup needed as the request should fail

    def test_create_system_without_authorization_header(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system without authorization header."""
        context, access_token = api_context

        headers = {
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/data_system",
            data=json.dumps(valid_system_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", valid_system_payload, response)

        assert response.status == 401, f"Expected 401 status code for missing authorization, got {response.status}"

        # No cleanup needed as the request should fail

    def test_create_system_with_special_characters_in_name(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with special characters in name."""
        context, access_token = api_context

        # Test valid special characters according to pattern: ^[a-zA-Z_][a-zA-Z0-9_\- ]{2,249}$
        valid_special_names = [
            "System with spaces",
            "System-with-hyphens",
            "System_with_underscores",
            "System_123_numbers"
        ]

        for special_name in valid_special_names:
            payload = system_api.modify_payload(valid_system_payload, "entity.name", special_name)
            response = system_api.create_system(payload, request)

            assert response.ok, f"Request failed for name '{special_name}': {response.status} - {response.text()}"
            json_response = response.json()
            assert json_response["name"] == special_name

        # Test invalid special characters that should be rejected
        invalid_special_names = [
            "System.with.dots",
            "System (with parentheses)",
            "System@with@at",
            "123StartWithNumber",
            "System#with#hash"
        ]

        for invalid_name in invalid_special_names:
            payload = system_api.modify_payload(valid_system_payload, "entity.name", invalid_name)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            assert response.status == 422, f"Invalid name '{invalid_name}' should be rejected with 422, got {response.status}"

    def test_create_system_with_long_name(self, api_context, request, valid_system_payload, system_api, cleanup_created_systems):
        """Test creating a system with a very long name."""
        context, access_token = api_context

        # Test with a 500 character name
        long_name = "A" * 500
        payload = system_api.modify_payload(valid_system_payload, "entity.name", long_name)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        # This might succeed or fail depending on business rules - adjust based on actual requirements
        if response.ok:
            json_response = response.json()
            assert json_response["name"] == long_name
            # Add to cleanup if successful
            if "identifier" in json_response:
                system_identifier = json_response["identifier"]
                system_api.add_system_to_cleanup(system_identifier)
                cleanup_created_systems(system_identifier)  # Also add to function cleanup for safety
        else:
            # If it fails, it should be a validation error
            assert response.status == 422, f"Expected 422 for long name, got {response.status}"

    def test_create_system_with_long_description(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with a very long description."""
        context, access_token = api_context

        # Test with a 999 character description (within limit)
        long_description = "This is a valid long description. " * 28  # Approximately 999 chars
        payload = system_api.modify_payload(valid_system_payload, "entity.description", long_description)
        response = system_api.create_system(payload, request)

        assert response.ok, f"Request failed for valid long description: {response.status} - {response.text()}"
        json_response = response.json()
        assert json_response["description"] == long_description

        # Test with a description exceeding 1000 characters (should fail)
        too_long_description = "A" * 1001  # Exceeds the 1000 character limit
        payload = system_api.modify_payload(valid_system_payload, "entity.description", too_long_description)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert response.status == 422, f"Description over 1000 chars should be rejected with 422, got {response.status}"

    def test_create_system_with_minimal_payload(self, api_context, request, system_api):
        """Test creating a system with minimal required fields only."""
        context, access_token = api_context

        minimal_payload = {
            "entity": {
                "name": f"Minimal System {makeid()}",
                "entity_type": "data_system",
                "label": "DSS",
                "description": "Minimal description",
                "owner_person": {
                    "email": os.getenv("OWNER_EMAIL", "test@example.com"),
                    "full_name": os.getenv("OWNER_NAME", "Test User"),
                },
            },
            "entity_info": {
                "owner": os.getenv("OWNER_EMAIL", "test@example.com"),
                "contact_ids": [],
                "links": [],
            },
        }

        response = system_api.create_system(minimal_payload, request)

        assert response.ok, f"Request failed for minimal payload: {response.status} - {response.text()}"
        json_response = response.json()
        assert "identifier" in json_response

    def test_create_system_with_empty_contact_ids(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with empty contact_ids array."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity_info.contact_ids", [])
        response = system_api.create_system(payload, request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"

    def test_create_system_with_empty_links(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with empty links array."""
        context, access_token = api_context

        payload = system_api.modify_payload(valid_system_payload, "entity_info.links", [])
        response = system_api.create_system(payload, request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"

    def test_create_system_with_malformed_json(self, api_context, request, system_api):
        """Test creating a system with malformed JSON payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        malformed_json = '{"entity": {"name": "Test"'  # Missing closing braces

        response = context.post(
            "/api/data/data_system",
            data=malformed_json,
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", malformed_json, response)

        assert response.status == 422, f"Expected 422 status code for malformed JSON, got {response.status}"

        # No cleanup needed as the request should fail

    def test_create_system_with_wrong_content_type(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with wrong Content-Type header."""
        context, access_token = api_context

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "text/plain"
        }

        response = context.post(
            "/api/data/data_system",
            data=json.dumps(valid_system_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", valid_system_payload, response)

        assert response.status == 500, f"Expected 500 status code for wrong content type, got {response.status}"

        # No cleanup needed as the request should fail

    def test_create_system_response_structure(self, api_context, request, system_api):
        """Test that the response structure matches expected format."""
        context, access_token = api_context

        response = system_api.create_valid_system("Response Structure Test", request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"
        json_response = response.json()

        # Validate response structure based on actual API response
        required_fields = ["identifier", "name", "description", "label", "created_at", "urn"]
        for field in required_fields:
            assert field in json_response, f"Response missing required field: {field}"

        # Validate data types
        assert isinstance(json_response["identifier"], str), "identifier should be a string"
        assert isinstance(json_response["name"], str), "name should be a string"
        assert isinstance(json_response["description"], str), "description should be a string"
        assert isinstance(json_response["label"], str), "label should be a string"
        assert isinstance(json_response["urn"], str), "urn should be a string"

        # Check if owner_person structure is included
        if "owner_person" in json_response:
            owner = json_response["owner_person"]
            assert "email" in owner, "owner_person missing email"
            assert "full_name" in owner, "owner_person missing full_name"

    def test_cleanup_mechanism_verification(self, api_context, request, system_api, cleanup_created_systems):
        """Test to verify that the cleanup mechanism works correctly."""
        context, access_token = api_context

        # Create a system specifically for testing cleanup
        response = system_api.create_valid_system("Cleanup Test System", request)

        assert response.ok, f"Failed to create test system: {response.status} - {response.text()}"
        json_response = response.json()
        system_id = json_response["identifier"]

        # Verify the system was created
        assert "identifier" in json_response
        assert json_response["name"].startswith("Cleanup Test System")

        # The system should be automatically added to cleanup via system_api.create_valid_system()
        assert system_id in system_api.system_ids, "System ID should be automatically tracked for cleanup"

        # Also add to function cleanup for immediate verification
        cleanup_created_systems(system_id)

        print(f"✅ Created system {system_id} for cleanup testing - it will be automatically cleaned up")
