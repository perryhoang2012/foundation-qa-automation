import json
from typing import Any, Dict

def attach_api_details(test_info, details: Dict[str, Any]) -> None:
    endpoint = details["endpoint"]
    method = details.get("method", "POST")
    payload = details["payload"]
    response = details["response"]

    test_info.attach(
        "api-request",
        body=json.dumps({"endpoint": endpoint, "method": method, "payload": payload}, indent=2).encode("utf-8"),
        content_type="application/json",
    )

    test_info.attach(
        "api-response",
        body=json.dumps(response, indent=2).encode("utf-8"),
        content_type="application/json",
    )
