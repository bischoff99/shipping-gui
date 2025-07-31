# Enhanced Testing Infrastructure

## Overview
Comprehensive testing suite for the MCP-Enhanced Shipping GUI application, featuring unit tests, integration tests, and API validation.

## Test Structure
```
tests_new/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests for individual components
│   ├── test_app_factory.py  # Application factory pattern tests
│   ├── test_security_middleware.py  # Security middleware tests
│   └── test_routes.py       # Route blueprint tests
├── integration/             # Integration tests
│   ├── test_security_integration.py  # End-to-end security tests
│   └── test_mcp_integration.py      # MCP feature integration tests
└── api/                     # API endpoint tests
    └── (API test files)
```

## Running Tests

### All Tests
```bash
pytest tests_new/
```

### Unit Tests Only
```bash
pytest tests_new/unit/
```

### Integration Tests Only
```bash  
pytest tests_new/integration/
```

### With Coverage
```bash
pytest tests_new/ --cov=src --cov-report=html
```

### Specific Test Categories
```bash
# Security tests
pytest tests_new/ -m security

# Performance tests  
pytest tests_new/ -m performance

# MCP feature tests
pytest tests_new/ -m mcp
```

## Test Features

### Comprehensive Fixtures
- **Application Factory**: Creates test apps with different configurations
- **Database Sessions**: Automated database setup/cleanup
- **Mock APIs**: Mocked Veeqo and Easyship API responses
- **Sample Data**: Pre-configured test data for all models
- **Security Context**: CSRF protection and authentication helpers

### Security Testing
- CSRF protection validation
- Input sanitization verification  
- Rate limiting enforcement
- XSS/SQL injection protection
- API key validation
- Session security configuration

### MCP Integration Testing
- AI-enhanced parsing validation
- Route optimization testing
- Error analysis verification
- Development insights validation
- MCP server health monitoring
- Performance under load

### Performance Monitoring
- Response time measurement
- Concurrent request handling
- Memory usage tracking
- Database query optimization

## Test Configuration

### Environment Variables
```bash
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
export WTF_CSRF_ENABLED=false
```

### Pytest Markers
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.mcp` - MCP integration tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.integration` - Integration tests

### Mock Configuration
Tests use extensive mocking for:
- External API calls (Veeqo, Easyship)
- Database operations
- MCP server communications
- Redis/caching operations
- File system operations

## Test Data

### Sample Customer Data
```python
{
    'name': 'John Doe',
    'email': 'john.doe@example.com', 
    'phone': '+1234567890',
    'address': '123 Main St',
    'city': 'Boston',
    'state': 'MA',
    'zip': '02101',
    'country': 'US'
}
```

### Mock API Responses
- Successful order creation
- Validation errors
- API connection failures
- Rate limiting responses
- Authentication failures

## Continuous Integration

### GitHub Actions Integration
Tests run automatically on:
- Pull requests
- Main branch commits
- Scheduled nightly runs

### Test Reports
- Coverage reports generated in HTML format
- Performance benchmarks tracked
- Security scan results included
- MCP feature status monitoring

## Development Guidelines

### Adding New Tests
1. Follow existing test patterns
2. Use appropriate fixtures
3. Mock external dependencies
4. Add proper test markers
5. Include docstrings
6. Test both success and failure cases

### Test Organization
- Unit tests: Test individual functions/classes
- Integration tests: Test component interactions  
- API tests: Test endpoint behavior
- Security tests: Test security features
- Performance tests: Test under load

### Best Practices
- Tests should be independent and repeatable
- Use descriptive test names
- Mock external services
- Test edge cases and error conditions
- Keep tests fast and focused
- Use appropriate assertions

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure PYTHONPATH includes src/
- **Database Errors**: Check test database configuration
- **Mock Failures**: Verify mock setup matches actual API
- **Timeout Issues**: Increase test timeouts for slow operations

### Debug Mode
```bash
pytest tests_new/ -v -s --tb=short
```

### Specific Test Debugging
```bash
pytest tests_new/unit/test_app_factory.py::TestAppFactory::test_create_app_development -v -s
```

## Coverage Goals
- Overall coverage: >90%
- Critical paths: 100%
- Security features: 100%
- API endpoints: >95%
- Error handling: >90%