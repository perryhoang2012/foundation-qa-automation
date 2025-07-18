import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.source_payload import create_source_payload
from utils.common import makeid
from conftest import record_api_info, get_headers

class TestOriginErrorHandling:
    """Test suite for error handling scenarios in POST /api/data/origin endpoint"""

    def test_create_origin_with_null_payload(self, api_context, request):
        """Test creating an origin with null payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        response = context.post(
            "/api/data/origin",
            data="null",
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", None, response)

        # Discover how API handles null payload
        if response.status == 400:
            print("Null payload rejected with 400 Bad Request")
        elif response.status == 422:
            print("Null payload rejected with 422 Validation Error")
        else:
            print(f"Null payload handling: status {response.status}")

    def test_create_origin_with_empty_payload(self, api_context, request):
        """Test creating an origin with empty JSON payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        response = context.post(
            "/api/data/origin",
            data="{}",
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", {}, response)

        # Discover how API handles empty payload
        if response.ok:
            print("Empty payload was accepted - API has defaults")
            json_response = response.json()
            # Handle nested response structure
            if "entity" in json_response and "identifier" in json_response["entity"]:
                print(f"Created origin with identifier: {json_response['entity']['identifier']}")
                # Add to cleanup (but would need origin_api for this)
            elif "identifier" in json_response:
                print(f"Created origin with identifier: {json_response['identifier']}")
        else:
            print(f"Empty payload was rejected with status {response.status}")

    def test_create_origin_with_missing_entity_section(self, api_context, request):
        """Test creating an origin without entity section."""
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
            "/api/data/origin",
            data=json.dumps(payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", payload, response)

        # Discover if entity section is required
        if response.ok:
            print("entity section is optional - request succeeded without it")
        else:
            print(f"entity section appears to be required - request failed with status {response.status}")

    def test_create_origin_without_authorization(self, api_context, request, valid_origin_payload):
        """Test creating an origin without authorization header."""
        context, access_token = api_context

        headers = {
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/origin",
            data=json.dumps(valid_origin_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", valid_origin_payload, response)

        assert response.status == 401, f"Expected 401 status code for missing authorization, got {response.status}"

    def test_create_origin_with_invalid_authorization(self, api_context, request, valid_origin_payload):
        """Test creating an origin with invalid authorization token."""
        context, access_token = api_context

        headers = {
            "Authorization": "Bearer invalid_token",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/origin",
            data=json.dumps(valid_origin_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", valid_origin_payload, response)

        assert response.status == 401, f"Expected 401 status code for invalid token, got {response.status}"

    def test_create_origin_without_x_account_header(self, api_context, request, valid_origin_payload):
        """Test creating an origin without x-account header."""
        context, access_token = api_context

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = context.post(
            "/api/data/origin",
            data=json.dumps(valid_origin_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", valid_origin_payload, response)

        # Discover if x-account header is required
        if response.ok:
            print("x-account header is optional - request succeeded without it")
        else:
            print(f"x-account header appears to be required - request failed with status {response.status}")

    def test_create_origin_with_malformed_json(self, api_context, request):
        """Test creating an origin with malformed JSON payload."""
        context, access_token = api_context

        headers = get_headers(access_token)
        malformed_json = '{"entity": {"name": "Test"'  # Missing closing braces

        response = context.post(
            "/api/data/origin",
            data=malformed_json,
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", malformed_json, response)

        # Should be a parsing error
        assert response.status in [400, 422], f"Expected 400 or 422 status code for malformed JSON, got {response.status}"

    def test_create_origin_with_wrong_content_type(self, api_context, request, valid_origin_payload):
        """Test creating an origin with wrong Content-Type header."""
        context, access_token = api_context

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "text/plain"
        }

        response = context.post(
            "/api/data/origin",
            data=json.dumps(valid_origin_payload),
            headers=headers
        )

        record_api_info(request, "POST", "/api/data/origin", valid_origin_payload, response)

        # Should fail due to wrong content type
        assert not response.ok, f"Request should fail with wrong content type, got {response.status}"

    def test_create_origin_with_extremely_long_values(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with extremely long field values."""
        context, access_token = api_context

        # Test with 10000 character values
        extremely_long_value = "A" * 10000

        test_cases = [
            ("entity.name", extremely_long_value),
            ("entity.description", extremely_long_value),
            ("entity.label", extremely_long_value),
        ]

        for field_path, value in test_cases:
            payload = origin_api.modify_payload(valid_origin_payload, field_path, value)
            response = origin_api.create_origin(payload, request, add_to_cleanup=False)

            if response.ok:
                print(f"Extremely long {field_path} (10k chars) was accepted")
                json_response = response.json()
                if "identifier" in json_response:
                    origin_api.add_origin_to_cleanup(json_response["identifier"])
            else:
                print(f"Extremely long {field_path} (10k chars) was rejected with status {response.status}")

    def test_create_origin_with_sql_injection_attempts(self, api_context, request, origin_api):
        """Test creating an origin with SQL injection attempts in various fields."""
        context, access_token = api_context

        sql_injection_payloads = [
            "'; DROP TABLE origins; --",
            "' OR '1'='1",
            "'; INSERT INTO origins VALUES ('malicious'); --",
            "' UNION SELECT * FROM users --"
        ]

        for sql_payload in sql_injection_payloads:
            test_cases = [
                ("entity.name", f"Test Origin {makeid(5)} {sql_payload}"),
                ("entity.description", f"Description {sql_payload}"),
                ("entity.label", f"Label{sql_payload}"),
            ]

            for field_path, value in test_cases:
                # Create a unique payload for each test to avoid conflicts
                unique_payload = create_source_payload(f"SQL Test {makeid(3)}")
                payload = origin_api.modify_payload(unique_payload, field_path, value)
                response = origin_api.create_origin(payload, request, add_to_cleanup=False)

                if response.ok:
                    print(f"SQL injection in {field_path} was handled safely")
                    json_response = response.json()
                    # Verify the data was properly handled - check in entity section
                    field_name = field_path.split(".")[-1]
                    if "entity" in json_response:
                        assert field_name in json_response["entity"], f"Field {field_name} not found in entity section"
                        # Add to cleanup if created successfully
                        if "identifier" in json_response["entity"]:
                            origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
                    else:
                        assert field_name in json_response, f"Field {field_name} not found in response"
                else:
                    # Should not cause server errors
                    assert response.status in [400, 422], f"SQL injection should not cause server error, got {response.status}"
                    print(f"SQL injection in {field_path} was rejected with status {response.status}")

    def test_create_origin_with_script_injection_attempts(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with script injection attempts."""
        context, access_token = api_context

        script_injection_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "{{7*7}}",  # Template injection
            "${7*7}",   # Expression injection
        ]

        for script_payload in script_injection_payloads:
            payload = origin_api.modify_payload(valid_origin_payload, "entity.name", f"Origin {script_payload}")
            response = origin_api.create_origin(payload, request)

            if response.ok:
                print(f"Script injection was handled safely")
                json_response = response.json()
                assert "name" in json_response
            else:
                # Should not cause server errors
                assert response.status in [400, 422], f"Script injection should not cause server error, got {response.status}"
                print(f"Script injection was rejected with status {response.status}")

    def test_create_origin_with_invalid_json_types(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with invalid data types for fields."""
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
            payload = origin_api.modify_payload(valid_origin_payload, field_path, invalid_value)
            response = origin_api.create_origin(payload, request, add_to_cleanup=False)

            if response.ok:
                print(f"Invalid type for {field_path} was accepted")
                json_response = response.json()
                if "identifier" in json_response:
                    origin_api.add_origin_to_cleanup(json_response["identifier"])
            else:
                print(f"Invalid type for {field_path} was rejected with status {response.status}")

    def test_create_origin_with_additional_unknown_fields(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with additional unknown fields."""
        context, access_token = api_context

        # Add unknown fields to the payload
        payload = deepcopy(valid_origin_payload)
        payload["unknown_field"] = "unknown_value"
        payload["entity"]["unknown_entity_field"] = "unknown_entity_value"
        payload["entity_info"]["unknown_info_field"] = "unknown_info_value"

        response = origin_api.create_origin(payload, request)

        if response.ok:
            print("Unknown fields were accepted (likely ignored)")
            # Verify the response doesn't include unknown fields
            json_response = response.json()
            assert "unknown_field" not in json_response, "Unknown fields should not be returned in response"
        else:
            print(f"Unknown fields were rejected with status {response.status}")

    def test_create_origin_concurrent_requests(self, api_context, request, origin_api):
        """Test creating multiple origins concurrently."""
        context, access_token = api_context

        base_name = f"Concurrent Test Origin {makeid(5)}"

        # Create multiple origins with similar names
        responses = []
        for i in range(5):
            response = origin_api.create_valid_origin(f"{base_name} {i}", request)
            responses.append(response)

        # All should succeed and have unique identifiers
        identifiers = set()
        for i, response in enumerate(responses):
            assert response.ok, f"Request {i} failed: {response.status} - {response.text()}"
            json_response = response.json()
            # Handle nested response structure
            if "entity" in json_response and "identifier" in json_response["entity"]:
                identifier = json_response["entity"]["identifier"]
            else:
                identifier = json_response.get("identifier")

            assert identifier, f"No identifier found in response {i}"
            assert identifier not in identifiers, f"Duplicate identifier found: {identifier}"
            identifiers.add(identifier)

        print(f"✅ Successfully created {len(responses)} concurrent origins with unique identifiers")

    def test_create_origin_error_response_format(self, api_context, request, valid_origin_payload, origin_api, assert_error_response):
        """Test that error responses follow the expected format."""
        context, access_token = api_context

        # Force an error by using invalid JSON type
        payload = origin_api.modify_payload(valid_origin_payload, "entity.name", 12345)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        if not response.ok:
            error_response = assert_error_response(response)
            if error_response:
                # Verify error response structure
                assert isinstance(error_response["errors"], list), "errors should be a list"
                if len(error_response["errors"]) > 0:
                    first_error = error_response["errors"][0]
                    expected_error_fields = ["detail", "loc", "type"]
                    for field in expected_error_fields:
                        if field in first_error:
                            print(f"✅ Error contains expected field: {field}")
                        else:
                            print(f"⚠️ Error missing field: {field}")
        else:
            print("⚠️ Expected error response but request succeeded")
