import pytest
import os
import sys
import json
from types import FunctionType
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_config import load_config
from test_data.shared.mesh_payload import create_mesh_payload
from test_data.shared.system_payload import create_system_payload

config = load_config("test_data/procedures/procedures-1.yml")

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
USERNAME = os.getenv("QA_USERNAME", "")
PASSWORD = os.getenv("QA_PASSWORD", "")
X_ACCOUNT = os.getenv("X_ACCOUNT", "")


if config is None:
    config = {}

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

@pytest.fixture
def id_map():
    return {}

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


@pytest.fixture
def req_context():
    return {"user": "tester", "env": "test"}


class ProcedureStep:
    def __init__(self, id_map, req_context, step, api_context):
        self.id_map = id_map
        self.req_context = req_context
        self.step = step
        self.api_context = api_context

    def execute(self):
        raise NotImplementedError("Subclasses phải override method này")

class CreateMeshStep(ProcedureStep):
    def execute(self):
        print("▶️ create_mesh_logic", self.step, self.api_context )
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        payload = create_mesh_payload(self.step.get("name"))
        response = context.post('/api/data/mesh', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.req_context, "POST", "/api/data/mesh", payload, response)
        mesh_id = assert_entity_created(response)
        register_entity(self.id_map, {
            "id": self.step["id"],
            "identifier": mesh_id,
            "type": "mesh"
        })

