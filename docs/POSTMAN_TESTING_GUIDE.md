# Postman API Testing Guide

This guide explains how to use **Postman** to test the Order & Warehouse Management System API endpoints as an alternative or complement to the existing Python test suite.

## 📋 Table of Contents

- [Overview](#overview)
- [Setup & Installation](#setup--installation)
- [Using the Postman Collection](#using-the-postman-collection)
- [Environment Configuration](#environment-configuration)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Comparison with Python Tests](#comparison-with-python-tests)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

### Why Use Postman?

**Postman complements the existing Python test suite** by providing:

- **Visual Interface**: Easy-to-use GUI for API testing
- **Manual Testing**: Interactive testing during development
- **Team Collaboration**: Shareable collections and environments
- **Documentation**: Auto-generated API documentation
- **CI/CD Integration**: Can be integrated into automated pipelines
- **Real-time Testing**: Test against live APIs without writing code

### Relationship to Existing Tests

| Test Type | Python Tests | Postman Tests |
|-----------|--------------|---------------|
| **Unit Tests** | ✅ Mock-based, fast | ❌ Real API calls only |
| **Integration Tests** | ✅ Real API calls | ✅ Real API calls |
| **Manual Testing** | ❌ Code required | ✅ GUI-based |
| **Automation** | ✅ Command line | ✅ Newman CLI |
| **CI/CD** | ✅ Native Python | ✅ Newman integration |

## 🚀 Setup & Installation

### Prerequisites

1. **Download Postman**
   - Desktop: [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
   - Web: [https://web.postman.co/](https://web.postman.co/)

2. **Start Your Flask Application**
   ```bash
   # Make sure your Flask app is running
   python app.py
   # Or using WSGI
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

3. **Set Environment Variables** (for integration testing)
   ```bash
   export VEEQO_API_KEY="your_veeqo_api_key_here"
   export EASYSHIP_API_KEY="your_easyship_api_key_here"
   export RUN_INTEGRATION_TESTS="true"
   ```

### Importing the Collection

1. **Download the Collection**
   - Use the `postman_collection.json` file provided in this repository

2. **Import into Postman**
   - Open Postman
   - Click "Import" button
   - Drag and drop `postman_collection.json` or click "Upload Files"
   - The collection will appear in your sidebar

## ⚙️ Environment Configuration

### Setting Up Environment Variables

1. **Create New Environment**
   - Click the gear icon (⚙️) in top right
   - Click "Add" to create new environment
   - Name it "Order Management API - Local"

2. **Add Variables**
   ```json
   {
     "base_url": "http://localhost:5000",
     "VEEQO_API_KEY": "your_actual_veeqo_key",
     "EASYSHIP_API_KEY": "your_actual_easyship_key"
   }
   ```

3. **Select Environment**
   - Use the dropdown in top right to select your environment

### Multiple Environments

Create separate environments for different stages:

**Local Development:**
```json
{
  "base_url": "http://localhost:5000",
  "VEEQO_API_KEY": "dev_veeqo_key",
  "EASYSHIP_API_KEY": "dev_easyship_key"
}
```

**Staging:**
```json
{
  "base_url": "https://staging.yourapp.com",
  "VEEQO_API_KEY": "staging_veeqo_key",
  "EASYSHIP_API_KEY": "staging_easyship_key"
}
```

**Production:**
```json
{
  "base_url": "https://yourapp.com",
  "VEEQO_API_KEY": "prod_veeqo_key",
  "EASYSHIP_API_KEY": "prod_easyship_key"
}
```

## 🧪 Test Categories

The Postman collection includes the following test categories:

### 1. Customer Management
- **Parse Customer Input**: Test customer data parsing
- Validates tab-separated and space-separated formats
- Tests error handling for invalid input

### 2. Data Synchronization  
- **Sync All Data**: Full data sync from both platforms
- **Manual Product Sync**: Trigger bidirectional product sync
- Tests API connectivity and data retrieval

### 3. Inventory Management
- **Get Inventory Alerts**: Retrieve active alerts
- **Get Inventory Summary**: Comprehensive inventory overview
- **Resolve Alert**: Mark alerts as resolved
- **Get Reorder Suggestions**: Automated reorder recommendations

### 4. Product Statistics
- **Get Product Stats**: Real-time product performance data
- Includes sync stats, performance metrics, and alert counts

### 5. Auto-Sync Management
- **Start Auto Sync**: Begin automatic synchronization
- **Stop Auto Sync**: Halt automatic synchronization
- Configurable sync intervals

### 6. Order Processing
- **FedEx Orders**: Process and create FedEx shipments
- **Veeqo Orders**: Process and create Veeqo orders
- **Purchase Orders**: Retrieve Veeqo purchase orders

### 7. Error Handling Tests
- Tests for invalid inputs, missing data, and edge cases
- Validates proper error responses and status codes

## 🎯 Running Tests

### Individual Request Testing

1. **Select a Request**
   - Expand a folder in the collection
   - Click on a specific request

2. **Review Request Details**
   - Check HTTP method (GET, POST, etc.)
   - Review headers and body content
   - Verify URL and parameters

3. **Send Request**
   - Click "Send" button
   - Review response in the bottom panel

4. **Check Test Results**
   - Click "Test Results" tab
   - View passed/failed assertions

### Running Entire Collection

1. **Collection Runner**
   - Right-click on collection name
   - Select "Run collection"

2. **Configure Run**
   - Select environment
   - Choose requests to run
   - Set iterations and delay

3. **Start Test Run**
   - Click "Run Order & Warehouse Management System API"
   - Monitor progress in real-time

4. **Review Results**
   - View summary of all tests
   - Export results if needed

### Command Line Testing (Newman)

Install Newman for command-line testing:

```bash
# Install Newman globally
npm install -g newman

# Run collection
newman run postman_collection.json \
  --environment your_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

## 📊 Comparison with Python Tests

### When to Use Postman vs Python Tests

**Use Postman for:**
- ✅ Manual testing during development
- ✅ API exploration and documentation
- ✅ Team collaboration and sharing
- ✅ Quick integration testing
- ✅ Visual test result analysis

**Use Python Tests for:**
- ✅ Unit testing with mocks
- ✅ Automated CI/CD pipelines
- ✅ Complex business logic testing
- ✅ Fast execution (mocked tests)
- ✅ Version control integration

### Test Coverage Comparison

| Feature | Python Tests | Postman Tests |
|---------|-------------|---------------|
| **Customer Parsing** | ✅ Unit + Integration | ✅ Integration only |
| **API Endpoints** | ✅ All endpoints | ✅ All endpoints |
| **Error Handling** | ✅ Comprehensive | ✅ Basic scenarios |
| **Business Logic** | ✅ Deep validation | ❌ API-level only |
| **External APIs** | ✅ Mock + Real | ✅ Real only |
| **Performance** | ✅ Fast (mocked) | ⚠️ Slower (real APIs) |

## 💡 Best Practices

### 1. Test Organization
- **Group related tests** in folders
- **Use descriptive names** for requests
- **Add documentation** to each request
- **Include example responses**

### 2. Environment Management
- **Use variables** for all URLs and keys
- **Create separate environments** for each stage
- **Never hardcode sensitive data**
- **Use global variables** for common values

### 3. Test Scripts
- **Add assertions** to verify responses
- **Check status codes** for all requests
- **Validate response structure**
- **Set variables** from responses for chaining

### 4. Error Handling
- **Test both success and failure cases**
- **Verify error response formats**
- **Check appropriate status codes**
- **Test edge cases and invalid inputs**

### 5. Performance Considerations
- **Add delays** between requests for rate limiting
- **Monitor response times**
- **Test with realistic data volumes**
- **Use pre-request scripts** for setup

## 🔧 Advanced Features

### Pre-request Scripts

Add setup logic before requests:

```javascript
// Set dynamic timestamp
pm.globals.set('timestamp', new Date().toISOString());

// Generate random customer name
pm.globals.set('customer_name', 'customer_' + Math.floor(Math.random() * 1000));
```

### Test Scripts

Add custom validation logic:

```javascript
// Check response structure
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('data');
});

// Set variables for next request
if (pm.response.code === 200) {
    var responseData = pm.response.json();
    pm.environment.set('order_id', responseData.order_id);
}
```

### Data-Driven Testing

Use CSV/JSON files for test data:

1. **Create test data file** (`test_customers.csv`):
   ```csv
   name,phone,email,city,state
   John Doe,+1234567890,john@test.com,Las Vegas,Nevada
   Jane Smith,+0987654321,jane@test.com,Los Angeles,California
   ```

2. **Use in Collection Runner**:
   - Upload data file
   - Reference columns as `{{name}}`, `{{phone}}`, etc.

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: connect ECONNREFUSED 127.0.0.1:5000
   ```
   **Solution**: Ensure Flask app is running on correct port

2. **Invalid API Keys**
   ```
   401 Unauthorized
   ```
   **Solution**: Check environment variables are set correctly

3. **JSON Parse Errors**
   ```
   Unexpected token in JSON
   ```
   **Solution**: Verify request body format and Content-Type header

4. **Rate Limiting**
   ```
   429 Too Many Requests
   ```
   **Solution**: Add delays between requests or reduce test frequency

### Debug Tips

- **Use Console**: View `console.log()` output in Postman Console
- **Check Variables**: Verify environment/global variables are set
- **Inspect Requests**: Use browser dev tools for web version
- **Test Individually**: Run single requests before full collection

## 🔄 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Postman API Tests
on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Start Flask App
      run: |
        pip install -r requirements.txt
        python app.py &
        sleep 10
    
    - name: Install Newman
      run: npm install -g newman
    
    - name: Run Postman Tests
      run: |
        newman run postman_collection.json \
          --environment postman_environment.json \
          --reporters cli,junit \
          --reporter-junit-export results.xml
      env:
        VEEQO_API_KEY: ${{ secrets.VEEQO_API_KEY }}
        EASYSHIP_API_KEY: ${{ secrets.EASYSHIP_API_KEY }}
    
    - name: Publish Test Results
      uses: EnricoMi/publish-unit-test-result-action@v1
      if: always()
      with:
        files: results.xml
```

## 📈 Monitoring and Reporting

### Built-in Reports
- **Test Summary**: Pass/fail counts and timing
- **Response Time**: Performance metrics
- **Coverage**: Endpoint coverage analysis

### External Integration
- **Newman HTML Reporter**: Detailed HTML reports
- **Slack/Teams**: Test result notifications
- **Dashboard Tools**: Grafana, DataDog integration

---

## 🤝 Contributing

When adding new API endpoints:

1. **Add to Postman collection** with proper tests
2. **Update environment variables** if needed
3. **Include error test cases**
4. **Document expected behavior**
5. **Test both success and failure paths**

## 📞 Support

For Postman-specific issues:
1. Check this documentation first
2. Verify environment setup
3. Test individual requests before collections
4. Check Postman Console for detailed errors
5. Refer to [Postman Documentation](https://learning.postman.com/)

---

**Happy API Testing with Postman! 🚀✨**
