import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError
import json

from utils.load_config import load_config
from test_data.shared.mesh_payload import create_mesh_payload
from test_data.shared.system_payload import create_system_payload
from test_data.shared.source_payload import create_source_payload
from test_data.shared.object_payload import create_object_payload, configure_object_payload
from test_data.shared.product_payload import create_product_payload
from test_data.shared.connection_source_payload import create_connection_source_payload
from test_data.shared.schema_product_payload import schema_product_create_payload


load_dotenv()

landscape_config = load_config("test_data/landscapes/landscape-4.yml")

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
USERNAME = os.getenv("QA_USERNAME", "")
PASSWORD = os.getenv("QA_PASSWORD", "")
X_ACCOUNT = os.getenv("X_ACCOUNT", "")



@pytest.fixture(scope="session")
def api_context(playwright: Playwright):
    """Create API request context and get access token"""
    context = playwright.request.new_context(base_url=BASE_URL)
    login_payload = {"user": USERNAME, "password": PASSWORD}
    access_token = None
    try:
        response = context.post("/api/iam/login", data=json.dumps(login_payload), headers={"Content-Type": "application/json"})
        access_token = response.json().get("access_token")
    except PlaywrightTimeoutError:
        context.dispose()
        access_token = None
    except Exception as e:
        context.dispose()
        access_token = None

    yield context, access_token
    context.dispose()


@pytest.fixture(scope="session")
def id_map():
    return []


def register_entity(id_map, entity):
    id_map.append(entity)


def find_entity(id_map, entity_id):
    return next((item for item in id_map if item['id'] == entity_id), None)


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "x-account": X_ACCOUNT,
        "Content-Type": "application/json"
    }

def skip_if_no_token(access_token):
    if not access_token:
        pytest.skip("Skipping test: Access token not found")


def record_api_info(request, method, url, payload, response):
    request.node._api_info = {
        "method": method,
        "url": url,
        "payload": payload,
        "response": response.json() if response else None
    }


def assert_success_response(response):
    try:
        if not response.ok:
            text = response.text()
            pytest.fail(f"Request failed: {response.status} - {text}")
    except Exception as e:
        pytest.fail(f"Request failed: {e}")


def assert_entity_created(response):
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
    context, access_token = api_context
    if not access_token:
        request.node._api_info = {
            "method": "POST",
            "url": "/api/iam/login",
            "payload": {"user": USERNAME, "password": PASSWORD},
            "response": "Login failed - no access token"
        }
        pytest.fail("Login failed - no access token")
    else:
        request.node._api_info = {
            "method": "POST",
            "url": "/api/iam/login",
            "payload": {"user": USERNAME, "password": PASSWORD},
            "response": "Login successful"
        }
        assert access_token is not None

@pytest.mark.parametrize("mesh", landscape_config["mesh"], ids=[m["id"] for m in landscape_config["mesh"]])
def test_create_mesh(api_context, id_map, request, mesh):
    context, access_token = api_context
    skip_if_no_token(access_token)
    payload = create_mesh_payload(mesh.get("name"))
    response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
    record_api_info(request, "POST", "/api/data/mesh", payload, response)
    mesh_id = assert_entity_created(response)
    print(mesh_id)
    register_entity(id_map, {
        "id": mesh["id"],
        "identifier": mesh_id,
        "type": "mesh"
    })

@pytest.mark.parametrize("system", landscape_config["systems"], ids=[s["id"] for s in landscape_config["systems"]])
def test_create_system(api_context, id_map, request, system):
    context, access_token = api_context
    skip_if_no_token(access_token)
    payload = create_system_payload(system.get("name"))
    response = context.post('/api/data/data_system', data=json.dumps(payload), headers=get_headers(access_token))
    record_api_info(request, "POST", "/api/data/data_system", payload, response)
    system_id = response.json()['identifier']
    assert system_id is not None, "System ID is missing"
    register_entity(id_map, {
        "id": system["id"],
        "identifier": system_id,
        "type": "system"
    })

@pytest.mark.parametrize("source", landscape_config["sources"], ids=[s["id"] for s in landscape_config["sources"]])
def test_create_source(api_context, id_map, request, source):
    context, access_token = api_context
    skip_if_no_token(access_token)
    payload = create_source_payload(source.get("name"))
    response = context.post('/api/data/origin', data=json.dumps(payload), headers=get_headers(access_token))
    record_api_info(request, "POST", "/api/data/origin", payload, response)
    source_id = assert_entity_created(response)
    register_entity(id_map, {
        "id": source["id"],
        "identifier": source_id,
        "type": "source"
    })

@pytest.mark.parametrize("source", landscape_config["sources"], ids=[f"{source['system']} to {source['id']}" for source in landscape_config["sources"]])
def test_link_system_to_source(api_context, id_map, request, source):
    context, access_token = api_context
    skip_if_no_token(access_token)
    source_entity = find_entity(id_map, source["id"])
    system_entity = find_entity(id_map, source["system"])
    print("identifier:", system_entity["identifier"])
    print("child_identifier:", source_entity["identifier"])
    if source_entity and system_entity:
        params = {
            "identifier": system_entity["identifier"],
            "child_identifier": source_entity["identifier"],
        }
        response = context.post(
            '/api/data/link/data_system/origin',
            params=params,
            headers=get_headers(access_token)
        )
        record_api_info(request, "POST", "/api/data/link/data_system/origin", params, response)
        assert_success_response(response)


