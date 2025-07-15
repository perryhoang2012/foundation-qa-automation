"""
Mock configuration for API testing.

This module provides mock responses and configurations for testing
API endpoints without requiring a real server.
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock


class MockResponse:
    """Mock response class for API testing."""

    def __init__(self, status_code=200, json_data=None, text_data=None, ok=True):
        self.status_code = status_code
        self.status = status_code
        self._json_data = json_data or {}
        self._text_data = text_data or ""
        self.ok = ok

    def json(self):
        return self._json_data

    def text(self):
        return self._text_data


class MockAPIConfig:
    """Configuration class for API mocking."""

    def __init__(self):
        self.entity_counter = 0
        self.access_token = "mock_access_token_12345"
        self.base_url = "http://localhost:8000"

    def get_next_id(self) -> int:
        """Get the next available entity ID."""
        self.entity_counter += 1
        return self.entity_counter

    def create_mock_mesh_response(
        self, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response specifically for mesh creation."""
        if identifier is None:
            identifier = f"mock_mesh_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={
                "entity": {
                    "identifier": identifier,
                    "type": "mesh",
                    "status": "created",
                }
            },
        )

    def create_mock_system_response(
        self, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response specifically for system creation."""
        if identifier is None:
            identifier = f"mock_system_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={"identifier": identifier, "type": "system", "status": "created"},
        )

    def create_mock_source_response(
        self, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response specifically for source creation."""
        if identifier is None:
            identifier = f"mock_source_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={
                "entity": {
                    "identifier": identifier,
                    "type": "source",
                    "status": "created",
                }
            },
        )

    def create_mock_object_response(
        self, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response specifically for object creation."""
        if identifier is None:
            identifier = f"mock_object_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={
                "entity": {
                    "identifier": identifier,
                    "type": "object",
                    "status": "created",
                }
            },
        )

    def create_mock_product_response(
        self, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response specifically for product creation."""
        if identifier is None:
            identifier = f"mock_product_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={
                "entity": {
                    "identifier": identifier,
                    "type": "product",
                    "status": "created",
                }
            },
        )

    def create_mock_entity_response(
        self, entity_type: str, identifier: Optional[str] = None
    ) -> MockResponse:
        """Create a mock response for entity creation (generic fallback)."""
        if identifier is None:
            identifier = f"mock_{entity_type}_id_{self.get_next_id()}"

        return MockResponse(
            status_code=201,
            json_data={
                "entity": {
                    "identifier": identifier,
                    "type": entity_type,
                    "status": "created",
                }
            },
        )

    def create_mock_success_response(self) -> MockResponse:
        """Create a mock success response."""
        return MockResponse(
            status_code=200,
            json_data={
                "status": "success",
                "message": "Operation completed successfully",
            },
        )

    def create_mock_login_response(self) -> MockResponse:
        """Create a mock login response."""
        return MockResponse(
            status_code=200, json_data={"access_token": self.access_token}
        )

    def create_mock_error_response(
        self, status_code: int = 400, message: str = "Error"
    ) -> MockResponse:
        """Create a mock error response."""
        return MockResponse(
            status_code=status_code, json_data={"error": message}, ok=False
        )


def create_mock_context() -> Mock:
    """Create a mock API context."""
    context = Mock()

    # Mock the request methods
    context.post = Mock()
    context.get = Mock()
    context.put = Mock()
    context.delete = Mock()
    context.dispose = Mock()

    return context


def setup_mock_responses(context: Mock, config: MockAPIConfig) -> None:
    """Setup default mock responses for the context."""

    # Setup login response
    context.post.return_value = config.create_mock_login_response()

    # Setup entity creation responses with specific methods
    def mock_post_entity(url, data=None, headers=None, **kwargs):
        if "mesh" in url:
            return config.create_mock_mesh_response()
        elif "data_system" in url:
            return config.create_mock_system_response()
        elif "origin" in url:  # Source endpoint
            return config.create_mock_source_response()
        elif "resource" in url:  # Object endpoint
            return config.create_mock_object_response()
        elif "product" in url:
            return config.create_mock_product_response()
        else:
            return config.create_mock_success_response()

    context.post.side_effect = mock_post_entity

    # Setup PUT requests (for updates)
    context.put.return_value = config.create_mock_success_response()

    # Setup GET requests
    context.get.return_value = config.create_mock_success_response()

    # Setup DELETE requests
    context.delete.return_value = config.create_mock_success_response()


# Global mock configuration instance
mock_config = MockAPIConfig()
