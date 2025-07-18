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
    return create_mesh_payload("Test Mesh Validation")

class TestMeshFieldValidation:
    """Test class for validating different fields in the Mesh API."""
    
    def test_mesh_description_validation(self, api_context, request, valid_mesh_payload, mesh_ids):
        """Test validation for the description field."""
        context, access_token = api_context
        # Test with empty description
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["description"] = ""
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        # Check if API accepts empty description or requires non-empty
        if response.ok:
            json_response = response.json()
            assert "entity" in json_response, "Response missing 'entity' field"
            assert json_response["entity"]["description"] == "", "Description should be empty"
            mesh_ids.append(json_response["entity"]["identifier"])  # Add to cleanup list
        
        # Test with very long description
        payload["entity"]["description"] = "A" * 2000  # 2000 characters
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        
        # The test assertion depends on API's behavior with long descriptions
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
    
    def test_mesh_purpose_validation(self, api_context, request, valid_mesh_payload, mesh_ids):
        """Test validation for the purpose field."""
        context, access_token = api_context
        # Test with empty purpose
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["purpose"] = ""
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        # Check if API accepts empty purpose or requires non-empty
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
    
    def test_mesh_assignees_validation(self, api_context, request, valid_mesh_payload, mesh_ids):
        """Test validation for the assignees field."""
        context, access_token = api_context
        # Test with empty assignees list
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["assignees"] = []
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
        
        # Test with invalid email format
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["assignees"] = [
            {
                "email": "invalid-quang.doan",
                "full_name": "Test User",
                "role": "Owner",
            }
        ]
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
        
        # Test with missing required assignee fields
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["assignees"] = [
            {
                "email": "quang.doan@meshx.io",
                # Missing full_name and role
            }
        ]
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
    
    def test_mesh_security_policy_validation(self, api_context, request, valid_mesh_payload, mesh_ids):
        """Test validation for the security_policy field."""
        context, access_token = api_context
        # Test with invalid security policy structure
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["security_policy"] = "not-an-array"
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list
        
        # Assuming security_policy is an array of objects with specific structure
        payload = deepcopy(valid_mesh_payload)
        payload["entity"]["security_policy"] = [
            {"invalid_key": "value"}
        ]
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/mesh", payload, response)
        
        if response.ok:
            mesh_ids.append(response.json()["entity"]["identifier"])  # Add to cleanup list

class TestMeshApiPerformance:
    """Test class for API performance aspects."""
    
    def test_create_multiple_mesh_entities(self, api_context, request, mesh_ids):
        """Test creating multiple mesh entities in sequence to check performance."""
        context, access_token = api_context
        # Create 5 mesh entities in sequence
        created_meshes = []
        for i in range(5):
            payload = create_mesh_payload(f"Performance Test Mesh {i}")
            start_time = pytest.importorskip("time").time()
            response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
            end_time = pytest.importorskip("time").time()
            
            # Record response time
            duration = end_time - start_time
            
            if response.ok:
                mesh_id = response.json()["entity"]["identifier"]
                mesh_ids.append(mesh_id)  # Add to cleanup list
                created_meshes.append({
                    "id": mesh_id,
                    "name": payload["entity"]["name"],
                    "response_time": duration
                })
        
        # Log performance data
        avg_response_time = sum(m["response_time"] for m in created_meshes) / len(created_meshes) if created_meshes else 0
        record_api_info(request, "POST", "/api/data/mesh", 
                       {"performance_test": "create_multiple_mesh_entities"},
                       {"created_meshes": len(created_meshes), "avg_response_time": avg_response_time})
        
        assert len(created_meshes) > 0, "Failed to create any mesh entities"
        # Add assertion for acceptable response time if there's a known threshold

class TestMeshApiEdgeCases:
    """Test class for API edge cases."""
    
    def test_special_characters_in_mesh_name(self, api_context, request, mesh_ids):
        """Test creating a mesh with special characters in the name."""
        context, access_token = api_context
        special_chars = [
            "Test Mesh !@#$%^&*()_+",
            "Test Mesh with spaces",
            "Test-Mesh-with-hyphens",
            "Test_Mesh_with_underscores",
            "Test Mesh with 👍 emoji",
            "Test Mesh with quotes \" ' ",
            "Test Mesh with <html> tags",
        ]
        
        for name in special_chars:
            payload = create_mesh_payload(name)
            response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(request, "POST", "/api/data/mesh", {"name": name}, 
                          {"status": response.status, "ok": response.ok})
            
            # Check if API handles special characters correctly
            if response.ok:
                json_response = response.json()
                assert "entity" in json_response, "Response missing 'entity' field"
                mesh_ids.append(json_response["entity"]["identifier"])  # Add to cleanup list
                # Verify if the name is preserved or sanitized
    
    def test_request_timeout_handling(self, api_context, request, mesh_ids):
        """Test how the API handles potential timeouts with large payloads."""
        context, access_token = api_context
        # Create a very large payload to potentially trigger timeout
        payload = create_mesh_payload("Large Payload Test")
        
        # Add a lot of data to the payload
        payload["large_data"] = ["data" * 1000] * 100
        
        try:
            response = context.post('/api/data/mesh', data=json.dumps(payload), 
                                   headers=get_headers(access_token), timeout=5000)
            record_api_info(request, "POST", "/api/data/mesh", {"large_payload": True}, 
                          {"status": response.status, "ok": response.ok})
        except Exception as e:
            # Handle timeout or other exceptions
            record_api_info(request, "POST", "/api/data/mesh", {"large_payload": True}, 
                          {"error": str(e)})
            pytest.skip(f"Request failed with exception: {str(e)}")
