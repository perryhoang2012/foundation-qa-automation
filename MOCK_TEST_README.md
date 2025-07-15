# Mocked API Testing

This document explains how to use the mocked API tests for the Velora API automation framework.

## Overview

The mocked tests allow you to run API automation tests without requiring a real server. All API calls are intercepted and return predefined mock responses.

## Files Structure

```
tests/
├── test_procedures_generator_by_verlora_mock.py  # Main test file with mocked API
├── mock_config.py                                 # Mock configuration and responses
└── ...

run_mock_tests.py                                  # Test runner script
MOCK_TEST_README.md                               # This file
```

## Key Features

### 1. Mock Response System

The `MockResponse` class simulates HTTP responses:

- `status_code`: HTTP status code
- `json()`: Returns JSON data
- `text()`: Returns text data
- `ok`: Boolean indicating success/failure

### 2. Mock API Configuration

The `MockAPIConfig` class provides:

- Entity ID generation
- Predefined response templates
- Centralized mock configuration

### 3. Automatic Mock Setup

The `setup_mock_responses()` function automatically configures:

- Login responses
- Entity creation responses (mesh, system, source, object, product)
- Success responses for operations
- Error responses when needed

## How to Run Tests

### Option 1: Using the Test Runner Script

```bash
python run_mock_tests.py
```

### Option 2: Using pytest directly

```bash
pytest tests/test_procedures_generator_by_verlora_mock.py -v -s
```

### Option 3: Run specific test

```bash
pytest tests/test_procedures_generator_by_verlora_mock.py::test_login_api -v
```

## Mock Responses

### Entity Creation Responses

When creating entities (mesh, system, source, object, product), the mock returns:

```json
{
  "entity": {
    "identifier": "mock_mesh_id_1",
    "type": "mesh",
    "status": "created"
  }
}
```

### Success Responses

For operations like linking, configuration, etc.:

```json
{
  "status": "success",
  "message": "Operation completed successfully"
}
```

### Login Response

```json
{
  "access_token": "mock_access_token_12345"
}
```

## Test Structure

### 1. Fixtures

- `api_context`: Provides mock context and access token
- `id_map`: Empty dictionary for entity mapping

### 2. Step Classes

Each API operation has a corresponding step class:

- `CreateMeshStep`
- `CreateSystemStep`
- `CreateSourceStep`
- `CreateObjectStep`
- `LinkObjectToSourceStep`
- `ConfigureObjectDetailsStep`
- `CreateProductStep`
- `LinkProductToObjectStep`
- `LinkProductToProductStep`
- `CreateDataProductSchemaStep`
- `LinkSystemToSourceStep`
- `ConfigureConnectionDetailsStep`
- `SetConnectionSecretsStep`
- `CreateTransformationBuilderStep`

### 3. Test Execution

Tests are parameterized based on the procedure configuration:

```python
@pytest.mark.parametrize(
    "step",
    config.get("steps", []),
    ids=lambda x: f"Step {config.get('steps', []).index(x) + 1}: {x['type']}_{x.get('id') or x.get('identifier') or ''}",
)
def test_step_execution(request, step, api_context, id_map):
    get_step_instance(request, step, api_context, id_map).execute()
```

## Customizing Mock Responses

### 1. Modify Mock Configuration

Edit `tests/mock_config.py` to change default responses:

```python
def create_mock_entity_response(self, entity_type: str, identifier: str = None) -> MockResponse:
    # Customize the response structure
    return MockResponse(
        status_code=201,
        json_data={
            "entity": {
                "identifier": identifier or f"custom_{entity_type}_id",
                "type": entity_type,
                "status": "created",
                "custom_field": "custom_value"
            }
        }
    )
```

### 2. Add Custom Mock Responses

```python
def create_custom_response(self) -> MockResponse:
    return MockResponse(
        status_code=200,
        json_data={"custom": "response"}
    )
```

### 3. Mock Error Scenarios

```python
# In your test
context.post.return_value = mock_config.create_mock_error_response(400, "Bad Request")
```

## Benefits

1. **No Server Required**: Tests run without a real API server
2. **Fast Execution**: No network delays
3. **Predictable Results**: Consistent mock responses
4. **Isolated Testing**: No external dependencies
5. **Easy Debugging**: Clear mock responses
6. **CI/CD Friendly**: No server setup needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in Python path
2. **Mock Not Working**: Check that `setup_mock_responses()` is called
3. **Missing Responses**: Verify the mock configuration covers all endpoints

### Debug Mode

Run with verbose output to see mock interactions:

```bash
pytest tests/test_procedures_generator_by_verlora_mock.py -v -s --tb=long
```

## Integration with Real API

To switch from mock to real API:

1. Remove mock imports
2. Use real Playwright context
3. Update environment variables
4. Remove mock response setup

The test structure remains the same, only the API context changes.
