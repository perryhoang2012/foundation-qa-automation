"""
Test procedures generator for Velora API testing.

This module provides comprehensive test procedures for API automation,
including step-by-step execution of various API operations.
"""

import json
import os
import importlib.util
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError


from steps.mesh_steps import CreateMeshStep, GetAllMeshStep
from steps.check_compute import CheckStatusComputeStep
from steps.object_steps import (
    ConfigureObjectDetailsStep,
    CreateObjectStep,
    GetAllObjectStep,
    GetObjectByIdStep,
    LinkObjectToSourceStep,
)
from steps.product_steps import (
    CreateDataProductSchemaStep,
    CreateProductStep,
    CreateTransformationBuilderStep,
    GetAllProductStep,
    GetProductByIdStep,
    LinkProductToObjectStep,
    LinkProductToProductStep,
)
from steps.source_steps import (
    ConfigureConnectionDetailsStep,
    CreateSourceStep,
    GetAllSourceStep,
    GetSourceByIdStep,
    LinkSystemToSourceStep,
    SetConnectionSecretsStep,
)
from steps.system_steps import CreateSystemStep, GetAllSystemStep

import pytest
from tests.e2e.procedures.mock_config import (
    create_mock_context,
    setup_mock_responses,
    mock_config,
)
from utils.common import record_api_info
from config import API_ENDPOINTS


# Load procedure configuration
spec = importlib.util.spec_from_file_location(
    "procedure_config", "test_data/procedures/procedure-1.py"
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
def id_map():
    """Return an empty ID mapping dictionary."""
    return {}


def get_step_instance(
    request,
    step,
    api_context,
    id_map,
):
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
        "get_all_mesh": GetAllMeshStep,
        "create_mesh": CreateMeshStep,
        "get_all_system": GetAllSystemStep,
        "create_system": CreateSystemStep,
        "get_all_source": GetAllSourceStep,
        "get_source_by_id": GetSourceByIdStep,
        "create_source": CreateSourceStep,
        "get_all_object": GetAllObjectStep,
        "get_object_by_id": GetObjectByIdStep,
        "create_object": CreateObjectStep,
        "link_object_to_source": LinkObjectToSourceStep,
        "configure_object_details": ConfigureObjectDetailsStep,
        "get_all_product": GetAllProductStep,
        "get_product_by_id": GetProductByIdStep,
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


def test_login_api(api_context, request):
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
    request,
    step,
    api_context,
    id_map,
):
    """
    Execute individual test steps.

    Args:
        request: The test request object
        step: The step configuration
        api_context: Tuple of (context, access_token)
        id_map: The entity ID mapping dictionary
    """
    get_step_instance(request, step, api_context, id_map).execute()
    print(id_map)
