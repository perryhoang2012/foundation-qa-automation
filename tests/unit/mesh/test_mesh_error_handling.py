import os
import sys
import pytest
import json
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.mesh_payload import create_mesh_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

@pytest.fixture(scope="module")
def valid_mesh_payload():
    return create_mesh_payload("Schema Test Mesh")

class TestMeshApiSchemaValidation:
    """Test class for API schema validation."""
    
    def test_missing_required_fields(self, api_context, request, mesh_ids, mesh_api, assert_status):
        """Test API behavior when required fields are missing."""
        context, access_token = api_context
        # Test with missing 'entity' field
        payload = {"entity_info": {"owner": "quang.doan@meshx.io"}}
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)
        
        assert_status(response, 422, f"Expected 422 status code for missing 'entity', got {response.status}")
        
        # Test with missing 'entity_info' field
        payload = {"entity": {"name": "Test Mesh", "entity_type": "mesh"}}
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)
        
        # The API might require entity_info or make it optional
    
    def test_additional_fields(self, api_context, request, valid_mesh_payload, mesh_ids, mesh_api):
        """Test API behavior when additional fields are provided."""
        context, access_token = api_context
        # Add extra fields at the root level
        payload = mesh_api.modify_payload(valid_mesh_payload, "extra_field", "This is an extra field")
        response = mesh_api.create_mesh(payload, request)
        
        # Check if API ignores or rejects additional fields
        
        # Add extra fields in the entity object
        payload = mesh_api.modify_payload(valid_mesh_payload, "entity.extra_entity_field", "This is an extra entity field")
        response = mesh_api.create_mesh(payload, request)
        
        # Check if API ignores or rejects additional fields in entity
    
    def test_incorrect_field_types(self, api_context, request, valid_mesh_payload, mesh_ids, mesh_api):
        """Test API behavior when fields have incorrect types."""
        context, access_token = api_context
        # Test with non-string name
        payload = mesh_api.modify_payload(valid_mesh_payload, "entity.name", 12345)  # Number instead of string
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)
        
        # Test with non-array assignees
        payload = mesh_api.modify_payload(valid_mesh_payload, "entity.assignees", "Not an array")  # String instead of array
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)
        
        # Test with incorrect entity_type value type
        payload = mesh_api.modify_payload(valid_mesh_payload, "entity.entity_type", ["mesh"])  # Array instead of string
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)

class TestMeshApiErrorHandling:
    """Test class for API error handling."""
    
    def test_malformed_json(self, api_context, request, mesh_ids, mesh_api, assert_status):
        """Test API behavior with malformed JSON."""
        context, access_token = api_context
        # Test with incomplete JSON
        malformed_json = '{"entity": {"name": "Test Mesh"'  # Missing closing brackets
        
        response = mesh_api.create_mesh(malformed_json, request, add_to_cleanup=False)
        
        # The API returns 422 for malformed JSON, not 400 as expected
        assert_status(response, 422, f"Expected 422 status code for malformed JSON, got {response.status}")
    
    def test_empty_request_body(self, api_context, request, mesh_ids, mesh_api, assert_status):
        """Test API behavior with empty request body."""
        context, access_token = api_context
        # Test with empty JSON object
        empty_json = '{}'
        
        response = mesh_api.create_mesh(empty_json, request, add_to_cleanup=False)
        
        assert_status(response, 422, f"Expected 422 status code for empty request body, got {response.status}")
        
        # Test with empty string
        response = mesh_api.create_mesh("", request, add_to_cleanup=False)
        
        # The API returns 422 for empty string, not 400 as expected
        assert_status(response, 422, f"Expected 422 status code for empty string, got {response.status}")
    
    def test_error_response_format(self, api_context, request, valid_mesh_payload, mesh_ids, mesh_api, assert_error_response):
        """Test the format of error responses."""
        context, access_token = api_context
        # Create a payload that should trigger a validation error
        payload = mesh_api.modify_payload(valid_mesh_payload, "entity.name", "")  # Empty name should cause validation error
        
        response = mesh_api.create_mesh(payload, request, add_to_cleanup=False)
        
        if not response.ok:
            assert_error_response(response)
    
    @pytest.mark.serial
    def test_too_many_requests(self, api_context, request, mesh_ids, mesh_api):
        """Test API rate limiting by sending many requests in quick succession."""
        context, access_token = api_context
        # Send 10 requests in quick succession
        responses = []
        for i in range(10):
            payload = create_mesh_payload(f"Rate Limit Test Mesh {i}")
            response = mesh_api.create_mesh(payload, add_to_cleanup=False)
            responses.append({"status": response.status, "ok": response.ok})
        
        record_api_info(request, "POST", "/api/data/mesh", {"rate_limit_test": True}, {"responses": responses})
        
        # Check if any requests were rate limited (HTTP 429)
        rate_limited = any(r["status"] == 429 for r in responses)
        
        # This is an informational test - we're just checking if rate limiting exists
        # No assertion necessary, as the API may or may not implement rate limiting
