"""
Test procedures generator for Velora API testing.

This module provides comprehensive test procedures for API automation,
including step-by-step execution of various API operations.
"""

from _pytest._code import source
import pytest
import os
import sys
import json
import importlib.util
from typing import Any, Dict
import time

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from constants.status_check_compute import COMPLETED
from test_data.velora.product_transformation_payload import (
    create_transformation_builder_payload_with_inputs,
)
from utils.common import register_entity, find_entity, record_api_info
from constants import API_ENDPOINTS
from steps import (
    check_compute,
    create_mesh,
    create_system,
    create_source,
    create_object,
    link_object_to_source,
    config_object,
    create_product,
    link_product_to_object,
    link_product_to_product,
    create_data_product_schema,
    link_system_to_source,
    config_connection_detail_source,
    set_connection_secret,
    create_transformation_builder,
    login,
    check_status_compute,
    get_source_by_id,
    get_object_by_id,
    get_product_by_id,
)

# Import mock configuration
from tests.mock_config import create_mock_context, setup_mock_responses, mock_config

# Load procedure configuration
spec = importlib.util.spec_from_file_location(
    "procedure_config", "test_data/procedures_temp/procedure-1.py"
)
if spec is None:
    raise FileNotFoundError("Could not load procedure configuration file")
if spec.loader is None:
    raise FileNotFoundError("Could not load procedure configuration file")
procedure_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(procedure_config)
config = procedure_config.config

# Environment variables
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
USERNAME = os.getenv("QA_USERNAME", "test_user")
PASSWORD = os.getenv("QA_PASSWORD", "test_password")

if config is None:
    config = {}

global is_check_compute


@pytest.fixture(scope="session")
def api_context():
    """
    Create API request context and get access token.

    Returns:
        Tuple of (context, access_token)
    """
    context = create_mock_context()
    setup_mock_responses(context, mock_config)

    yield context, mock_config.access_token
    context.dispose()


@pytest.fixture(scope="session")
def id_map() -> Dict[str, Any]:
    """Return an empty ID mapping dictionary."""
    return {}


def skip_if_no_token(access_token: str) -> None:
    """
    Skip test if no access token is available.

    Args:
        access_token: The access token to check
    """
    if not access_token:
        pytest.skip("Skipping test: Access token not found")


def assert_success_response(response: Any) -> None:
    """
    Assert that the response indicates success.

    Args:
        response: The API response to check

    Raises:
        pytest.fail: If the response indicates failure
    """
    try:
        if not response.ok:
            text = response.text()
            pytest.fail(f"Request failed: {response.status} - {text}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")


def assert_entity_created(response: Any) -> str:
    """
    Assert that an entity was created and return its identifier.

    Args:
        response: The API response to check

    Returns:
        The identifier of the created entity

    Raises:
        pytest.fail: If the response indicates failure or missing data
    """
    try:
        if not response.ok:
            pytest.fail(f"Request failed: {response.status} - {response.text()}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")

    entity = response.json().get("entity")
    assert entity is not None, "Response missing 'entity'"
    identifier = entity.get("identifier")
    assert identifier is not None, "Entity missing 'identifier'"
    return identifier


