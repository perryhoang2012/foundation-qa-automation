import json
import pytest
from api.product import (
    create_data_product_schema,
    create_product,
    create_transformation_builder,
    delete_product,
    get_all_product,
    get_product_by_id,
    link_product_to_object,
    link_product_to_product,
)
from steps.procedure import ProcedureStep
from test_data.velora.product_transformation_payload import (
    create_transformation_builder_payload_with_inputs,
)
from utils.common import (
    assert_entity_created,
    assert_success_response,
    find_entity,
    register_entity,
    skip_if_no_token,
)


class GetAllProductStep(ProcedureStep):
    """Step to get all product entities."""

    def execute(self) -> None:
        """Execute product retrieval step."""
        print("▶️ get_all_product_logic", self.step)
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        response = get_all_product(context, access_token, self.request)


class GetProductByIdStep(ProcedureStep):
    """Step to get a product entity by its identifier."""

    def execute(self) -> None:
        """Execute product retrieval step."""
        context, access_token = self.api_context
        skip_if_no_token(access_token)

        product_ref = self.step.get("input", {}).get("product_ref")
        if not product_ref:
            pytest.fail("Missing required input: 'product_ref'.")

        product_entry = self.id_map.get(product_ref)
        if not product_entry or "identifier" not in product_entry:
            pytest.fail(f"'product_ref' '{product_ref}' not found in id_map.")

        product_id = product_entry["identifier"]
        response = get_product_by_id(context, product_id, access_token, self.request)
        response_data = response.json()
        entity = response_data.get("entity")

        if not entity or "identifier" not in entity:
            pytest.fail("Invalid response: missing 'entity' or 'identifier' field.")

        register_entity(
            self.id_map,
            {
                **response_data,
                "id": product_ref,
            },
        )


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


class DeleteProductStep(ProcedureStep):
    """Step to delete a product entity."""

    def execute(self) -> None:
        """Execute product deletion step."""
        print("▶️ delete_product_logic", self.step)

        context, access_token = self.api_context
        skip_if_no_token(access_token)

        product_ref = self.step.get("input", {}).get("product_ref")
        if not product_ref:
            pytest.fail("Product reference ('product_ref') is required for deletion.")

        product_entry = self.id_map.get(product_ref)
        if not product_entry or "identifier" not in product_entry:
            pytest.fail("Product reference ('product_ref') not found in id_map.")
        product_id = product_entry["identifier"]

        response = delete_product(context, product_id, access_token, self.request)


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
