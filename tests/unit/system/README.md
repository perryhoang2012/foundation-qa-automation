# System API Tests

This directory contains comprehensive API tests for the POST `/api/data/data_system` endpoint.

## Test Files

### 1. `conftest.py`

Contains fixtures and helper classes for system API testing:

- **API context setup** with authentication
- **SystemApiHelper class** for common operations
- **Cleanup fixtures** to automatically delete created test data
- **Helper functions** for headers, recording API info, etc.

### 2. `test_system_api.py`

Main API test suite covering:

- **Happy path scenarios**: Valid system creation
- **Required field validation**: Missing name, entity_type, owner info, etc.
- **Header validation**: Missing/invalid authorization, x-account header
- **Special characters**: Unicode, special symbols in names
- **Response structure validation**: Proper JSON structure and data types
- **Edge cases**: Long names/descriptions, minimal payloads

### 3. `test_system_error_handling.py`

Error handling and security test suite covering:

- **Malformed requests**: Null payloads, empty JSON, malformed JSON
- **Missing sections**: No entity or entity_info sections
- **Security tests**: SQL injection, XSS attempts
- **Data type validation**: Wrong types for fields
- **Extreme values**: Very long strings, concurrent requests
- **Error response format**: Proper error structure validation

### 4. `test_system_validation.py`

Detailed validation test suite covering:

- **Required field validation**: All mandatory fields
- **Email format validation**: Valid/invalid email formats
- **Entity type validation**: Only 'data_system' should be accepted
- **String length limits**: Min/max length testing
- **Empty/whitespace validation**: Empty strings, whitespace-only values
- **Array field validation**: contact_ids and links arrays
- **Nested object validation**: owner_person structure
- **Case sensitivity**: Field names and values
- **Data consistency**: Related field validation

## Test Categories

### Positive Tests

- ✅ Valid system creation with all required fields
- ✅ Valid email formats
- ✅ Special characters in names (Unicode, symbols)
- ✅ Different valid array values
- ✅ Minimal required payload

### Negative Tests

- ❌ Missing required fields (name, entity_type, owner info, etc.)
- ❌ Invalid email formats
- ❌ Wrong entity_type values
- ❌ Empty/whitespace-only strings
- ❌ Wrong data types for fields
- ❌ Malformed JSON payloads

### Security Tests

- 🔒 SQL injection attempts
- 🔒 XSS/script injection attempts
- 🔒 Missing/invalid authentication
- 🔒 Missing x-account header

### Edge Cases

- 🎯 Extremely long field values
- 🎯 Concurrent system creation
- 🎯 Unknown/extra fields in payload
- 🎯 Field order independence

## Running the Tests

### Run all system tests:

```bash
pytest tests/unit/system/ -v
```

### Run specific test file:

```bash
pytest tests/unit/system/test_system_api.py -v
pytest tests/unit/system/test_system_error_handling.py -v
pytest tests/unit/system/test_system_validation.py -v
```

### Run with specific markers:

```bash
pytest tests/unit/system/ -m "api" -v
```

## Configuration

Make sure your `.env` file contains:

```
API_URL=https://api.stg.meshx.dev
API_TOKEN=your_jwt_token_here
X_ACCOUNT=your_account_id
OWNER_EMAIL=your_email@domain.com
OWNER_NAME=Your Name
```

## Test Data

The tests use the `create_system_payload()` function from `test_data/shared/system_payload.py` to generate valid payloads with:

- Random system names using `makeid()`
- Environment-based owner information
- Required entity_type set to "data_system"
- Proper nested structure for entity and entity_info

## Cleanup

All tests automatically clean up created systems using the `system_ids` fixture, which:

- Tracks all created system identifiers
- Automatically deletes them after test completion
- Handles cleanup failures gracefully
- Works with parallel test execution

## Error Handling

The tests validate:

- Proper HTTP status codes (200, 400, 401, 422)
- Error response structure with required fields
- Appropriate error messages for different scenarios
- No server errors (500) for invalid input

## Extensibility

To add new tests:

1. Use the existing fixtures (`api_context`, `system_api`, `valid_system_payload`)
2. Follow the naming convention `test_*`
3. Use the `SystemApiHelper` for common operations
4. Ensure cleanup by using `system_api.create_system()` or managing `system_ids` manually
