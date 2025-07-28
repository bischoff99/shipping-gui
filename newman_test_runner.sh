#!/bin/bash

# Newman Test Runner for Order & Warehouse Management System
# This script automates Newman test execution with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
COLLECTION_FILE="postman_collection.json"
ENV_FILE=".env"
RESULTS_DIR="test_results"
BASE_URL="http://localhost:5000"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print headers
print_header() {
    echo
    print_colored $CYAN "=========================================="
    print_colored $WHITE " $1"
    print_colored $CYAN "=========================================="
    echo
}

# Function to check prerequisites
check_prerequisites() {
    print_header "CHECKING PREREQUISITES"
    
    local all_good=true
    
    # Check Newman
    if command -v newman &> /dev/null; then
        local newman_version=$(newman --version)
        print_colored $GREEN "✅ Newman installed: $newman_version"
    else
        print_colored $RED "❌ Newman not found"
        print_colored $YELLOW "   Install with: npm install -g newman"
        all_good=false
    fi
    
    # Check collection file
    if [ -f "$COLLECTION_FILE" ]; then
        print_colored $GREEN "✅ Collection file found: $COLLECTION_FILE"
    else
        print_colored $RED "❌ Collection file not found: $COLLECTION_FILE"
        all_good=false
    fi
    
    # Check environment file
    if [ -f "$ENV_FILE" ]; then
        print_colored $GREEN "✅ Environment file found: $ENV_FILE"
    else
        print_colored $YELLOW "⚠️  Environment file not found: $ENV_FILE"
        print_colored $YELLOW "   Some tests may fail without proper API keys"
    fi
    
    # Check if server is running
    if curl -s "$BASE_URL" > /dev/null 2>&1; then
        print_colored $GREEN "✅ Flask server is running at $BASE_URL"
    else
        print_colored $YELLOW "⚠️  Flask server not detected at $BASE_URL"
        print_colored $YELLOW "   Make sure to start the server before running tests"
    fi
    
    if [ "$all_good" = false ]; then
        print_colored $RED "❌ Prerequisites check failed"
        exit 1
    fi
    
    print_colored $GREEN "✅ All prerequisites satisfied"
}

# Function to load environment variables
load_env_vars() {
    if [ -f "$ENV_FILE" ]; then
        print_colored $BLUE "📋 Loading environment variables from $ENV_FILE"
        export $(grep -v '^#' $ENV_FILE | xargs)
        
        # Validate API keys
        if [ -n "$VEEQO_API_KEY" ] && [ "$VEEQO_API_KEY" != "your-veeqo-api-key" ]; then
            print_colored $GREEN "✅ VEEQO_API_KEY configured"
        else
            print_colored $YELLOW "⚠️  VEEQO_API_KEY not configured properly"
        fi
        
        if [ -n "$EASYSHIP_API_KEY" ] && [ "$EASYSHIP_API_KEY" != "your-easyship-api-key" ]; then
            print_colored $GREEN "✅ EASYSHIP_API_KEY configured"
        else
            print_colored $YELLOW "⚠️  EASYSHIP_API_KEY not configured properly"
        fi
    else
        print_colored $YELLOW "⚠️  No environment file found, using default values"
        export VEEQO_API_KEY="test-key"
        export EASYSHIP_API_KEY="test-key"
    fi
}

# Function to create results directory
setup_results_directory() {
    mkdir -p "$RESULTS_DIR"
    print_colored $BLUE "📁 Results directory: $RESULTS_DIR"
}

# Function to run Newman tests
run_newman_tests() {
    local test_type=$1
    local additional_args=$2
    
    print_header "RUNNING NEWMAN TESTS"
    
    local html_report="$RESULTS_DIR/test_report_${test_type}_${TIMESTAMP}.html"
    local json_report="$RESULTS_DIR/test_results_${test_type}_${TIMESTAMP}.json"
    local junit_report="$RESULTS_DIR/junit_results_${test_type}_${TIMESTAMP}.xml"
    
    print_colored $BLUE "🧪 Executing test suite..."
    print_colored $WHITE "   Collection: $COLLECTION_FILE"
    print_colored $WHITE "   Base URL: $BASE_URL"
    print_colored $WHITE "   Reports: HTML, JSON, JUnit"
    
    # Build Newman command
    local newman_cmd="newman run $COLLECTION_FILE"
    newman_cmd="$newman_cmd --env-var base_url=$BASE_URL"
    newman_cmd="$newman_cmd --env-var VEEQO_API_KEY=$VEEQO_API_KEY"
    newman_cmd="$newman_cmd --env-var EASYSHIP_API_KEY=$EASYSHIP_API_KEY"
    newman_cmd="$newman_cmd --reporters cli,html,json,junit"
    newman_cmd="$newman_cmd --reporter-html-export $html_report"
    newman_cmd="$newman_cmd --reporter-json-export $json_report"
    newman_cmd="$newman_cmd --reporter-junit-export $junit_report"
    newman_cmd="$newman_cmd --delay-request 1000"
    newman_cmd="$newman_cmd --timeout-request 30000"
    newman_cmd="$newman_cmd $additional_args"
    
    # Execute Newman
    if eval $newman_cmd; then
        print_colored $GREEN "✅ Newman tests completed successfully"
        
        # Display report locations
        print_colored $CYAN "📊 Test Reports Generated:"
        print_colored $WHITE "   HTML Report: $html_report"
        print_colored $WHITE "   JSON Report: $json_report"
        print_colored $WHITE "   JUnit Report: $junit_report"
        
        # Try to extract summary from JSON report
        if [ -f "$json_report" ]; then
            extract_test_summary "$json_report"
        fi
        
        return 0
    else
        print_colored $RED "❌ Newman tests failed"
        return 1
    fi
}

