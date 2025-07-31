# Complete Postman Testing Execution Plan
## Order & Warehouse Management System API Testing

This document provides a comprehensive step-by-step plan for executing all Postman tests for the unified order and warehouse management system.

## Overview
The testing suite includes **8 main test categories** with **25+ individual test cases** covering:
- Customer Management (2 tests)
- Data Synchronization (2 tests) 
- Inventory Management (4 tests)
- Product Statistics (1 test)
- Auto-Sync Management (2 tests)
- FedEx Order Processing (2 tests)
- Veeqo Order Processing (3 tests)
- Error Handling Tests (3 tests)

## Prerequisites

### 1. System Requirements
- Python 3.7+ installed
- Postman Desktop Application or Newman CLI
- Valid API keys for Veeqo and Easyship
- Internet connection for API calls

### 2. Environment Setup
```bash
# Clone/navigate to project directory
cd your-project-directory

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env file with your actual API keys
# VEEQO_API_KEY=your-actual-veeqo-key
# EASYSHIP_API_KEY=your-actual-easyship-key
```

### 3. Verify Installation
```bash
# Check Python version
python --version

# Check Flask installation
python -c "import flask; print(flask.__version__)"

# Verify environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('VEEQO_API_KEY:', 'SET' if os.getenv('VEEQO_API_KEY') else 'NOT SET')"
```

## Step 1: Start Flask Application

### Option A: Using Shell Script (Linux/Mac)
```bash
chmod +x start_server.sh
./start_server.sh
```

### Option B: Using Batch Script (Windows)
```cmd
start_server.bat
```

### Option C: Direct Python Execution
```bash
python app.py
```

### Verify Server is Running
- Open browser and navigate to `http://localhost:5000`
- You should see the application dashboard
- Server logs should show: `Running on http://127.0.0.1:5000`

**⚠️ IMPORTANT: Keep the Flask server running throughout all testing!**

## Step 2: Import Postman Collection

### Using Postman Desktop App
1. Open Postman Desktop Application
2. Click **Import** button (top left)
3. Select **File** tab
4. Choose `postman_collection.json` from project directory
5. Click **Import**
6. Collection "Order & Warehouse Management System API" should appear in left sidebar

### Verify Import Success
- Collection should show 8 folders
- Total of 25+ requests should be visible
- Each request should have pre-configured URLs and test scripts

## Step 3: Configure Environment Variables

### Create Postman Environment
1. Click **Environments** tab (left sidebar)
2. Click **Create Environment**
3. Name: `Order Management Testing`
4. Add the following variables:

| Variable Name | Initial Value | Current Value |
|---------------|---------------|---------------|
| `VEEQO_API_KEY` | `{{VEEQO_API_KEY}}` | `your-actual-veeqo-key` |
| `EASYSHIP_API_KEY` | `{{EASYSHIP_API_KEY}}` | `your-actual-easyship-key` |
| `base_url` | `http://localhost:5000` | `http://localhost:5000` |

5. Click **Save**
6. Select this environment from the dropdown (top right)

### Verify Environment Setup
- Environment should be active (shown in top right)
- Variables should resolve properly in requests

## Step 4: Execute All Tests Systematically

### Testing Sequence (Recommended Order)

#### Phase 1: Basic Functionality Tests
1. **Customer Management**
   - ✅ Parse Customer Input (Valid data)
   - ✅ Parse Customer Input (Invalid data - Error handling)

2. **Data Synchronization**
   - ✅ Sync All Data
   - ✅ Manual Product Sync

#### Phase 2: Inventory and Product Tests
3. **Inventory Management**
   - ✅ Get Inventory Alerts
   - ✅ Get Inventory Summary
   - ✅ Resolve Alert (Test with ID: 1)
   - ✅ Get Reorder Suggestions

4. **Product Statistics**
   - ✅ Get Product Stats

#### Phase 3: Advanced Features Tests
5. **Auto-Sync Management**
   - ✅ Start Auto Sync (10-minute interval)
   - ✅ Stop Auto Sync

#### Phase 4: Order Processing Tests
6. **FedEx Order Processing**
   - ✅ Process All FedEx Orders
   - ✅ Create FedEx Order (Customer: john_doe)

7. **Veeqo Order Processing**
   - ✅ Process All Veeqo Orders
   - ✅ Create Veeqo Order (Customer: jane_smith)
   - ✅ Get Veeqo Purchase Orders

#### Phase 5: Error Handling Tests
8. **Error Handling**
   - ✅ Parse Customer - No JSON (400 error expected)
   - ✅ Resolve Non-existent Alert (404 error expected)

