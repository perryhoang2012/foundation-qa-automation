#!/usr/bin/env python3
"""
Test runner for mocked API tests.

This script demonstrates how to run the mocked API tests
without requiring a real server.
"""

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run the mocked API tests."""
    print("🚀 Starting mocked API tests...")
    print("=" * 50)

    # Set environment variables for testing
    os.environ.setdefault("API_URL", "http://localhost:8000")
    os.environ.setdefault("QA_USERNAME", "test_user")
    os.environ.setdefault("QA_PASSWORD", "test_password")

    # Run the specific test file
    test_args = [
        "tests/test_procedures_generator_by_verlora_mock.py",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "-s",  # Show print statements
    ]

    print(f"Running tests with args: {' '.join(test_args)}")
    print("=" * 50)

    # Run pytest
    exit_code = pytest.main(test_args)

    print("=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
