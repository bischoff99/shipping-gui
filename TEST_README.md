# API Testing Suite Documentation

This comprehensive testing suite validates the API logic and responses for the Order & Warehouse Management System. It includes both unit tests and integration tests to ensure reliable API functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Setup & Installation](#setup--installation)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Configuration](#configuration)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The testing suite covers:

- **API Endpoint Testing**: All Flask routes and JSON responses
- **External API Integration**: Veeqo and Easyship API interactions
- **Business Logic Validation**: Customer parsing, routing, validation
- **Error Handling**: Edge cases and failure scenarios
- **Response Format Validation**: Consistent API response structures

## 🏗️ Test Structure

```
├── test_api_responses.py      # Unit tests (mock-based)
├── test_api_integration.py    # Integration tests (real APIs)
├── test_config.py            # Test configuration and sample data
├── run_tests.py              # Main test runner
└── TEST_README.md            # This documentation
```

### Test Categories

1. **Unit Tests** (`test_api_responses.py`)
   - Mock-based testing
   - Fast execution
   - No external dependencies
   - Default test suite

2. **Integration Tests** (`test_api_integration.py`)
   - Real API calls
   - Requires valid API keys
   - Rate-limited execution
   - Optional testing

## 🚀 Setup & Installation

### Prerequisites

```bash
# Ensure you have Python 3.7+
python --version

# Install required packages
pip install -r requirements.txt

# Additional testing packages (if needed)
pip install unittest-mock requests-mock
```

### Environment Setup

Create a `.env` file or set environment variables:

```bash
# Required for integration tests
export VEEQO_API_KEY="your_veeqo_api_key_here"
export EASYSHIP_API_KEY="your_easyship_api_key_here"

# Optional test configuration
export RUN_INTEGRATION_TESTS="true"
export API_CALL_DELAY="1.0"
export MAX_API_CALLS="5"
```

## 🎯 Running Tests

### Quick Start

```bash
# Run unit tests only (default, fastest)
python run_tests.py

# Check environment setup
python run_tests.py --check-env
```

### All Test Options

```bash
# Unit tests only (mock-based, fast)
python run_tests.py --unit

# Integration tests only (requires API keys)
python run_tests.py --integration

# All tests (unit + integration)
python run_tests.py --all

# Specific test file
python run_tests.py --specific test_api_responses.py

# Specific test class
python run_tests.py --specific test_api_responses.py FlaskAPIEndpointsTest

# Specific test method
python run_tests.py --specific test_api_responses.py FlaskAPIEndpointsTest test_api_parse_customer_success

# Verbose output
python run_tests.py --verbose
```

### Direct Test Execution

```bash
# Run unit tests directly
python test_api_responses.py

# Run integration tests directly
python test_api_integration.py
```

## 🧪 Test Types

### 1. Flask API Endpoints (`FlaskAPIEndpointsTest`)

Tests all API endpoints and their responses:

```python
# Tests covered:
- /api/parse_customer (POST)
- /sync_data (GET)
- /api/sync_products (POST)
- /api/product_stats (GET)
- /api/inventory_alerts (GET)
- /api/inventory_summary (GET)
- /api/reorder_suggestions (GET)
- /api/resolve_alert/<id> (POST)
- /api/start_auto_sync (POST)
- /api/stop_auto_sync (POST)
```

### 2. External API Integration (`ExternalAPITest`)

Tests Veeqo and Easyship API integrations:

```python
# Veeqo API tests:
- get_warehouses()
- get_products()
- create_order()
- get_purchase_orders()

# Easyship API tests:
- get_addresses()
- get_products()
- create_shipment()
- book_fedex_rate()
```

### 3. Business Logic (`BusinessLogicTest`)

Tests core business logic:

```python
# Validation tests:
- Customer data validation
- Warehouse data validation
- Product validation

# Utility function tests:
- Customer input parsing
- Data normalization
- Phone/email formatting

# Routing system tests:
- Order routing decisions
- Carrier selection
- Platform mapping
```

### 4. Order Processing (`OrderProcessingTest`)

Tests order creation workflows:

```python
# FedEx order processing
# Veeqo order processing
# Purchase order management
# Error handling in order flow
```

### 5. Error Handling (`ErrorHandlingTest`)

Tests error scenarios:

```python
# API exceptions
# Invalid JSON requests
# Missing parameters
# Network failures
# Authentication errors
```

## ⚙️ Configuration

### Test Configuration (`test_config.py`)

The `TestConfig` class centralizes all test settings:

```python
class TestConfig:
    # Integration test settings
    RUN_INTEGRATION_TESTS = True/False
    API_CALL_DELAY = 1.0  # seconds
    MAX_API_CALLS_PER_TEST = 5
    
    # API credentials
    VEEQO_API_KEY = "your_key"
    EASYSHIP_API_KEY = "your_key"
```

### Sample Data (`SampleData`)

Pre-defined test data for consistent testing:

```python
# Customer data variants
VALID_CUSTOMER = {...}
MINIMAL_CUSTOMER = {...}
INTERNATIONAL_CUSTOMER = {...}
INVALID_CUSTOMER = {...}

# Product and warehouse samples
SAMPLE_PRODUCTS = [...]
SAMPLE_WAREHOUSES = [...]
```

### Environment Variables

```bash
# Core testing
RUN_INTEGRATION_TESTS=true/false
TESTING=true

# API rate limiting
API_CALL_DELAY=1.0
MAX_API_CALLS=5
API_TIMEOUT=30

# API credentials
VEEQO_API_KEY=your_veeqo_key
EASYSHIP_API_KEY=your_easyship_key
```

## ✍️ Writing New Tests

### Adding Unit Tests

1. **Create test class** inheriting from `APITestCase`:

```python
class MyNewTest(APITestCase):
    def test_my_feature(self):
        # Your test code here
        pass
```

2. **Use mocking** for external dependencies:

```python
@patch('app.some_api_call')
def test_with_mock(self, mock_api):
    mock_api.return_value = {'status': 'success'}
    # Test your logic
```

3. **Assert JSON responses**:

```python
response = self.client.post('/api/endpoint', json={...})
data = self.assertJSONResponse(response)
self.assertEqual(data['status'], 'success')
```

### Adding Integration Tests

1. **Create integration test class**:

```python
class MyIntegrationTest(APIIntegrationTestCase):
    def test_real_api_call(self):
        self.skipIfNoRealAPITests()
        
        result = self.make_rate_limited_call(
            lambda: self.veeqo_api.some_method()
        )
        # Validate real API response
```

2. **Use rate limiting** for real API calls:

```python
result = self.make_rate_limited_call(api_function)
```

### Test Naming Conventions

- `test_[feature]_success` - Happy path tests
- `test_[feature]_error` - Error condition tests
- `test_[feature]_invalid_input` - Input validation tests
- `test_[feature]_edge_case` - Edge case scenarios

## 🐛 Troubleshooting

### Common Issues

1. **ImportError: No module named 'app'**
   ```bash
   # Ensure you're in the project root directory
   cd /path/to/your/project
   python run_tests.py
   ```

2. **API Key Issues**
   ```bash
   # Check environment variables
   echo $VEEQO_API_KEY
   echo $EASYSHIP_API_KEY
   
   # Set if missing
   export VEEQO_API_KEY="your_key_here"
   ```

3. **Integration Tests Failing**
   ```bash
   # Check if integration tests are enabled
   export RUN_INTEGRATION_TESTS=true
   
   # Verify API connectivity
   python run_tests.py --check-env
   ```

4. **Rate Limiting Issues**
   ```bash
   # Increase delay between API calls
   export API_CALL_DELAY=2.0
   
   # Reduce max calls per test
   export MAX_API_CALLS=3
   ```

### Debug Mode

Run tests with verbose output:

```bash
python run_tests.py --verbose
```

### Individual Test Debugging

```bash
# Run specific failing test
python run_tests.py --specific test_api_responses.py FlaskAPIEndpointsTest test_failing_method

# Add print statements in test code
def test_debug(self):
    print(f"Debug: {some_variable}")
    # Your test code
```

## 📊 Test Coverage

### Current Coverage Areas

✅ **Covered:**
- All Flask API endpoints
- External API integrations (Veeqo/Easyship)
- Customer data validation
- Order routing logic
- Error handling scenarios
- Response format validation

🔄 **Partial Coverage:**
- Real-time inventory monitoring
- Advanced product synchronization
- Performance under load

❌ **Not Covered:**
- Database operations (if any)
- File system operations
- Email notifications (if implemented)

### Improving Coverage

1. **Add new test cases** for uncovered scenarios
2. **Mock external dependencies** properly
3. **Test edge cases** and error conditions
4. **Validate response schemas** thoroughly

## 🚀 Best Practices

### Writing Effective Tests

1. **Keep tests independent** - Each test should run in isolation
2. **Use descriptive names** - Test names should explain what they test
3. **Mock external dependencies** - Don't rely on external services in unit tests
4. **Test both success and failure paths** - Cover happy path and error scenarios
5. **Use appropriate assertions** - Choose the right assertion method
6. **Keep tests focused** - One test should test one specific behavior

### Test Organization

1. **Group related tests** in the same test class
2. **Use setUp/tearDown** for common test preparation
3. **Share test data** through `SampleData` class
4. **Document complex test scenarios** with comments

### Performance Considerations

1. **Use mocks for unit tests** - Avoid real API calls
2. **Implement rate limiting** for integration tests
3. **Run integration tests sparingly** - Use them for critical paths only
4. **Cache test data** when possible

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run unit tests
      run: python run_tests.py --unit
    - name: Run integration tests
      run: python run_tests.py --integration
      env:
        RUN_INTEGRATION_TESTS: true
        VEEQO_API_KEY: ${{ secrets.VEEQO_API_KEY }}
        EASYSHIP_API_KEY: ${{ secrets.EASYSHIP_API_KEY }}
```

---

## 🤝 Contributing

When adding new features to the API:

1. **Write tests first** (TDD approach)
2. **Add both unit and integration tests** if applicable
3. **Update this documentation** if adding new test types
4. **Ensure all tests pass** before submitting changes

## 📞 Support

If you encounter issues with the testing suite:

1. Check this documentation first
2. Review error messages carefully
3. Verify environment setup
4. Check API key validity and permissions
5. Review network connectivity for integration tests

---

**Happy Testing! 🧪✨**
