import json
import time

import pytest
from api.check_compute import check_status_compute
from api.source import get_source_by_id
from api.product import get_product_by_id
from api.object import get_object_by_id
from constants.status_check_compute import StatusCheckCompute
from steps.procedure import ProcedureStep
from utils.common import assert_success_response, find_entity, skip_if_no_token


class CheckStatusComputeStep(ProcedureStep):
    """Step to check the status of a compute."""

    def execute(self) -> None:
        """Execute compute status checking step with retry logic."""
        context, access_token = self.api_context
        skip_if_no_token(access_token)
        time.sleep(60)

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

            if healthy and status == StatusCheckCompute.COMPLETED:
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
