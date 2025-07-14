import pytest
import os
import sys
import json
from types import FunctionType
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_data.velora.product_transformation_payload import create_transformation_builder_payload_with_inputs

from utils.load_config import load_config
from utils.common import register_entity, find_entity, get_headers, record_api_info


import importlib.util
spec = importlib.util.spec_from_file_location("procedure_config", "test_data/procedures_temp/procedure-2.py")
procedure_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(procedure_config)
config = procedure_config.config

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

@pytest.fixture(scope="session")
def id_map():
    return {}


def skip_if_no_token(access_token):
    if not access_token:
        pytest.skip("Skipping test: Access token not found")

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


class ProcedureStep:
    def __init__(self, request, step, api_context, id_map):
        self.request = request
        self.step = step
        self.api_context = api_context
        self.id_map = id_map
    def execute(self):
        raise NotImplementedError("Subclasses must override this method")

class CreateMeshStep(ProcedureStep):
    def execute(self):
        print("▶️ create_mesh_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        url = f"/api/data/mesh"
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create mesh not found")
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.request, "POST", url, payload, response)
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
        url = f"/api/data/data_system"
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create system not found")
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.request, "POST", url, payload, response)
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
        url = f"/api/data/origin"
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create source not found")
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.request, "POST", url, payload, response)
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
        url = f"/api/data/resource"
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create object not found")
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.request, "POST", url, payload, response)
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
        url = f"/api/data/link/origin/resource"
        source_entity = None
        object_entity = None
        if("input" in self.step):
            if(self.step["input"].get("source_ref")):
                source_entity = find_entity(self.id_map, self.step["input"].get("source_ref"))
            if(self.step["input"].get("object_ref")):
                object_entity = find_entity(self.id_map, self.step["input"].get("object_ref"))
            if object_entity and source_entity:
                params = {
                    "identifier": source_entity["identifier"],
                    "child_identifier": object_entity["identifier"],
                }
                response = context.post(url, params=params, headers=get_headers(access_token))
                record_api_info(self.request, "POST", url, params, response)
                assert_success_response(response)
            else:
                pytest.fail("object or source not found")
        else:
            pytest.fail("input not found")