class CreateSystemStep(ProcedureStep):
    def execute(self):
        print("▶️ create_system_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        payload = create_system_payload(self.step.get("name"))
        response = context.post('/api/data/data_system', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.req_context, "POST", "/api/data/data_system", payload, response)
        system_id = response.json()['identifier']
        assert system_id is not None, "System ID is missing"
        register_entity(self.id_map, {
            "id": self.step["id"],
            "identifier": system_id,
            "type": "system"
        })

class CreateSourceStep(ProcedureStep):
    def execute(self):
        print("▶️ create_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        payload = create_source_payload(self.step.get("name"))
        response = context.post('/api/data/origin', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.req_context, "POST", "/api/data/origin", payload, response)
        source_id = assert_entity_created(response)
        register_entity(self.id_map, {
            "id": self.step["id"],
            "identifier": source_id,
            "type": "source"
        })

class CreateObjectStep(ProcedureStep):
    def execute(self):
        print("▶️ create_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        payload = create_object_payload(self.step.get("name"))
        response = context.post('/api/data/resource', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.req_context, "POST", "/api/data/resource", payload, response)
        object_id = assert_entity_created(response)
        register_entity(self.id_map, {
            "id": self.step["id"],
            "identifier": object_id,
            "type": "object"
        })

class LinkObjectToSourceStep(ProcedureStep):
    def execute(self):
        print("▶️ link_object_to_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["identifier"])
        object_entity = find_entity(self.id_map, self.step["child_identifier"])
        if object_entity and source_entity:
            params = {
                "identifier": source_entity["identifier"],
                "child_identifier": object_entity["identifier"],
            }
            response = context.post('/api/data/link/origin/resource', params=params, headers=get_headers(access_token))
            record_api_info(self.req_context, "POST", "/api/data/link/origin/resource", params, response)
            assert_success_response(response)

class ConfigureObjectDetailsStep(ProcedureStep):
    def execute(self):
        print("▶️ configure_object_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        object_entity = find_entity(self.id_map, self.step["identifier"])
        if object_entity:
            payload = configure_object_payload()
            url = f'/api/data/resource/config?identifier={object_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.req_context, "PUT", url, payload, response)
            assert_success_response(response)

class CreateProductStep(ProcedureStep):
    def execute(self):
        print("▶️ create_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        mesh = find_entity(self.id_map, self.step["mesh"])
        payload = create_product_payload(mesh["identifier"], self.step.get("name"))
        response = context.post('/api/data/product', data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.req_context, "POST", "/api/data/product", payload, response)
        product_id = assert_entity_created(response)
        register_entity(self.id_map, {
            "id": self.step["id"],
            "identifier": product_id,
            "type": "product"
        })

class LinkProductToObjectStep(ProcedureStep):
    def execute(self):
        print("▶️ link_product_to_object_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        object_entity = find_entity(self.id_map, self.step["identifier"])
        product_entity = find_entity(self.id_map, self.step["child_identifier"])
        if object_entity and source_entity:
            params = {
                "identifier": object_entity["identifier"],
                "child_identifier": product_entity["identifier"],
            }
            response = context.post('/api/data/link/resource/product', params = params, headers=get_headers(access_token))
            record_api_info(self.req_context, "POST", "/api/data/link/resource/product", params, response)
            assert_success_response(response)

class LinkProductToProductStep(ProcedureStep):
    def execute(self):
        print("▶️ link_product_to_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        product_entity = find_entity(self.id_map, self.step["identifier"])
        product_child_entity = find_entity(self.id_map, self.step["child_identifier"])
        if object_entity and source_entity:
            params = {
                "identifier": product_entity["identifier"],
                "child_identifier": product_child_entity["identifier"],
            }
            response = context.post('/api/data/link/product/product', params = params, headers=get_headers(access_token))
            record_api_info(self.req_context, "POST", "/api/data/link/product/product", params, response)
            assert_success_response(response)

class CreateDataProductSchemaStep(ProcedureStep):
    def execute(self):
        print("▶️ create_data_product_schema_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        product_entity = find_entity(self.id_map, self.step["identifier"])
        if product_entity:
            payload = schema_product_create_payload()
            url = f'/api/data/product/schema?identifier={product_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.req_context, "PUT", url, payload, response)
            assert_success_response(response)

class LinkSystemToSourceStep(ProcedureStep):
    def execute(self):
        print("▶️ link_system_to_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["identifier"])
        system_entity = find_entity(self.id_map, self.step["child_identifier"])
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
            record_api_info(self.req_context, "POST", "/api/data/link/data_system/origin", params, response)
            assert_success_response(response)

class ConfigureConnectionDetailsStep(ProcedureStep):
    def execute(self):
        print("▶️ configure_connection_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["identifier"])
        if source_entity:
            payload = create_connection_source_payload()
            url = f'/api/data/origin/connection?identifier={source_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.req_context, "PUT", url, payload, response)
            assert_success_response(response)

class SetConnectionSecretsStep(ProcedureStep):
    def execute(self):
        print("▶️ set_connection_secrets_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["identifier"])
        if source_entity:
            payload = {
                "access_key": os.getenv("S3_ACCESS_KEY", ""),
                "access_secret": os.getenv("S3_SECRET_KEY", ""),
            }
            url = f'/api/data/origin/secret?identifier={source_entity["identifier"]}'
            response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.req_context, "POST", url, payload, response)
            assert_success_response(response)

# ---------------------------
# Phần 2: Hàm lấy instance lớp tương ứng với step type

def get_step_instance(step, api_context, id_map, req_context):
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
        "create_data_product_schema": CreateDataProductSchemaStep,
        "link_system_to_source": LinkSystemToSourceStep,
        "configure_connection_details": ConfigureConnectionDetailsStep,
        "set_connection_secrets": SetConnectionSecretsStep,
    }
    if step_type not in mapping:
        raise ValueError(f"Unknown step type: {step_type}")
    return mapping[step_type](id_map, req_context, step, api_context)


def execute_procedure(step,api_context, req_context, id_map):
    if not isinstance(step, dict):
        raise TypeError("Step must be a dict")
    if "type" not in step:
        raise KeyError("Step missing 'type'")

    instance = get_step_instance(step, api_context, id_map, req_context)
    return instance.execute()



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


def generate_test_function(step):
    def func(id_map, req_context, api_context):
        execute_procedure(step, api_context, req_context, id_map)
    return func

for idx, step in enumerate(config.get("steps", [])):
    step_type = step.get("type")
    step_id = step.get("id") or step.get("identifier") or f"step{idx+1}"
    test_name = f"test_{step_type}_{step_id}".replace("-", "_")


    func = generate_test_function(step)
    globals()[test_name] = func