class ProcedureStep:
    """Base class for all procedure steps."""

    def __init__(
        self,
        request: Any,
        step: Dict[str, Any],
        api_context: tuple[Any, str],
        id_map: Dict[str, Any],
    ):
        """
        Initialize a procedure step.

        Args:
            request: The test request object
            step: The step configuration
            api_context: Tuple of (context, access_token)
            id_map: The entity ID mapping dictionary
        """
        self.request = request
        self.step = step
        self.api_context = api_context
        self.id_map = id_map

    def execute(self) -> None:
        """Execute the procedure step. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must override this method")


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
        print("🔍 Source response:", response)
        print("🔍 Source response.json():", response.json())
        print("🔍 Source response.ok:", response.ok)
        source_id = assert_entity_created(response)
        register_entity(
            self.id_map,
            {"id": self.step["id"], "identifier": source_id, "type": "source"},
        )


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


class CreateProductStep(ProcedureStep):
    """Step to create a product entity."""

    def execute(self) -> None:
        """Execute product creation step."""
        print("▶️ create_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        mesh = None
        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create product not found")

        if self.step.get("mesh_ref"):
            mesh = find_entity(self.id_map, self.step["mesh_ref"])
            if mesh is not None:
                payload["host_mesh_identifier"] = mesh["identifier"]

        response = create_product(context, payload, access_token, self.request)
        product_id = assert_entity_created(response)
        register_entity(
            self.id_map,
            {"id": self.step["id"], "identifier": product_id, "type": "product"},
        )


class LinkProductToObjectStep(ProcedureStep):
    """Step to link a product to an object."""

    def execute(self) -> None:
        """Execute product-to-object linking step."""
        print("▶️ link_product_to_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            if self.step["input"].get("object_ref"):
                object_entity = find_entity(
                    self.id_map, self.step["input"].get("object_ref")
                )
            if self.step["input"].get("product_ref"):
                product_entity = find_entity(
                    self.id_map, self.step["input"].get("product_ref")
                )

            if object_entity and product_entity:
                response = link_product_to_object(
                    context, product_entity, object_entity, access_token, self.request
                )
                assert_success_response(response)
            else:
                pytest.fail("object or product not found")
        else:
            pytest.fail("input link product to object not found")


class LinkProductToProductStep(ProcedureStep):
    """Step to link a product to another product."""

    def execute(self) -> None:
        """Execute product-to-product linking step."""
        print("▶️ link_product_to_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            if self.step["input"].get("product_ref"):
                product_entity = find_entity(
                    self.id_map, self.step["input"].get("product_ref")
                )
            if self.step["input"].get("product_child_ref"):
                product_child_entity = find_entity(
                    self.id_map, self.step["input"].get("product_child_ref")
                )

            if product_entity and product_child_entity:
                response = link_product_to_product(
                    context,
                    product_entity,
                    product_child_entity,
                    access_token,
                    self.request,
                )
                assert_success_response(response)
            else:
                pytest.fail("product or product child not found")
        else:
            pytest.fail("input link product to product not found")


class CreateDataProductSchemaStep(ProcedureStep):
    """Step to create a data product schema."""

    def execute(self) -> None:
        """Execute data product schema creation step."""
        print("▶️ create_data_product_schema_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        product_entity = find_entity(self.id_map, self.step["ref"])

        if "input" in self.step:
            payload = self.step["input"]
        else:
            pytest.fail("input create data product schema not found")

        if product_entity:
            response = create_data_product_schema(
                context, product_entity, payload, access_token, self.request
            )
            assert_success_response(response)
        else:
            pytest.fail("product not found")


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


class CreateTransformationBuilderStep(ProcedureStep):
    """Step to create a transformation builder."""

    def execute(self) -> None:
        """Execute transformation builder creation step."""
        print("▶️ create_transformation_builder_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        if "input" in self.step:
            if self.step["input"].get("product_ref"):
                product_entity = find_entity(
                    self.id_map, self.step["input"].get("product_ref")
                )
            if self.step["input"].get("input_refs"):
                input_entities = []
                for input_ref in self.step["input"].get("input_refs"):
                    input_entity = find_entity(self.id_map, input_ref)
                    if input_entity:
                        input_entities.append(input_entity)
                    else:
                        pytest.fail(f"input {input_ref} not found")

                if input_entities:
                    payload = create_transformation_builder_payload_with_inputs(
                        input_entities
                    )
                    print("payload", json.dumps(payload, indent=2))
                else:
                    pytest.fail("input entities not found")
            else:
                pytest.fail("input input_refs not found")

            if product_entity:
                response = create_transformation_builder(
                    context, product_entity, payload, access_token, self.request
                )
                assert_success_response(response)
            else:
                pytest.fail("product not found")


class CheckStatusComputeStep(ProcedureStep):
    """Step to check the status of a compute."""

    def execute(self) -> None:
        """Execute compute status checking step with retry logic."""
        time.sleep(2)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        entity = find_entity(self.id_map, self.step["ref"])
        if entity is None:
            pytest.fail("Entity not found")

        entity_type = entity.get("type")
        identifier = entity.get("identifier")

        if entity_type == "source":
            response = get_source_by_id(context, identifier, access_token, self.request)
        elif entity_type == "object":
            response = get_object_by_id(context, identifier, access_token, self.request)
        elif entity_type == "product":
            response = get_product_by_id(
                context, identifier, access_token, self.request
            )
        else:
            pytest.fail(f"Unknown entity type: {entity_type}")

        if not response or not response.ok:
            pytest.fail(
                f"Get {entity_type} by id failed: {response.text() if response else 'No response'}"
            )

        data = response.json()
        compute_identifier = data.get("compute_identifier")
        healthy = data.get("healthy")

        MAX_RETRIES = self.step.get("max_retries", 5)
        DELAY_SECONDS = self.step.get("retry_interval", 60)

        for attempt in range(1, MAX_RETRIES + 1):
            print(
                f"[CheckStatusComputeStep] Attempt {attempt}/{MAX_RETRIES} checking compute status..."
            )

            response = check_status_compute(
                context, compute_identifier, access_token, self.request
            )
            assert_success_response(response)

            data = response.json()
            status = data.get("status")

            if healthy and status == COMPLETED:
                print("[CheckStatusComputeStep] Compute completed successfully.")
                return

            if attempt < MAX_RETRIES:
                print(
                    f"[CheckStatusComputeStep] Not completed yet. Retrying in {DELAY_SECONDS} seconds..."
                )
                time.sleep(DELAY_SECONDS)
            else:
                try:
                    pytest.fail("Compute failed after retries: " + json.dumps(data))
                finally:
                    pytest.exit("Stopping all tests due to compute failure")


def get_step_instance(
    request: Any,
    step: Dict[str, Any],
    api_context: tuple[Any, str],
    id_map: Dict[str, Any],
) -> ProcedureStep:
    """
    Factory function to create step instances based on step type.

    Args:
        request: The test request object
        step: The step configuration
        api_context: Tuple of (context, access_token)
        id_map: The entity ID mapping dictionary

    Returns:
        A ProcedureStep instance

    Raises:
        ValueError: If the step type is unknown
    """
    step_type = step.get("type")
    mapping = {
        "create_mesh": CreateMeshStep,
        "create_system": CreateSystemStep,
        "create_source": CreateSourceStep,
        "create_object": CreateObjectStep,
        "link_object_to_source": LinkObjectToSourceStep,
        "configure_object_details": ConfigureObjectDetailsStep,
        "create_product": CreateProductStep,
        "link_product_to_object": LinkProductToObjectStep,
        "link_product_to_product": LinkProductToProductStep,
        "define_product_schema": CreateDataProductSchemaStep,
        "link_system_to_source": LinkSystemToSourceStep,
        "configure_source": ConfigureConnectionDetailsStep,
        "set_source_secret": SetConnectionSecretsStep,
        "apply_product_transformation": CreateTransformationBuilderStep,
        "check_status_compute": CheckStatusComputeStep,
    }

    if step_type not in mapping:
        raise ValueError(f"Unknown step type: {step_type}")

    return mapping[step_type](request, step, api_context, id_map)


def test_login_api(api_context: tuple[Any, str], request: Any) -> None:
    """
    Test API login functionality.

    Args:
        api_context: Tuple of (context, access_token)
        request: The test request object
    """
    context, access_token = api_context
    url = API_ENDPOINTS["LOGIN"]
    method = "POST"
    payload = {"user": USERNAME, "password": PASSWORD}

    if not access_token:
        record_api_info(request, method, url, payload, "Login failed - no access token")
        pytest.fail("Login failed - no access token")
    else:
        record_api_info(request, method, url, payload, "Login successful")
        assert access_token is not None


@pytest.mark.parametrize(
    "step",
    config.get("steps", []),
    ids=lambda x: f"Step {config.get('steps', []).index(x) + 1}: {x['type']}_{x.get('id') or x.get('identifier') or x.get('ref') or ''}",
)
def test_step_execution(
    request: Any,
    step: Dict[str, Any],
    api_context: tuple[Any, str],
    id_map: Dict[str, Any],
) -> None:
    """
    Execute individual test steps.

    Args:
        request: The test request object
        step: The step configuration
        api_context: Tuple of (context, access_token)
        id_map: The entity ID mapping dictionary
    """
    get_step_instance(request, step, api_context, id_map).execute()
