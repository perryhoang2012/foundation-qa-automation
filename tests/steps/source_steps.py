import pytest
from api.source import (
    config_connection_detail_source,
    create_source,
    get_all_source,
    link_system_to_source,
    set_connection_secret,
)
from steps.procedure import ProcedureStep
from utils.common import (
    assert_entity_created,
    assert_success_response,
    find_entity,
    register_entity,
    skip_if_no_token,
)


class GetAllSourceStep(ProcedureStep):
    """Step to get all source entities."""

    def execute(self) -> None:
        """Execute source retrieval step."""
        print("▶️ get_all_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        response = get_all_source(context, access_token, self.request)


class CreateSourceStep(ProcedureStep):
    """Step to create a source entity."""

    def execute(self) -> None:
        """Execute source creation step."""
        print("▶️ create_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create source not found")

        response = create_source(context, payload, access_token, self.request)
        source_id = assert_entity_created(response)
        register_entity(
            self.id_map,
            {"id": self.step["id"], "identifier": source_id, "type": "source"},
        )


class ConfigureConnectionDetailsStep(ProcedureStep):
    """Step to configure connection details for a source."""

    def execute(self) -> None:
        """Execute connection details configuration step."""
        print("▶️ configure_connection_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        source_entity = find_entity(self.id_map, self.step["ref"])

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input configure connection details not found")

        if source_entity:
            response = config_connection_detail_source(
                context, source_entity, payload, access_token, self.request
            )
            assert_success_response(response)
        else:
            pytest.fail("source not found")


class SetConnectionSecretsStep(ProcedureStep):
    """Step to set connection secrets for a source."""

    def execute(self) -> None:
        """Execute connection secrets setting step."""
        print("▶️ set_connection_secrets_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        source_entity = find_entity(self.id_map, self.step["ref"])

        if "input" in self.step:
            if source_entity:
                payload = self.step["input"]
                response = set_connection_secret(
                    context, source_entity, payload, access_token, self.request
                )
                assert_success_response(response)
            else:
                pytest.fail("source not found")
        else:
            pytest.fail("input set connection secrets not found")


class LinkSystemToSourceStep(ProcedureStep):
    """Step to link a system to a source."""

    def execute(self) -> None:
        """Execute system-to-source linking step."""
        print("▶️ link_system_to_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            if self.step["input"].get("system_ref"):
                system_entity = find_entity(
                    self.id_map, self.step["input"].get("system_ref")
                )
            if self.step["input"].get("source_ref"):
                source_entity = find_entity(
                    self.id_map, self.step["input"].get("source_ref")
                )

        if source_entity and system_entity:
            response = link_system_to_source(
                context, system_entity, source_entity, access_token, self.request
            )
            assert_success_response(response)
        else:
            pytest.fail("source or system not found")
