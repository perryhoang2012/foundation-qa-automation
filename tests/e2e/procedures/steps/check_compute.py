import json
import time

import pytest
from api.check_compute import check_status_compute
from api.source import get_source_by_id
from api.product import get_product_by_id
from api.object import get_object_by_id
from config.status_check_compute import StatusCheckCompute
from steps.procedure import ProcedureStep
from utils.common import assert_success_response, find_entity, skip_if_no_token


class CheckStatusComputeStep(ProcedureStep):
    """Step to check the status of a compute."""

    def execute(self) -> None:
        DEFAULT_NUM_RETRIES = 5
        DEFAULT_DELAY_SECONDS = 60

        """Execute compute status checking step with retry logic."""
        MAX_RETRIES = self.step.get("max_retries", DEFAULT_NUM_RETRIES)
        DELAY_SECONDS = self.step.get("retry_interval", DEFAULT_DELAY_SECONDS)

        context, access_token = self.api_context
        skip_if_no_token(access_token)
        print(json.dumps(self.id_map, indent=4))

        entity = find_entity(self.id_map, self.step["ref"])
        if entity is None:
            pytest.fail("Entity not found")

        if entity.get("type") == "product":
            compute_identifier = entity.get("compute", {}).get("identifier")
        else:
            compute_identifier = entity.get("compute_identifier")
        healthy = entity.get("healthy")

        if compute_identifier is None:
            pytest.fail("Compute identifier not found")

        time.sleep(DELAY_SECONDS)
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

            if status.get("status") == StatusCheckCompute.COMPLETED.value:
                print("[CheckStatusComputeStep] Compute completed successfully.")
                return

            if attempt < MAX_RETRIES:
                print(
                    f"[CheckStatusComputeStep] Not completed yet. Retrying in {DELAY_SECONDS} seconds..."
                )
                time.sleep(DELAY_SECONDS)
            else:
                pytest.fail("Compute failed after retries")