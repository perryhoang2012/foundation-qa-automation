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
        """Execute mesh deletion step."""
        print("▶️ delete_mesh_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "ref" in self.step:
            ref = self.step["ref"]
        else:
            pytest.fail("input delete mesh not found")

        response = delete_mesh(context, ref, access_token, self.request)
