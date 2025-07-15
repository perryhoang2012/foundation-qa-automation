import os
import sys

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from constants.api_endpoints import API_ENDPOINTS
from test_data.shared.connection_source_payload import create_connection_source_payload
from test_data.shared.mesh_payload import create_mesh_payload
from test_data.shared.object_payload import (
    configure_object_payload,
    create_object_payload,
)
from test_data.shared.product_payload import create_product_payload
from test_data.shared.schema_product_payload import schema_product_create_payload
from test_data.shared.source_payload import create_source_payload
from test_data.shared.system_payload import create_system_payload
from utils.load_config import load_config
from utils.common import register_entity, find_entity, record_api_info

# Import mock configuration
from tests.mock_config import create_mock_context, setup_mock_responses, mock_config

from api import (
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
    login,
)

# Load environment variables
load_dotenv()

# Load landscape configuration
landscape_config = load_config("test_data/landscapes/landscape-4.yml")

# Environment variables
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
USERNAME = os.getenv("QA_USERNAME", "")
PASSWORD = os.getenv("QA_PASSWORD", "")
X_ACCOUNT = os.getenv("X_ACCOUNT", "")


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


def skip_if_no_token(access_token):
    """
    Skip test if no access token is available.

    Args:
        access_token: Access token to check
    """
    if not access_token:
        pytest.skip("Skipping test: Access token not found")


def assert_success_response(response):
    """
    Assert that the response is successful.

    Args:
        response: Response object to check

    Raises:
        pytest.fail: If response is not successful
    """
    try:
        if not response.ok:
            text = response.text()
            pytest.fail(f"Request failed: {response.status} - {text}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")


def assert_entity_created(response) -> str:
    """
    Assert that an entity was created successfully and return its identifier.

    Args:
        response: Response object to check

    Returns:
        Entity identifier

    Raises:
        pytest.fail: If entity creation failed
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
    "mesh", landscape_config["mesh"], ids=[m["id"] for m in landscape_config["mesh"]]
)
def test_create_mesh(api_context, id_map, request, mesh):
    """
    Test creating mesh entities.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        mesh: Mesh configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    payload = create_mesh_payload(mesh.get("name"))
    response = create_mesh(context, payload, access_token, request)
    mesh_id = assert_entity_created(response)
    register_entity(id_map, {"id": mesh["id"], "identifier": mesh_id, "type": "mesh"})


@pytest.mark.parametrize(
    "system",
    landscape_config["systems"],
    ids=[s["id"] for s in landscape_config["systems"]],
)
def test_create_system(api_context, id_map, request, system):
    """
    Test creating system entities.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        system: System configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    payload = create_system_payload(system.get("name"))
    response = create_system(context, payload, access_token, request)
    system_id = response.json()["identifier"]
    assert system_id is not None, "System ID is missing"
    register_entity(
        id_map, {"id": system["id"], "identifier": system_id, "type": "system"}
    )


@pytest.mark.parametrize(
    "source",
    landscape_config["sources"],
    ids=[s["id"] for s in landscape_config["sources"]],
)
def test_create_source(api_context, id_map, request, source):
    """
    Test creating source entities.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        source: Source configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    payload = create_source_payload(source.get("name"))
    response = create_source(context, payload, access_token, request)
    source_id = assert_entity_created(response)
    register_entity(
        id_map, {"id": source["id"], "identifier": source_id, "type": "source"}
    )


@pytest.mark.parametrize(
    "source",
    landscape_config["sources"],
    ids=[
        f"{source['system']} to {source['id']}"
        for source in landscape_config["sources"]
    ],
)
def test_link_system_to_source(
    api_context,
    id_map,
    request,
    source,
):
    """
    Test linking system to source.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        source: Source configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    source_entity = find_entity(id_map, source["id"])
    system_entity = find_entity(id_map, source["system"])

    if source_entity and system_entity:
        response = link_system_to_source(
            context, system_entity, source_entity, access_token, request
        )
        assert_success_response(response)


@pytest.mark.parametrize(
    "source",
    landscape_config["sources"],
    ids=[f"{source['id']}" for source in landscape_config["sources"]],
)
def test_configure_connection_details(
    api_context,
    id_map,
    request,
    source,
):
    """
    Test configuring connection details for sources.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        source: Source configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    source_entity = find_entity(id_map, source["id"])
    if source_entity:
        payload = create_connection_source_payload()
        response = config_connection_detail_source(
            context, source_entity, payload, access_token, request
        )
        assert_success_response(response)


