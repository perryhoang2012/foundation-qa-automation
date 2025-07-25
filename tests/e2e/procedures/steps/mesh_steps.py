"""
Mesh step operations for API testing.

This module provides functions to interact with mesh-related API endpoints
including creating, reading, and deleting mesh resources.
"""

import pytest

from api.mesh import create_mesh, get_all_mesh, delete_mesh
from steps.procedure import ProcedureStep
from utils.common import assert_entity_created, skip_if_no_token, register_entity


class CreateMeshStep(ProcedureStep):
    """Step to create a mesh entity."""

    def execute(self) -> None:
        """Execute mesh creation step."""
        print("▶️ create_mesh_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create mesh not found")

        response = create_mesh(context, payload, access_token, self.request)
        mesh_id = assert_entity_created(response)
        register_entity(
            self.id_map, {"id": self.step["id"], "identifier": mesh_id, "type": "mesh"}
        )


class GetAllMeshStep(ProcedureStep):
    """Step to create a mesh entity."""

    def execute(self) -> None:
        """Execute mesh creation step."""
        print("▶️ create_mesh_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        response = get_all_mesh(context, access_token, self.request)


class DeleteMeshStep(ProcedureStep):
    """Step to delete a mesh entity."""

    def execute(self) -> None:
        """Execute the mesh deletion step."""
        print("▶️ delete_mesh_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        mesh_ref = self.step.get("input", {}).get("mesh_ref")
        if not mesh_ref:
            pytest.fail("Mesh reference ('mesh_ref') is required for deletion.")

        mesh_entry = self.id_map.get(mesh_ref)
        if not mesh_entry or "identifier" not in mesh_entry:
            pytest.fail("Mesh reference ('mesh_ref') not found in id_map.")
        mesh_id = mesh_entry["identifier"]

        response = delete_mesh(context, mesh_id, access_token, self.request)
