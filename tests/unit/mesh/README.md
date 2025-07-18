# Mesh API Tests

This directory contains comprehensive tests for the Mesh API endpoint (`POST /api/data/mesh`).

## Test Files

- **test_mesh_api.py**: Basic API functionality tests
- **test_mesh_validation.py**: Tests for field validation and performance
- **test_mesh_error_handling.py**: Tests for error handling and schema validation
- **test_mesh_operations.py**: Tests for specific API operations and behaviors

## Running the Tests

To run all mesh API tests:

```bash
pytest -v tests/unit/mesh/
```

To run a specific test file:

```bash
pytest -v tests/unit/mesh/test_mesh_api.py
```

To run a specific test:

```bash
pytest -v tests/unit/mesh/test_mesh_api.py::test_create_mesh_with_valid_payload
```

## Test Coverage

These tests validate:

1. **Basic Functionality**

   - Creating mesh with valid payload
   - Proper response structure
   - Proper identifier assignment

2. **Validation**

   - Field validation (required fields, data types)
   - Name field validation
   - Description field validation
   - Assignees validation
   - Security policy validation

3. **Error Handling**

   - Missing required fields
   - Invalid field types
   - Malformed JSON
   - Empty requests
   - Error response format

4. **API Operations**

   - Idempotency (if supported)
   - Concurrent creation
   - Transaction handling
   - Creating with minimal fields

5. **Edge Cases**
   - Special characters in fields
   - Very long field values
   - Rate limiting behavior
   - Performance with multiple requests

## Test Data

The tests use data fixtures defined in `conftest.py` to provide test data and helper functions.

## Dependencies

These tests depend on the following fixtures and functions:

- `api_context` from the main conftest.py
- `create_mesh_payload` from test_data/shared/mesh_payload.py
- Helper functions for headers and assertions
