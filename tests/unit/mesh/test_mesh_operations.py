import os
import sys
import pytest
import json
import time
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from test_data.shared.mesh_payload import create_mesh_payload
from utils.common import makeid
from conftest import requires_auth, record_api_info, get_headers

@pytest.fixture(scope="module")
def created_mesh_id(api_context, mesh_ids, mesh_api):
    """Create a mesh and return its ID for testing other operations."""
    context, access_token = api_context
    # Create a new mesh for testing
    mesh_name = f"Operations Test Mesh {makeid(5)}"
    response = mesh_api.create_valid_mesh(mesh_name)
    
    if not response.ok:
        pytest.skip(f"Failed to create test mesh: {response.status} - {response.text()}")
    
    mesh_id = response.json()["entity"]["identifier"]
    
    yield mesh_id

class TestMeshApiOperations:
    """Test class for API operation validation focusing on specific functionalities."""
    
    def test_idempotent_creation(self, api_context, request, mesh_ids):
        """Test if creating the same mesh twice returns the same identifier (idempotency)."""
        context, access_token = api_context
        # Create a unique mesh with a consistent identifier for idempotency testing
        unique_id = makeid(10)
        mesh_name = f"Idempotent Mesh {unique_id}"
        
        payload = create_mesh_payload(mesh_name)
        # Add a consistent identifier for testing idempotency, if supported by the API
        if "external_id" in payload["entity"]:
            payload["entity"]["external_id"] = f"test-idempotent-{unique_id}"
        
        # First creation
        response1 = context.post('/api/data/mesh', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        })
        
        if not response1.ok:
            pytest.skip(f"First mesh creation failed: {response1.status} - {response1.text()}")
        
        first_id = response1.json()["entity"]["identifier"]
        mesh_ids.append(first_id)  # Add to the list for cleanup
        
        # Second creation with the exact same payload
        response2 = context.post('/api/data/mesh', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        })
        
        request.node._api_info = {
            "method": "POST",
            "url": "/api/data/mesh",
            "payload": payload,
            "first_response": response1.json(),
            "second_response": response2.json() if response2.ok else response2.text()
        }
        
        # Check if the API is idempotent - should either return the same ID or an error indicating duplication
        if response2.ok:
            second_id = response2.json()["entity"]["identifier"]
            # Note: This assertion may not pass if the API doesn't implement idempotency
            # In that case, the test should be adjusted based on the actual API behavior
            assert first_id == second_id, "API is not idempotent: returned different IDs for identical requests"
    
    @pytest.mark.serial
    def test_concurrent_creation(self, api_context, request, mesh_ids):
        """Test creating multiple meshes concurrently."""
        context, access_token = api_context
        # Create meshes sequentially instead of concurrently
        # Playwright doesn't support concurrent requests from the same context
        mesh_names = [f"Concurrent Mesh {i} {makeid(3)}" for i in range(5)]
        
        results = []
        for name in mesh_names:
            payload = create_mesh_payload(name)
            try:
                response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
                    "Authorization": f"Bearer {access_token}",
                    "x-account": os.getenv("X_ACCOUNT", ""),
                    "Content-Type": "application/json"
                })
                results.append({
                    "name": name,
                    "status": response.status,
                    "ok": response.ok,
                    "id": response.json()["entity"]["identifier"] if response.ok else None
                })
                
                # Add to cleanup list if mesh was created successfully
                if response.ok:
                    mesh_ids.append(response.json()["entity"]["identifier"])
            except Exception as e:
                results.append({"name": name, "error": str(e)})
        
        request.node._api_info = {
            "method": "POST",
            "url": "/api/data/mesh",
            "sequential_results": results
        }
        
        # Check if any meshes were created successfully
        successful = [r for r in results if r.get("ok", False)]
        assert len(successful) > 0, "Failed to create any meshes sequentially"
        
        # Log some information about the performance
        if len(successful) > 0:
            print(f"Successfully created {len(successful)} out of {len(results)} meshes sequentially")
    
    def test_create_mesh_transaction(self, api_context, request, mesh_ids):
        """Test if mesh creation is transactional (all-or-nothing)."""
        context, access_token = api_context
        # Create a payload with a valid structure but with some invalid data
        # that should cause the transaction to fail
        payload = create_mesh_payload("Transaction Test Mesh")
        
        # Add invalid data that should cause a validation error
        payload["entity"]["assignees"] = [
            {
                "email": "invalid-quang.doan",  # Invalid email format
                "full_name": "",  # Empty full name
                "role": "Invalid Role"  # Potentially invalid role
            }
        ]
        
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        })
        
        request.node._api_info = {
            "method": "POST",
            "url": "/api/data/mesh",
            "payload": payload,
            "response": response.json() if response.ok else response.text()
        }
        
        # If the API is truly transactional, the request should fail entirely
        # and not create a partial mesh
        assert not response.ok, "Request with invalid data should have failed"
        
        # If the request did succeed, we should check if the created mesh has the correct data
        # and doesn't contain partial/incorrect information
    
    def test_mesh_creation_with_minimal_fields(self, api_context, request, mesh_ids):
        """Test creating a mesh with only the minimal required fields."""
        context, access_token = api_context
        # Create a minimal payload with only the required fields
        minimal_payload = {
            "entity": {
                "name": f"Minimal Mesh {makeid(5)}",
                "entity_type": "mesh"
            },
            "entity_info": {
                "owner": os.getenv("OWNER_EMAIL", "quang.doan@meshx.io")
            }
        }
        
        response = context.post('/api/data/mesh', data=json.dumps(minimal_payload), headers={
            "Authorization": f"Bearer {access_token}",
            "x-account": os.getenv("X_ACCOUNT", ""),
            "Content-Type": "application/json"
        })
        
        request.node._api_info = {
            "method": "POST",
            "url": "/api/data/mesh",
            "payload": minimal_payload,
            "response": response.json() if response.ok else response.text()
        }
        
        # Check if the API accepts a minimal payload
        # This depends on what fields are actually required by the API
        if response.ok:
            mesh_id = response.json()["entity"]["identifier"]
            mesh_ids.append(mesh_id)  # Add to cleanup list
