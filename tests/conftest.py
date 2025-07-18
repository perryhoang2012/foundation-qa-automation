"""
Pytest configuration and test session management.

This module provides pytest hooks for test session management,
result tracking, and webhook notifications.
"""

import os
from datetime import datetime
from typing import Any, Dict, List

import pytest
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Environment variables
WEBHOOK_URL = os.getenv("WEB_HOOK_GLUE", "")
TARGET_WEBHOOK = os.getenv("ID_GROUP_GLUE", "")


def pytest_sessionstart(session: pytest.Session) -> None:
    """
    Initialize test session results tracking.

    Args:
        session: The pytest session object
    """
    session.results = {  # type: ignore
        "start_time": datetime.now(),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "total": 0,
        "duration": 0,
        "failures": [],
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """
    Track test results and API information for failed tests.

    Args:
        item: The test item being executed
        call: The call information

    Yields:
        The test report
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        results = item.session.results  # type: ignore
        results["total"] += 1
        results["duration"] += rep.duration

        if rep.passed:
            results["passed"] += 1
        elif rep.failed:
            results["failed"] += 1

            # Get API information from test item
            api_info = getattr(item, "_api_info", {})

            results["failures"].append(
                {
                    "method": api_info.get("method", "UNKNOWN"),
                    "url": api_info.get("url", "UNKNOWN"),
                    "payload": api_info.get("payload", {}),
                    "response": api_info.get("response", None),
                }
            )
        elif rep.skipped:
            results["skipped"] += 1


def pytest_sessionfinish(session: pytest.Session, exitstatus: pytest.ExitCode) -> None:
    """
    Generate test summary and send webhook notification.

    Args:
        session: The pytest session object
        exitstatus: The exit status of the test session
    """
    results = session.results  # type: ignore
    end_time = datetime.now()
    start_time = results["start_time"]

    # Generate test summary
    summary = _generate_test_summary(results, start_time, end_time)

    # Prepare webhook payload
    payload = {"text": summary, "target": TARGET_WEBHOOK}

    # Send webhook notification (commented out for now)
    _send_webhook_notification(payload)


def _generate_test_summary(
    results: Dict[str, Any], start_time: datetime, end_time: datetime
) -> str:
    """
    Generate a formatted test summary.

    Args:
        results: Test session results
        start_time: Session start time
        end_time: Session end time

    Returns:
        Formatted test summary string
    """
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

    # Add failure details if any
    if results["failures"]:
        summary += "\n\n🚨 **Failures Details:**\n"
        for i, failure in enumerate(results["failures"], 1):
            summary += _format_failure_details(i, failure)

    return summary


def _format_failure_details(failure_index: int, failure: Dict[str, Any]) -> str:
    """
    Format failure details for webhook message.

    Args:
        failure_index: The index of the failure
        failure: Failure information dictionary

    Returns:
        Formatted failure details string
    """
    details = f"\n--- ❌ **Failure {failure_index}** ---\n"
    details += f"\n📡 **API Called:** `{failure['method']} {failure['url']}`\n"
    details += f"\n📦 **Payload:** `\n{failure['payload']}\n`\n"

    if failure.get("response"):
        details += f"\n📥 **Response:** `\n{failure['response']}\n`\n"

    return details


def _send_webhook_notification(payload: Dict[str, Any]) -> None:
    """
    Send webhook notification (currently disabled).

    Args:
        payload: The webhook payload to send
    """
    if not WEBHOOK_URL:
        print("⚠️ Webhook URL not configured, skipping notification.")
        return

    try:

        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("📤 Webhook sent successfully.")
    except ImportError:
        print("❌ Requests library not available, cannot send webhook.")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")
