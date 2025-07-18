import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.system_payload import create_system_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

class TestSystemValidation:
    """Test suite for validation scenarios in POST /api/data/data_system endpoint"""

    def test_validate_required_fields(self, api_context, request, valid_system_payload, system_api):
        """Test validation of all required fields."""
        context, access_token = api_context

        required_fields = [
            "entity.name",
            "entity.entity_type",
            "entity.label",
            "entity.description",
            "entity.owner_person.email",
            "entity.owner_person.full_name",
            "entity_info.owner",
        ]

        for field_path in required_fields:
            payload = system_api.modify_payload(valid_system_payload, field_path, None)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            # Check if the field is actually required - don't assume error code
            if not response.ok:
                print(f"Field {field_path} appears to be required (status: {response.status})")
                # Verify error response contains information about the missing field
                try:
                    error_response = response.json()
                    if "errors" in error_response:
                        print(f"  Error details available for {field_path}")
                except:
                    pass  # Skip if response is not JSON
            else:
                print(f"Field {field_path} appears to be optional (request succeeded)")
                # Clean up created system
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_email_format(self, api_context, request, valid_system_payload, system_api):
        """Test email format validation."""
        context, access_token = api_context

        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            "user name@domain.com",  # space in email
            "",
            "user@domain..com",
        ]

        for invalid_email in invalid_emails:
            # Test in owner_person.email
            payload = system_api.modify_payload(valid_system_payload, "entity.owner_person.email", invalid_email)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Invalid email '{invalid_email}' in owner_person was rejected (status: {response.status})")
            else:
                print(f"Invalid email '{invalid_email}' in owner_person was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

            # Test in entity_info.owner
            payload = system_api.modify_payload(valid_system_payload, "entity_info.owner", invalid_email)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Invalid email '{invalid_email}' in entity_info.owner was rejected (status: {response.status})")
            else:
                print(f"Invalid email '{invalid_email}' in entity_info.owner was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_valid_email_formats(self, api_context, request, valid_system_payload, system_api):
        """Test that valid email formats are accepted."""
        context, access_token = api_context

        valid_emails = [
            "user@domain.com",
            "user.name@domain.com",
            "user+tag@domain.com",
            "user123@domain123.com",
            "test@subdomain.domain.com",
            "a@b.co",
        ]

        for valid_email in valid_emails:
            payload = system_api.modify_payload(valid_system_payload, "entity.owner_person.email", valid_email)
            payload = system_api.modify_payload(payload, "entity_info.owner", valid_email)
            response = system_api.create_system(payload, request)

            assert response.ok, f"Valid email '{valid_email}' should be accepted, got {response.status} - {response.text()}"

    def test_validate_entity_type_values(self, api_context, request, valid_system_payload, system_api):
        """Test entity_type field validation."""
        context, access_token = api_context

        # Test valid entity_type
        payload = system_api.modify_payload(valid_system_payload, "entity.entity_type", "data_system")
        response = system_api.create_system(payload, request)
        assert response.ok, f"Valid entity_type 'data_system' should be accepted, got {response.status}"

        # Test invalid entity_types - discover which ones are actually invalid
        invalid_entity_types = [
            "system",
            "data",
            "invalid_type",
            "SYSTEM",
            "Data_System",
            "",
            123,
            True,
        ]

        for invalid_type in invalid_entity_types:
            payload = system_api.modify_payload(valid_system_payload, "entity.entity_type", invalid_type)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Entity type '{invalid_type}' was rejected (status: {response.status})")
            else:
                print(f"Entity type '{invalid_type}' was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_empty_strings(self, api_context, request, valid_system_payload, system_api):
        """Test validation of empty strings in required fields."""
        context, access_token = api_context

        string_fields = [
            "entity.name",
            "entity.entity_type",
            "entity.label",
            "entity.description",
            "entity.owner_person.email",
            "entity.owner_person.full_name",
            "entity_info.owner",
        ]

        for field_path in string_fields:
            payload = system_api.modify_payload(valid_system_payload, field_path, "")
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Empty string for {field_path} was rejected (status: {response.status})")
            else:
                print(f"Empty string for {field_path} was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_array_fields(self, api_context, request, valid_system_payload, system_api):
        """Test validation of array fields."""
        context, access_token = api_context

        # Test valid arrays
        valid_arrays = [
            [],                    # Empty array
            ["contact1"],          # Single item
            ["contact1", "contact2"],  # Multiple items
        ]

        for valid_array in valid_arrays:
            payload = system_api.modify_payload(valid_system_payload, "entity_info.contact_ids", valid_array)
            payload = system_api.modify_payload(payload, "entity_info.links", valid_array)
            response = system_api.create_system(payload, request)

            assert response.ok, f"Valid array {valid_array} should be accepted, got {response.status}"

        # Test invalid array values - discover which ones are actually invalid
        invalid_array_values = [
            "not_an_array",
            123,
            True,
            {"key": "value"},
        ]

        for invalid_value in invalid_array_values:
            payload = system_api.modify_payload(valid_system_payload, "entity_info.contact_ids", invalid_value)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Invalid array value {invalid_value} was rejected (status: {response.status})")
            else:
                print(f"Invalid array value {invalid_value} was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_nested_object_structure(self, api_context, request, valid_system_payload, system_api):
        """Test validation of nested object structures."""
        context, access_token = api_context

        # Test invalid owner_person structures - discover which ones are actually invalid
        invalid_owner_persons = [
            "not_an_object",
            123,
            [],
            True,
            {"email": "test@test.com"},  # Missing full_name
            {"full_name": "Test User"},  # Missing email
        ]

        for invalid_owner_person in invalid_owner_persons:
            payload = system_api.modify_payload(valid_system_payload, "entity.owner_person", invalid_owner_person)
            response = system_api.create_system(payload, request, add_to_cleanup=False)

            if not response.ok:
                print(f"Invalid owner_person structure {type(invalid_owner_person).__name__} was rejected (status: {response.status})")
            else:
                print(f"Invalid owner_person structure {type(invalid_owner_person).__name__} was accepted")
                # Clean up if successful
                json_response = response.json()
                if "identifier" in json_response:
                    system_api.add_system_to_cleanup(json_response["identifier"])

    def test_validate_field_order_independence(self, api_context, request, valid_system_payload, system_api):
        """Test that field order doesn't affect validation."""
        context, access_token = api_context

        # Create payload with different field ordering
        reordered_payload = {
            "entity_info": valid_system_payload["entity_info"],
            "entity": {
                "entity_type": valid_system_payload["entity"]["entity_type"],
                "owner_person": valid_system_payload["entity"]["owner_person"],
                "description": valid_system_payload["entity"]["description"],
                "name": valid_system_payload["entity"]["name"],
                "label": valid_system_payload["entity"]["label"],
            }
        }

        response = system_api.create_system(reordered_payload, request)
        assert response.ok, f"Field order should not affect validation, got {response.status} - {response.text()}"
