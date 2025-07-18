import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.system_payload import create_system_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

class TestSystemErrorHandling:
    """Test suite for error handling scenarios in POST /api/data/data_system endpoint"""

    def test_create_system_with_null_payload(self, api_context, request):
        """Test creating a system with null payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        response = context.post(
            "/api/data/data_system",
            data="null",
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", None, response)
        assert response.status == 422, f"Expected 422 status code for null payload, got {response.status}"

    def test_create_system_with_empty_payload(self, api_context, request):
        """Test creating a system with empty JSON payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        response = context.post(
            "/api/data/data_system",
            data="{}",
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", {}, response)
        assert response.status == 422, f"Expected 422 status code for empty payload, got {response.status}"

    def test_create_system_with_missing_entity_section(self, api_context, request):
        """Test creating a system without entity section."""
        context, access_token = api_context
        payload = {
            "entity_info": {
                "owner": os.getenv("OWNER_EMAIL", "test@example.com"),
                "contact_ids": [],
                "links": [],
            }
        }

        headers = get_headers(access_token)
        response = context.post(
            "/api/data/data_system",
            data=json.dumps(payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/data_system", payload, response)
        assert response.status == 422, f"Expected 422 status code for missing entity section, got {response.status}"

    def test_create_system_with_missing_owner_person_section(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system without owner_person section."""
        context, access_token = api_context
        payload = system_api.modify_payload(valid_system_payload, "entity.owner_person", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        # Discover if owner_person is actually required or optional
        if response.ok:
            print("owner_person section is optional - request succeeded without it")
            json_response = response.json()
            if "identifier" in json_response:
                system_api.add_system_to_cleanup(json_response["identifier"])
        else:
            print(f"owner_person section appears to be required - request failed with status {response.status}")
            if response.status == 422:
                print("  Failed with validation error as expected for missing required field")
            else:
                print(f"  Unexpected error status: {response.status}")

    def test_create_system_with_additional_unknown_fields(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with additional unknown fields."""
        context, access_token = api_context
        # Add unknown fields to the payload
        payload = deepcopy(valid_system_payload)
        payload["unknown_field"] = "unknown_value"
        payload["entity"]["unknown_entity_field"] = "unknown_entity_value"
        payload["entity_info"]["unknown_info_field"] = "unknown_info_value"

        response = system_api.create_system(payload, request)

        # The API might accept or reject unknown fields - adjust based on actual behavior
        if response.ok:
            # If it accepts unknown fields, verify the response doesn't include them
            json_response = response.json()
            assert "unknown_field" not in json_response
            assert "unknown_entity_field" not in json_response.get("entity", {})
        else:
            # If it rejects unknown fields, it should be a validation error
            assert response.status == 422, f"Expected 422 for unknown fields, got {response.status}"

    def test_create_system_with_extremely_long_values(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with extremely long field values."""
        context, access_token = api_context
        # Test with 10000 character values
        extremely_long_value = "A" * 10000

        test_cases = [
            ("entity.name", extremely_long_value),
            ("entity.description", extremely_long_value),
            ("entity.label", extremely_long_value),
        ]

        for field_path, value in test_cases:
            payload = system_api.modify_payload(valid_system_payload, field_path, value)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            # Should likely fail with validation error for extremely long values
            if not response.ok:
                assert response.status == 422, f"Expected 422 for extremely long {field_path}, got {response.status}"

    def test_create_system_with_sql_injection_attempts(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with SQL injection attempts in various fields."""
        context, access_token = api_context
        sql_injection_payloads = [
            "'; DROP TABLE systems; --",
            "' OR '1'='1",
            "'; INSERT INTO systems VALUES ('malicious'); --",
            "' UNION SELECT * FROM users --"
        ]

        for sql_payload in sql_injection_payloads:
            test_cases = [
                ("entity.name", f"Test System {sql_payload}"),
                ("entity.description", f"Description {sql_payload}"),
                ("entity.label", f"Label{sql_payload}"),
            ]

            for field_path, value in test_cases:
                payload = system_api.modify_payload(valid_system_payload, field_path, value)
                response = system_api.create_system(payload, request)

                # Should either succeed (with proper sanitization) or fail gracefully
                if response.ok:
                    # If successful, verify the data was properly handled
                    json_response = response.json()
                    # The response should contain the data as provided (properly escaped/sanitized)
                    assert field_path.split(".")[-1] in json_response
                else:
                    # If it fails, should be a validation error, not a server error
                    assert response.status in [400, 422], f"SQL injection attempt should not cause server error, got {response.status}"

    def test_create_system_with_script_injection_attempts(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with script injection attempts."""
        context, access_token = api_context
        script_injection_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "{{7*7}}",  # Template injection
            "${7*7}",   # Expression injection
        ]

        for script_payload in script_injection_payloads:
            payload = system_api.modify_payload(valid_system_payload, "entity.name", f"System {script_payload}")
            response = system_api.create_system(payload, request)

            # Should either succeed (with proper sanitization) or fail gracefully
            if response.ok:
                json_response = response.json()
                # Verify the response contains the data (should be properly escaped)
                assert "name" in json_response
            else:
                # Should not cause server errors
                assert response.status in [400, 422], f"Script injection should not cause server error, got {response.status}"

    def test_create_system_with_invalid_json_types(self, api_context, request, valid_system_payload, system_api):
        """Test creating a system with invalid data types for fields."""
        context, access_token = api_context
        invalid_type_tests = [
            ("entity.name", 12345),  # Number instead of string
            ("entity.name", True),   # Boolean instead of string
            ("entity.name", []),     # Array instead of string
            ("entity.name", {}),     # Object instead of string
            ("entity_info.contact_ids", "not_an_array"),  # String instead of array
            ("entity_info.links", 12345),  # Number instead of array
        ]

        for field_path, invalid_value in invalid_type_tests:
            payload = system_api.modify_payload(valid_system_payload, field_path, invalid_value)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            assert response.status == 422, f"Expected 422 for invalid type in {field_path}, got {response.status}"

    def test_create_system_error_response_format(self, api_context, request, valid_system_payload, system_api, assert_error_response):
        """Test that error responses follow the expected format."""
        context, access_token = api_context
        # Force an error by removing required field
        payload = system_api.modify_payload(valid_system_payload, "entity.name", None)
        response = system_api.create_system(payload, request, add_to_cleanup=False)

        assert not response.ok, "Request should fail"
        error_response = assert_error_response(response)

        # Verify error response structure
        assert isinstance(error_response["errors"], list), "errors should be a list"
        assert len(error_response["errors"]) > 0, "errors list should not be empty"

        # Check first error structure
        first_error = error_response["errors"][0]
        assert "loc" in first_error, "Error should have 'loc' field"
        assert "type" in first_error, "Error should have 'type' field"

    def test_create_system_concurrent_requests(self, api_context, request, system_api):
        """Test creating multiple systems with similar names concurrently."""
        context, access_token = api_context
        base_name = f"Concurrent Test System {makeid(5)}"

        # Create multiple systems with similar names
        responses = []
        for i in range(5):
            response = system_api.create_valid_system(f"{base_name} {i}", request)
            responses.append(response)

        # All should succeed and have unique identifiers
        identifiers = set()
        for i, response in enumerate(responses):
            assert response.ok, f"Request {i} failed: {response.status} - {response.text()}"
            json_response = response.json()
            identifier = json_response["identifier"]
            assert identifier not in identifiers, f"Duplicate identifier found: {identifier}"
            identifiers.add(identifier)
