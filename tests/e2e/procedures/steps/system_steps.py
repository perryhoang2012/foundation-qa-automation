import pytest
from api.system import create_system, delete_system, get_all_system
from steps.procedure import ProcedureStep
from utils.common import register_entity, skip_if_no_token


class GetAllSystemStep(ProcedureStep):
    """Step to get all system entities."""

    def execute(self) -> None:
        """Execute system retrieval step."""
        print("▶️ get_all_system_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        response = get_all_system(context, access_token, self.request)


class CreateSystemStep(ProcedureStep):
    """Step to create a system entity."""

    def execute(self) -> None:
        """Execute system creation step."""
        print("▶️ create_system_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create system not found")

        response = create_system(context, payload, access_token, self.request)
        system_id = response.json()["identifier"]
        assert system_id is not None, "System ID is missing"
        register_entity(
            self.id_map,
            {"id": self.step["id"], "identifier": system_id, "type": "system"},
        )


class DeleteSystemStep(ProcedureStep):
    """Step to delete a system entity."""

    def execute(self) -> None:
        """Execute system deletion step."""
        print("▶️ delete_system_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "ref" in self.step:
            ref = self.step["ref"]
        else:
            pytest.fail("input delete system not found")

        response = delete_system(context, ref, access_token, self.request)
