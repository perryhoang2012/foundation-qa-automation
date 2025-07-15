import pytest

from api.object import (
    config_object,
    create_object,
    delete_object,
    get_all_object,
    get_object_by_id,
    link_object_to_source,
)
from steps.procedure import ProcedureStep
from utils.common import (
    assert_entity_created,
    assert_success_response,
    find_entity,
    register_entity,
    skip_if_no_token,
)


class GetAllObjectStep(ProcedureStep):
    """Step to get all object resources."""

    def execute(self) -> None:
        """Execute object retrieval step."""
        print("▶️ get_all_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        response = get_all_object(context, access_token, self.request)


class GetObjectByIdStep(ProcedureStep):
    """Step to get an object by its identifier."""

    def execute(self) -> None:
        """Execute object retrieval step."""
        print("▶️ get_object_by_id_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "ref" in self.step:
            payload = self.step["ref"]
        else:
            pytest.fail("input get object by id not found")

        response = get_object_by_id(context, access_token, payload, self.request)


class CreateObjectStep(ProcedureStep):
    """Step to create an object entity."""

    def execute(self) -> None:
        """Execute object creation step."""
        print("▶️ create_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create object not found")

        response = create_object(context, payload, access_token, self.request)
        object_id = assert_entity_created(response)
        register_entity(
            self.id_map,
            {"id": self.step["id"], "identifier": object_id, "type": "object"},
        )


class DeleteObjectStep(ProcedureStep):
    """Step to delete an object entity."""

    def execute(self) -> None:
        """Execute object deletion step."""
        print("▶️ delete_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "ref" in self.step:
            ref = self.step["ref"]
        else:
            pytest.fail("input delete object not found")

        response = delete_object(context, ref, access_token, self.request)


class LinkObjectToSourceStep(ProcedureStep):
    """Step to link an object to a source."""

    def execute(self) -> None:
        """Execute object-to-source linking step."""
        print("▶️ link_object_to_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        source_entity = None
        object_entity = None

        if "input" in self.step:
            if self.step["input"].get("source_ref"):
                source_entity = find_entity(
                    self.id_map, self.step["input"].get("source_ref")
                )
            if self.step["input"].get("object_ref"):
                object_entity = find_entity(
                    self.id_map, self.step["input"].get("object_ref")
                )

            if object_entity and source_entity:
                response = link_object_to_source(
                    context, source_entity, object_entity, access_token, self.request
                )
                assert_success_response(response)
            else:
                pytest.fail("object or source not found")
        else:
            pytest.fail("input not found")


class ConfigureObjectDetailsStep(ProcedureStep):
    """Step to configure object details."""

    def execute(self) -> None:
        """Execute object configuration step."""
        print("▶️ configure_object_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        object_entity = find_entity(self.id_map, self.step["ref"])

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input configure object details not found")

        if object_entity:
            response = config_object(
                context, object_entity, payload, access_token, self.request
            )
            assert_success_response(response)
        else:
            pytest.fail("object not found")