### Individual Test Execution
1. Expand test category folder
2. Click on individual request
3. Click **Send** button
4. Review response in bottom panel
5. Check **Test Results** tab for assertions
6. Verify all tests pass (green checkmarks)

## Step 5: Run Complete Test Suite

### Using Collection Runner (Recommended)
1. Right-click on collection name
2. Select **Run collection**
3. **Collection Runner** window opens
4. Configuration:
   - Environment: `Order Management Testing`
   - Iterations: `1`
   - Delay: `1000ms` (between requests)
   - Keep variable values: ✅
   - Run order: Use default sequence

5. Click **Run Order & Warehouse Management System API**
6. Monitor test execution in real-time
7. Review final results summary

### Expected Results
- **Total Tests**: 25+ assertions
- **Passed**: Should be majority (depending on API availability)
- **Failed**: Some may fail if APIs are not accessible
- **Skipped**: 0

## Step 6: Automated Testing with Newman (Optional)

### Install Newman
```bash
npm install -g newman
```

### Run Complete Test Suite
```bash
# Basic execution
newman run postman_collection.json

# With environment variables
newman run postman_collection.json \
  --env-var "VEEQO_API_KEY=your-key" \
  --env-var "EASYSHIP_API_KEY=your-key" \
  --env-var "base_url=http://localhost:5000"

# With detailed reporting
newman run postman_collection.json \
  --env-var "VEEQO_API_KEY=your-key" \
  --env-var "EASYSHIP_API_KEY=your-key" \
  --reporters cli,html \
  --reporter-html-export test-results.html
```

### Newman Output Interpretation
- ✅ Green: Tests passed
- ❌ Red: Tests failed
- Summary shows total requests, tests, and assertions

## Step 7: Results Analysis & Troubleshooting

### Common Expected Results

#### ✅ Should Always Pass
- Parse Customer Input (valid data)
- Get Inventory Alerts (returns array)
- Get Inventory Summary (returns object)
- Get Product Stats (returns stats object)
- Start/Stop Auto Sync operations

#### ⚠️ May Fail (Depending on API Keys/Data)
- Sync All Data (requires valid API keys)
- FedEx/Veeqo order creation (requires valid customer data)
- Resolve specific alerts (depends on existing alert IDs)

#### ❌ Should Fail (Error Testing)
- Parse Customer - Invalid Input (400 expected)
- Parse Customer - No JSON (400 expected)  
- Resolve Non-existent Alert (404 expected)

### Troubleshooting Common Issues

#### Server Connection Issues
```
Error: connect ECONNREFUSED 127.0.0.1:5000
```
**Solution**: Ensure Flask server is running (`python app.py`)

#### API Key Issues
```
Error: 401 Unauthorized or 403 Forbidden
```
**Solution**: Verify API keys in `.env` file and Postman environment

#### Import Errors
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Install requirements (`pip install -r requirements.txt`)

### Success Metrics
- **80%+ test pass rate**: Excellent
- **60-79% test pass rate**: Good (some API dependencies may be unavailable)
- **<60% test pass rate**: Check server and API key configuration

## Step 8: Final Verification & Reporting

### Comprehensive Test Checklist
- [ ] Flask server started successfully
- [ ] Postman collection imported (25+ requests)
- [ ] Environment variables configured
- [ ] Customer Management tests executed
- [ ] Data Synchronization tests executed
- [ ] Inventory Management tests executed
- [ ] Product Statistics tests executed
- [ ] Auto-Sync Management tests executed
- [ ] FedEx Order Processing tests executed
- [ ] Veeqo Order Processing tests executed
- [ ] Error Handling tests executed
- [ ] Collection Runner executed successfully
- [ ] Results documented

### Test Report Template
```
=== POSTMAN TESTING RESULTS ===
Date: [Current Date]
Tester: [Your Name]
Environment: [Development/Production]

SUMMARY:
- Total Requests: ___
- Total Tests: ___
- Passed: ___
- Failed: ___
- Pass Rate: ___%

CATEGORY BREAKDOWN:
✅ Customer Management: __/2
✅ Data Synchronization: __/2  
✅ Inventory Management: __/4
✅ Product Statistics: __/1
✅ Auto-Sync Management: __/2
✅ FedEx Order Processing: __/2
✅ Veeqo Order Processing: __/3
✅ Error Handling: __/3

ISSUES IDENTIFIED:
- [List any failed tests and reasons]

RECOMMENDATIONS:
- [Any suggested improvements or fixes]
```

## Conclusion
This comprehensive testing plan ensures complete coverage of all API endpoints and functionality in the Order & Warehouse Management System. Execute tests systematically and document results for continuous improvement.
