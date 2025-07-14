# conftest.py
import json
import requests
import pytest
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# base_url = os.getenv("API_URL", "http://localhost:8000")
# username = os.getenv("QA_USERNAME", "")
# password = os.getenv("QA_PASSWORD", "")

WEBHOOK_URL = os.getenv("WEB_HOOK_GLUE", "")
TARGET_WEBHOOK = os.getenv("ID_GROUP_GLUE", "")

# @pytest.fixture(scope="session")
# def login_session_token(playwright):
#     context = playwright.request.new_context(base_url=base_url)
#     payload = {"user": username, "password": password}

#     try:
#         response = context.post("/api/iam/login", data=payload)
#         body = response.json()
#         return {
#             "token": body["access_token"],
#             "response": body,
#             "status": response.status,
#             "context": context,
#             "payload": payload
#         }
#     except Exception as e:
#         pytest.exit(f"Login failed: {e}")

# @pytest.fixture(scope="function")
# def ensure_login(request, login_session_token):
#     request.node._api_info = {
#         "method": "POST",
#         "url": "/api/iam/login",
#         "payload": login_session_token["payload"],
#         "response": {
#             "status": login_session_token["status"],
#             "body": login_session_token["response"]
#         }
#     }
#     return login_session_token


def pytest_sessionstart(session):
    session.results = {
        "start_time": datetime.now(),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "total": 0,
        "duration": 0,
        "failures": []
    }

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        results = item.session.results
        results["total"] += 1
        results["duration"] += rep.duration

        if rep.passed:
            results["passed"] += 1

        elif rep.failed:
            results["failed"] += 1

            api_info = getattr(item, "_api_info", {})

            results["failures"].append({
                "method": api_info.get("method", "UNKNOWN"),
                "url": api_info.get("url", "UNKNOWN"),
                "payload": api_info.get("payload", {}),
                "response": api_info.get("response", None),
            })

        elif rep.skipped:
            results["skipped"] += 1

def pytest_sessionfinish(session, exitstatus):
    results = session.results
    end_time = datetime.now()
    start_time = results["start_time"]

    summary = (
        f"✅ **Test Summary**\n"
        f"- 🕒 Start Time: {start_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"- 🕓 End Time:   {end_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"- Total: {results['total']}\n"
        f"- ✅ Passed: {results['passed']}\n"
        f"- ❌ Failed: {results['failed']}\n"
        f"- ⚠️ Skipped: {results['skipped']}\n"
        f"- ⏱ Duration: {round(results['duration'], 2)}s"
    )

    if results["failures"]:
        summary += "\n\n🚨 **Failures Details:**\n"
        for i, fail in enumerate(results["failures"], 1):
            summary += f"\n--- ❌ **Failure {i}** ---\n"
            summary += f"\n📡 **API Called:** `{fail['method']} {fail['url']}`\n"
            summary += f"\n📦 **Payload:** `\n{fail['payload']}\n`\n"
            if fail.get("response"):
                summary += f"\n📥 **Response:** `\n{fail['response']}\n`\n"

    payload = {
        "text": summary,
        "target": TARGET_WEBHOOK
    }


    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        res.raise_for_status()
        print("📤 Webhook sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")