# Function to extract test summary from JSON report
extract_test_summary() {
    local json_file=$1
    
    if command -v jq &> /dev/null; then
        print_colored $CYAN "📈 Test Summary:"
        
        local requests=$(jq -r '.run.stats.requests.total // 0' "$json_file")
        local tests=$(jq -r '.run.stats.tests.total // 0' "$json_file")
        local assertions=$(jq -r '.run.stats.assertions.total // 0' "$json_file")
        local passed=$(jq -r '.run.stats.assertions.passed // 0' "$json_file")
        local failed=$(jq -r '.run.stats.assertions.failed // 0' "$json_file")
        
        print_colored $WHITE "   Requests: $requests"
        print_colored $WHITE "   Tests: $tests"
        print_colored $WHITE "   Assertions: $assertions"
        
        if [ "$failed" -eq 0 ]; then
            print_colored $GREEN "   Passed: $passed/$assertions (100%)"
        else
            local pass_rate=$(( passed * 100 / assertions ))
            print_colored $YELLOW "   Passed: $passed/$assertions (${pass_rate}%)"
            print_colored $RED "   Failed: $failed"
        fi
    else
        print_colored $YELLOW "⚠️  Install 'jq' for detailed test summary"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -q, --quick             Run tests with minimal output"
    echo "  -v, --verbose           Run tests with verbose output"
    echo "  -f, --folder FOLDER     Run tests from specific folder only"
    echo "  -n, --iterations N      Run tests N times"
    echo "  --bail                  Stop on first test failure"
    echo "  --delay MS              Delay between requests in milliseconds"
    echo
    echo "Examples:"
    echo "  $0                      Run all tests with default settings"
    echo "  $0 --quick              Run tests with minimal output"
    echo "  $0 --folder 'Customer Management'  Run only customer management tests"
    echo "  $0 --iterations 3       Run all tests 3 times"
    echo
}

# Main execution
main() {
    local test_type="full"
    local additional_args=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -q|--quick)
                additional_args="$additional_args --reporter-cli-no-assertions"
                test_type="quick"
                shift
                ;;
            -v|--verbose)
                additional_args="$additional_args --verbose"
                test_type="verbose"
                shift
                ;;
            -f|--folder)
                additional_args="$additional_args --folder '$2'"
                test_type="folder_$(echo $2 | tr ' ' '_' | tr '[:upper:]' '[:lower:]')"
                shift 2
                ;;
            -n|--iterations)
                additional_args="$additional_args --iteration-count $2"
                test_type="iterations_$2"
                shift 2
                ;;
            --bail)
                additional_args="$additional_args --bail"
                shift
                ;;
            --delay)
                additional_args="$additional_args --delay-request $2"
                shift 2
                ;;
            *)
                print_colored $RED "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Main execution flow
    print_header "NEWMAN TEST RUNNER"
    print_colored $WHITE "Order & Warehouse Management System"
    print_colored $WHITE "Started at: $(date)"
    
    check_prerequisites
    load_env_vars
    setup_results_directory
    
    if run_newman_tests "$test_type" "$additional_args"; then
        print_header "TESTING COMPLETED SUCCESSFULLY"
        print_colored $GREEN "🎉 All tests completed!"
        print_colored $WHITE "Check the reports in: $RESULTS_DIR/"
        exit 0
    else
        print_header "TESTING FAILED"
        print_colored $RED "❌ Some tests failed"
        print_colored $WHITE "Check the reports for details: $RESULTS_DIR/"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"