class ConfigureObjectDetailsStep(ProcedureStep):
    def execute(self):
        print("▶️ configure_object_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        object_entity = find_entity(self.id_map, self.step["ref"])
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input configure object details not found")
        if object_entity:
            url = f'/api/data/resource/config?identifier={object_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.request, "PUT", url, payload, response)
            assert_success_response(response)
        else:
            pytest.fail("object not found")


class CreateProductStep(ProcedureStep):
    def execute(self):
        print("▶️ create_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        mesh = None
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create product not found")

        if(self.step.get("mesh_ref")):
                mesh = find_entity(self.id_map, self.step["mesh_ref"])
                payload["host_mesh_identifier"] = mesh["identifier"]
        url = f'/api/data/product'
        response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
        record_api_info(self.request, "POST", url, payload, response)
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
        url = f"/api/data/link/resource/product"
        if("input" in self.step):
            if(self.step["input"].get("object_ref")):
                object_entity = find_entity(self.id_map, self.step["input"].get("object_ref"))
            if(self.step["input"].get("product_ref")):
                product_entity = find_entity(self.id_map, self.step["input"].get("product_ref"))
            if object_entity and product_entity:
                params = {
                    "identifier": object_entity["identifier"],
                    "child_identifier": product_entity["identifier"],
                }
                url = f"/api/data/link/resource/product"
                response = context.post(url, params = params, headers=get_headers(access_token))
                record_api_info(self.request, "POST", url, params, response)
                assert_success_response(response)
            else:
                pytest.fail("object or product not found")
        else:
            pytest.fail("input link product to object not found")

class LinkProductToProductStep(ProcedureStep):
    def execute(self):
        print("▶️ link_product_to_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        if("input" in self.step):
            if(self.step["input"].get("product_ref")):
                product_entity = find_entity(self.id_map, self.step["input"].get("product_ref"))
            if(self.step["input"].get("product_child_ref")):
                product_child_entity = find_entity(self.id_map, self.step["input"].get("product_child_ref"))
            if product_entity and product_child_entity:
                params = {
                    "identifier": product_entity["identifier"],
                    "child_identifier": product_child_entity["identifier"],
                }
                url = f"/api/data/link/product/product"
                response = context.post(url, params = params, headers=get_headers(access_token))
                record_api_info(self.request, "POST", url, params, response)
                assert_success_response(response)
            else:
                pytest.fail("product or product child not found")
        else:
            pytest.fail("input link product to product not found")

class CreateDataProductSchemaStep(ProcedureStep):
    def execute(self):
        print("▶️ create_data_product_schema_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        product_entity = find_entity(self.id_map, self.step["ref"])
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input create data product schema not found")
        if product_entity:
            url = f'/api/data/product/schema?identifier={product_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.request, "PUT", url, payload, response)
            assert_success_response(response)
        else:
            pytest.fail("product not found")

class LinkSystemToSourceStep(ProcedureStep):
    def execute(self):
        print("▶️ link_system_to_source_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        url = f"/api/data/link/data_system/origin"
        if "input" in self.step:
            if(self.step["input"].get("system_ref")):
                system_entity = find_entity(self.id_map, self.step["input"].get("system_ref"))
            if(self.step["input"].get("source_ref")):
                source_entity = find_entity(self.id_map, self.step["input"].get("source_ref"))
        if source_entity and system_entity:
            params = {
                "identifier": system_entity["identifier"],
                "child_identifier": source_entity["identifier"],
            }
            response = context.post(
                url,
                params=params,
                headers=get_headers(access_token)
            )
            record_api_info(self.request, "POST", url, params, response)
            assert_success_response(response)
        else:
            pytest.fail("source or system not found")

class ConfigureConnectionDetailsStep(ProcedureStep):
    def execute(self):
        print("▶️ configure_connection_details_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["ref"])
        if("input" in self.step):
            payload = self.step["input"]
        else:
            pytest.fail("input configure connection details not found")
        if source_entity:
            url = f'/api/data/origin/connection?identifier={source_entity["identifier"]}'
            response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
            record_api_info(self.request, "PUT", url, payload, response)
            assert_success_response(response)
        else:
            pytest.fail("source not found")

class SetConnectionSecretsStep(ProcedureStep):
    def execute(self):
        print("▶️ set_connection_secrets_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        source_entity = find_entity(self.id_map, self.step["ref"])
        if "input" in self.step:
            if source_entity:
                payload = self.step["input"]
                url = f'/api/data/origin/secret?identifier={source_entity["identifier"]}'
                response = context.post(url, data=json.dumps(payload), headers=get_headers(access_token))
                record_api_info(self.request, "POST", url, payload, response)
                assert_success_response(response)
            else:
                pytest.fail("source not found")
        else:
            pytest.fail("input set connection secrets not found")

class CreateTransformationBuilderStep(ProcedureStep):
    def execute(self):
        print("▶️ create_transformation_builder_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        if("input" in self.step):
            if(self.step["input"].get("product_ref")):
                product_entity = find_entity(self.id_map, self.step["input"].get("product_ref"))
            if(self.step["input"].get("input_refs")):
                input_entities = []
                for input_ref in self.step["input"].get("input_refs"):
                    input_entity = find_entity(self.id_map, input_ref)
                    if input_entity:
                        input_entities.append(input_entity)
                    else:
                        pytest.fail(f"input {input_ref} not found")
                if input_entities:
                    payload = create_transformation_builder_payload_with_inputs(input_entities)
                    print('payload', json.dumps(payload, indent=2))
                else:
                    pytest.fail("input entities not found")
            else:
                pytest.fail("input input_refs not found")
            if product_entity:
                url = f'/api/data/product/compute/builder?identifier={product_entity["identifier"]}'
                response = context.put(url, data=json.dumps(payload), headers=get_headers(access_token))
                record_api_info(self.request, "PUT", url, payload, response)
                assert_success_response(response)
            else:
                 pytest.fail("product not found")


def get_step_instance(request, step, api_context, id_map):
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
    }
    if step_type not in mapping:
        raise ValueError(f"Unknown step type: {step_type}")
    return mapping[step_type](request, step, api_context, id_map)



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



@pytest.mark.parametrize("step", config.get("steps", []), ids=lambda x: f"Step {config.get('steps', []).index(x) + 1}: {x['type']}_{x.get('id') or x.get('identifier') or ''}")
def test_step_execution(request, step, api_context, id_map):
    get_step_instance(request, step, api_context, id_map).execute()