@pytest.mark.parametrize("source", landscape_config["sources"], ids=[f"{source['id']}" for source in landscape_config["sources"]])
def test_configure_connection_details(api_context, id_map, request, source):
    context, access_token = api_context
    skip_if_no_token(access_token)
    source_entity = find_entity(id_map, source["id"])
    if source_entity:
        payload = create_connection_source_payload()
        url = f'/api/data/origin/connection?identifier={source_entity["identifier"]}'
        response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "PUT", url, payload, response)
        assert_success_response(response)

@pytest.mark.parametrize("source", landscape_config["sources"], ids=[f"{source['id']}" for source in landscape_config["sources"]])
def test_set_connection_secrets(api_context, id_map, request, source):
    context, access_token = api_context
    skip_if_no_token(access_token)
    source_entity = find_entity(id_map, source["id"])
    if source_entity:
        payload = {
            "access_key": os.getenv("S3_ACCESS_KEY", ""),
            "access_secret": os.getenv("S3_SECRET_KEY", ""),
        }
        url = f'/api/data/origin/secret?identifier={source_entity["identifier"]}'
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "POST", url, payload, response)
        assert_success_response(response)

@pytest.mark.parametrize("object", landscape_config["objects"], ids=[o["id"] for o in landscape_config["objects"]])
def test_create_object(api_context, id_map, request, object):
    context, access_token = api_context
    skip_if_no_token(access_token)
    payload = create_object_payload(object.get("name"))
    response = context.post('/api/data/resource', data=json.dumps(payload), headers=get_headers(access_token))
    record_api_info(request, "POST", "/api/data/resource", payload, response)
    object_id = assert_entity_created(response)
    register_entity(id_map, {
        "id": object["id"],
        "identifier": object_id,
        "type": "object"
    })

@pytest.mark.parametrize("object", landscape_config["objects"], ids=[f"{object['source']} to {object['id']}" for object in landscape_config["objects"]])
def test_link_object_to_source(api_context, id_map, request, object):
    context, access_token = api_context
    skip_if_no_token(access_token)
    object_entity = find_entity(id_map, object["id"])
    source_entity = find_entity(id_map, object["source"])
    if object_entity and source_entity:
        params = {
            "identifier": source_entity["identifier"],
            "child_identifier": object_entity["identifier"],
        }
        response = context.post('/api/data/link/origin/resource', params=params, headers=get_headers(access_token))
        record_api_info(request, "POST", "/api/data/link/origin/resource", params, response)
        assert_success_response(response)

@pytest.mark.parametrize("object", landscape_config["objects"], ids=[f"{object['id']}" for object in landscape_config["objects"]])
def test_configure_object_details(api_context, id_map, request, object):
    context, access_token = api_context
    skip_if_no_token(access_token)
    object_entity = find_entity(id_map, object["id"])
    if object_entity:
        payload = configure_object_payload()
        url = f'/api/data/resource/config?identifier={object_entity["identifier"]}'
        response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "PUT", url, payload, response)
        assert_success_response(response)

@pytest.mark.parametrize("product", landscape_config["products"], ids=[product["id"] for product in landscape_config["products"]])
def test_create_product(api_context, id_map, request, product):
    context, access_token = api_context
    skip_if_no_token(access_token)
    mesh = find_entity(id_map, product["mesh"])
    payload = create_product_payload(mesh["identifier"], product.get("name"))
    response = context.post('/api/data/product', data=json.dumps(payload), headers=get_headers(access_token))
    record_api_info(request, "POST", "/api/data/product", payload, response)
    product_id = assert_entity_created(response)
    register_entity(id_map, {
        "id": product["id"],
        "identifier": product_id,
        "type": "product"
    })


@pytest.mark.parametrize("product", landscape_config["products"], ids=[f"{product['id']}" for product in landscape_config["products"]])
def test_link_inputs_to_product(api_context, id_map, request, product):
    context, access_token = api_context
    skip_if_no_token(access_token)
    product_entity = find_entity(id_map, product["id"])
    for input in product["input"]:
        entity = find_entity(id_map, input)
        if entity and product_entity:
            if "obj" in input:
                params = {
                    "identifier": entity["identifier"],
                    "child_identifier": product_entity["identifier"],
                }
                response = context.post('/api/data/link/resource/product', params = params, headers=get_headers(access_token))
                record_api_info(request, "POST", "/api/data/link/resource/product", params, response)
                assert_success_response(response)
            elif "prod" in input:
                params = {
                    "identifier": entity["identifier"],
                    "child_identifier": product_entity["identifier"],
                }
                response = context.post('/api/data/link/product/product', params = params, headers=get_headers(access_token))
                record_api_info(request, "POST", "/api/data/link/product/product", params, response)
                assert_success_response(response)

@pytest.mark.parametrize("product", landscape_config["products"], ids=[f"{product['id']}" for product in landscape_config["products"]])
def test_create_data_product_schema(api_context, id_map, request, product):
    context, access_token = api_context
    skip_if_no_token(access_token)
    product_entity = find_entity(id_map, product["id"])
    if product_entity:
        payload = schema_product_create_payload()
        url = f'/api/data/product/schema?identifier={product_entity["identifier"]}'
        response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(request, "PUT", url, payload, response)
        assert_success_response(response)