@pytest.mark.parametrize(
    "source",
    landscape_config["sources"],
    ids=[f"{source['id']}" for source in landscape_config["sources"]],
)
def test_set_connection_secrets(
    api_context,
    id_map,
    request,
    source,
):
    """
    Test setting connection secrets for sources.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        source: Source configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    source_entity = find_entity(id_map, source["id"])
    if source_entity:
        payload = {
            "access_key": os.getenv("S3_ACCESS_KEY", ""),
            "access_secret": os.getenv("S3_SECRET_KEY", ""),
        }
        response = set_connection_secret(
            context, source_entity, payload, access_token, request
        )
        assert_success_response(response)


@pytest.mark.parametrize(
    "object",
    landscape_config["objects"],
    ids=[o["id"] for o in landscape_config["objects"]],
)
def test_create_object(
    api_context,
    id_map,
    request,
    object,
):
    """
    Test creating object entities.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        object: Object configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    payload = create_object_payload(object.get("name"))
    response = create_object(context, payload, access_token, request)
    object_id = assert_entity_created(response)
    register_entity(
        id_map, {"id": object["id"], "identifier": object_id, "type": "object"}
    )


@pytest.mark.parametrize(
    "object",
    landscape_config["objects"],
    ids=[
        f"{object['source']} to {object['id']}"
        for object in landscape_config["objects"]
    ],
)
def test_link_object_to_source(
    api_context,
    id_map,
    request,
    object,
):
    """
    Test linking object to source.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        object: Object configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    object_entity = find_entity(id_map, object["id"])
    source_entity = find_entity(id_map, object["source"])

    if object_entity and source_entity:
        response = link_object_to_source(
            context, source_entity, object_entity, access_token, request
        )
        assert_success_response(response)


@pytest.mark.parametrize(
    "object",
    landscape_config["objects"],
    ids=[f"{object['id']}" for object in landscape_config["objects"]],
)
def test_configure_object_details(
    api_context,
    id_map,
    request,
    object,
):
    """
    Test configuring object details.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        object: Object configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    object_entity = find_entity(id_map, object["id"])
    if object_entity:
        payload = configure_object_payload()
        response = config_object(context, object_entity, payload, access_token, request)
        assert_success_response(response)


@pytest.mark.parametrize(
    "product",
    landscape_config["products"],
    ids=[product["id"] for product in landscape_config["products"]],
)
def test_create_product(
    api_context,
    id_map,
    request,
    product,
):
    """
    Test creating product entities.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        product: Product configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    mesh = find_entity(id_map, product["mesh"])
    if mesh is None:
        pytest.fail(f"Mesh not found for product {product['id']}")

    payload = create_product_payload(mesh["identifier"], product.get("name"))
    response = create_product(context, payload, access_token, request)
    product_id = assert_entity_created(response)
    register_entity(
        id_map, {"id": product["id"], "identifier": product_id, "type": "product"}
    )


@pytest.mark.parametrize(
    "product",
    landscape_config["products"],
    ids=[f"{product['id']}" for product in landscape_config["products"]],
)
def test_link_inputs_to_product(
    api_context,
    id_map,
    request,
    product,
):
    """
    Test linking inputs to product.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        product: Product configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    product_entity = find_entity(id_map, product["id"])
    for input_item in product["input"]:
        entity = find_entity(id_map, input_item)
        if entity and product_entity:
            if "obj" in input_item:
                response = link_product_to_object(
                    context, product_entity, entity, access_token, request
                )
                assert_success_response(response)
            elif "prod" in input_item:
                response = link_product_to_product(
                    context,
                    entity,
                    product_entity,
                    access_token,
                    request,
                )
                assert_success_response(response)


@pytest.mark.parametrize(
    "product",
    landscape_config["products"],
    ids=[f"{product['id']}" for product in landscape_config["products"]],
)
def test_create_data_product_schema(
    api_context,
    id_map,
    request,
    product,
):
    """
    Test creating data product schema.

    Args:
        api_context: Tuple of (context, access_token)
        id_map: List to store entity mappings
        request: Pytest request object
        product: Product configuration
    """
    context, access_token = api_context
    skip_if_no_token(access_token)

    product_entity = find_entity(id_map, product["id"])
    if product_entity:
        payload = schema_product_create_payload()
        response = create_data_product_schema(
            context, product_entity, payload, access_token, request
        )
        assert_success_response(response)
