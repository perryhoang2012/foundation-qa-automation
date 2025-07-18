import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.source_payload import create_source_payload
from utils.common import makeid
from conftest import record_api_info, get_headers

class TestOriginAPI:
    """Test suite for POST /api/data/origin endpoint"""

    def test_create_origin_with_valid_payload(self, api_context, request, origin_ids, origin_api):
        """Test creating an origin with a valid payload."""
        context, access_token = api_context

        response = origin_api.create_valid_origin("Valid Origin", request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"
        json_response = response.json()
        assert "entity" in json_response, "Response missing 'entity' section"
        assert "identifier" in json_response["entity"], "Response missing 'entity.identifier' field"
        assert json_response["entity"]["name"].startswith("Valid Origin"), "Name in response doesn't match payload"

        # Discover the entity_type field location and expected value
        if "entity_type" in json_response:
            assert json_response["entity_type"] == "origin", "Entity type should be 'origin'"
        elif "entity_type" in json_response.get("entity", {}):
            # Note: entity_type is not returned in the response, it's only used for creation
            print("entity_type field not returned in response - this is expected behavior")

    def test_create_origin_without_name(self, api_context, request, valid_origin_payload, origin_api, assert_status):
        """Test creating an origin without providing a name."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity.name", None)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if name is required
        if response.ok:
            print("Name field is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Name field appears to be required - request failed with status {response.status}")
            if response.status == 422:
                error_response = response.json()
                assert "errors" in error_response, "Error response should contain 'errors' field"

    def test_create_origin_with_empty_name(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with an empty name string."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity.name", "")
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if empty name is allowed
        if response.ok:
            print("Empty name is allowed - request succeeded")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Empty name was rejected with status {response.status}")

    def test_create_origin_without_entity_type(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin without entity_type field."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity.entity_type", None)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if entity_type is required
        if response.ok:
            print("entity_type field is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"entity_type field appears to be required - request failed with status {response.status}")

    def test_create_origin_with_invalid_entity_type(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with invalid entity_type."""
        context, access_token = api_context

        invalid_types = ["source", "invalid_type", "ORIGIN", "Origin", "system", "mesh"]

        for invalid_type in invalid_types:
            payload = origin_api.modify_payload(valid_origin_payload, "entity.entity_type", invalid_type)
            response = origin_api.create_origin(payload, request, add_to_cleanup=False)

            if response.ok:
                print(f"Entity type '{invalid_type}' was accepted")
                json_response = response.json()
                if "entity" in json_response and "identifier" in json_response["entity"]:
                    origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
            else:
                print(f"Entity type '{invalid_type}' was rejected with status {response.status}")

    def test_create_origin_without_label(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin without label field."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity.label", None)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if label is required
        if response.ok:
            print("Label field is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Label field appears to be required - request failed with status {response.status}")

    def test_create_origin_without_description(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin without description field."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity.description", None)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if description is required
        if response.ok:
            print("Description field is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Description field appears to be required - request failed with status {response.status}")

    def test_create_origin_without_entity_info_section(self, api_context, request, origin_api):
        """Test creating an origin without entity_info section."""
        context, access_token = api_context

        payload = {
            "entity": {
                "name": f"Test Origin {makeid()}",
                "entity_type": "origin",
                "label": "SCD",
                "description": "Test description",
            }
        }

        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if entity_info is required
        if response.ok:
            print("entity_info section is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"entity_info section appears to be required - request failed with status {response.status}")

    def test_create_origin_without_owner(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin without entity_info.owner field."""
        context, access_token = api_context

        payload = origin_api.modify_payload(valid_origin_payload, "entity_info.owner", None)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        # Discover if owner is required
        if response.ok:
            print("Owner field is optional - request succeeded without it")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Owner field appears to be required - request failed with status {response.status}")

    def test_create_origin_with_invalid_email_format(self, api_context, request, valid_origin_payload, origin_api):
        """Test creating an origin with invalid email format in owner field."""
        context, access_token = api_context

        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            "user name@domain.com",
            "",
        ]

        for invalid_email in invalid_emails:
            payload = origin_api.modify_payload(valid_origin_payload, "entity_info.owner", invalid_email)
            response = origin_api.create_origin(payload, request, add_to_cleanup=False)

            if response.ok:
                print(f"Invalid email '{invalid_email}' was accepted")
                json_response = response.json()
                if "entity" in json_response and "identifier" in json_response["entity"]:
                    origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
            else:
                print(f"Invalid email '{invalid_email}' was rejected with status {response.status}")

    def test_create_origin_with_special_characters_in_name(self, api_context, request, origin_api):
        """Test creating an origin with special characters in name."""
        context, access_token = api_context

        # Test valid special characters
        valid_special_names = [
            "Origin with spaces",
            "Origin-with-hyphens",
            "Origin_with_underscores",
            "Origin_123_numbers"
        ]

        for special_name in valid_special_names:
            # Create unique payload for each test
            unique_payload = create_source_payload(f"{special_name} {makeid(3)}")
            payload = origin_api.modify_payload(unique_payload, "entity.name", f"{special_name} {makeid(3)}")
            response = origin_api.create_origin(payload, request)

            if response.ok:
                json_response = response.json()
                expected_name = f"{special_name} {makeid(3)}"  # This won't match exactly due to dynamic ID
                # Just verify the special characters part is present
                assert special_name.replace(" ", "").replace("-", "").replace("_", "").replace("123", "") in json_response["entity"]["name"].replace(" ", "").replace("-", "").replace("_", "").replace("123", "")
                print(f"✅ Valid special name pattern '{special_name}' was accepted")
            else:
                print(f"❌ Valid special name '{special_name}' was rejected with status {response.status}")

        # Test potentially invalid special characters
        potentially_invalid_names = [
            f"Origin.with.dots.{makeid(3)}",
            f"Origin (with parentheses) {makeid(3)}",
            f"Origin@with@at {makeid(3)}",
            f"123StartWithNumber {makeid(3)}",
            f"Origin#with#hash {makeid(3)}"
        ]

        for invalid_name in potentially_invalid_names:
            unique_payload = create_source_payload(f"Special Test {makeid(3)}")
            payload = origin_api.modify_payload(unique_payload, "entity.name", invalid_name)
            response = origin_api.create_origin(payload, request, add_to_cleanup=False)

            if response.ok:
                print(f"Special name '{invalid_name}' was accepted")
                json_response = response.json()
                if "entity" in json_response and "identifier" in json_response["entity"]:
                    origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
            else:
                print(f"Special name '{invalid_name}' was rejected with status {response.status}")

    def test_create_origin_with_long_values(self, api_context, request, origin_api):
        """Test creating an origin with very long field values."""
        context, access_token = api_context

        # Test with long name
        long_name = "A" * 500
        unique_payload1 = create_source_payload(f"Long Name Test {makeid(3)}")
        payload = origin_api.modify_payload(unique_payload1, "entity.name", long_name)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        if response.ok:
            print(f"Long name (500 chars) was accepted")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Long name (500 chars) was rejected with status {response.status}")

        # Test with long description
        long_description = "This is a very long description. " * 30  # ~990 chars
        unique_payload2 = create_source_payload(f"Long Desc Test {makeid(3)}")
        payload = origin_api.modify_payload(unique_payload2, "entity.description", long_description)
        response = origin_api.create_origin(payload, request, add_to_cleanup=False)

        if response.ok:
            print(f"Long description (~990 chars) was accepted")
            json_response = response.json()
            if "entity" in json_response and "identifier" in json_response["entity"]:
                origin_api.add_origin_to_cleanup(json_response["entity"]["identifier"])
        else:
            print(f"Long description (~990 chars) was rejected with status {response.status}")

    def test_create_origin_with_minimal_payload(self, api_context, request, origin_api):
        """Test creating an origin with minimal required fields only."""
        context, access_token = api_context

        minimal_payload = {
            "entity": {
                "name": f"Minimal Origin {makeid()}",
                "entity_type": "origin",
                "label": "SCD",
                "description": "Minimal description",
            },
            "entity_info": {
                "owner": os.getenv("OWNER_EMAIL", "test@example.com"),
                "contact_ids": [],
                "links": [],
            },
        }

        response = origin_api.create_origin(minimal_payload, request)

        assert response.ok, f"Request failed for minimal payload: {response.status} - {response.text()}"
        json_response = response.json()
        assert "entity" in json_response
        assert "identifier" in json_response["entity"]

    def test_create_origin_with_empty_arrays(self, api_context, request, origin_api):
        """Test creating an origin with empty contact_ids and links arrays."""
        context, access_token = api_context

        # Create a unique payload to avoid name conflicts
        unique_payload = create_source_payload(f"Empty Arrays Test {makeid(5)}")

        # Test empty contact_ids
        payload = origin_api.modify_payload(unique_payload, "entity_info.contact_ids", [])
        response = origin_api.create_origin(payload, request)
        assert response.ok, f"Request failed with empty contact_ids: {response.status} - {response.text()}"

        # Test empty links with a different payload
        unique_payload2 = create_source_payload(f"Empty Links Test {makeid(5)}")
        payload = origin_api.modify_payload(unique_payload2, "entity_info.links", [])
        response = origin_api.create_origin(payload, request)
        assert response.ok, f"Request failed with empty links: {response.status} - {response.text()}"

    def test_create_origin_response_structure(self, api_context, request, origin_api):
        """Test that the response structure matches expected format."""
        context, access_token = api_context

        response = origin_api.create_valid_origin("Response Structure Test", request)

        assert response.ok, f"Request failed: {response.status} - {response.text()}"
        json_response = response.json()

        # Validate response structure
        required_top_fields = ["entity", "entity_info"]
        for field in required_top_fields:
            assert field in json_response, f"Response missing required top-level field: {field}"

        # Validate entity section structure
        entity = json_response["entity"]
        required_entity_fields = ["identifier", "name", "description", "label", "created_at"]
        for field in required_entity_fields:
            assert field in entity, f"Response missing required entity field: {field}"

        # Validate data types
        assert isinstance(entity["identifier"], str), "identifier should be a string"
        assert isinstance(entity["name"], str), "name should be a string"
        assert isinstance(entity["description"], str), "description should be a string"
        assert isinstance(entity["label"], str), "label should be a string"

        # Note: entity_type is not returned in the response, it's only used for creation

    def test_create_origin_with_unicode_characters(self, api_context, request, origin_api):
        """Test creating an origin with various Unicode characters."""
        context, access_token = api_context

        unicode_test_cases = [
            "Origin with émojis 🚀🔥💻",
            "Origine avec caractères français àáâãäåæç",
            "起源名称中文测试",
            "Происхождение с русскими символами",
            "أصل اختبار باللغة العربية",
            "מקור בעברית"
        ]

        for unicode_name in unicode_test_cases:
            # Create unique payload for each unicode test
            unique_payload = create_source_payload(f"Unicode Test {makeid(3)}")
            payload = origin_api.modify_payload(unique_payload, "entity.name", f"{unicode_name} {makeid(2)}")
            response = origin_api.create_origin(payload, request)

            if response.ok:
                json_response = response.json()
                # Verify the unicode characters are present (allowing for the random ID addition)
                response_name = json_response["entity"]["name"]
                # Check if the main part of the unicode name is in the response
                assert unicode_name in response_name or response_name.startswith(unicode_name), f"Unicode content not preserved: expected '{unicode_name}' in '{response_name}'"
                print(f"✅ Unicode name '{unicode_name}' was accepted")
            else:
                print(f"❌ Unicode name '{unicode_name}' was rejected with status {response.status}")

    def test_create_duplicate_origin_names(self, api_context, request, origin_api):
        """Test creating origins with duplicate names to see if API prevents duplicates."""
        context, access_token = api_context

        # Create first origin with a unique base name
        unique_base_name = f"Duplicate Test Origin {makeid(10)}"
        payload1 = create_source_payload(unique_base_name)
        response1 = origin_api.create_origin(payload1, request)
        assert response1.ok, f"First origin creation failed: {response1.status} - {response1.text()}"

        # Try to create second origin with the exact same name (same payload)
        payload2 = create_source_payload(unique_base_name)
        response2 = origin_api.create_origin(payload2, request, add_to_cleanup=False)

        if response2.ok:
            print("Duplicate names are allowed - both origins were created successfully")
            json_response1 = response1.json()
            json_response2 = response2.json()
            identifier1 = json_response1["entity"]["identifier"]
            identifier2 = json_response2["entity"]["identifier"]
            assert identifier1 != identifier2, "Duplicate origins should have different identifiers"

            # Add second origin to cleanup if it was created
            origin_api.add_origin_to_cleanup(identifier2)
        else:
            print(f"Duplicate names are not allowed - second creation failed with status {response2.status}")
            if response2.status == 409:
                print("API correctly prevents duplicate names with 409 Conflict")
            # Log the error details
            try:
                error_data = response2.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response2.text()}")

    def test_cleanup_mechanism_verification(self, api_context, request, origin_api, cleanup_created_origins):
        """Test to verify that the cleanup mechanism works correctly."""
        context, access_token = api_context

        # Create an origin specifically for testing cleanup
        response = origin_api.create_valid_origin("Cleanup Test Origin", request)

        assert response.ok, f"Failed to create test origin: {response.status} - {response.text()}"
        json_response = response.json()
        origin_id = json_response["entity"]["identifier"]

        # Verify the origin was created
        assert "entity" in json_response
        assert "identifier" in json_response["entity"]
        assert json_response["entity"]["name"].startswith("Cleanup Test Origin")

        # The origin should be automatically added to cleanup
        assert origin_id in origin_api.origin_ids, "Origin ID should be automatically tracked for cleanup"

        # Also add to function cleanup for immediate verification
        cleanup_created_origins(origin_id)

        print(f"✅ Created origin {origin_id} for cleanup testing - it will be automatically cleaned up")
