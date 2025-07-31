#!/usr/bin/env python3
"""
Comprehensive Test Runner for API Testing Suite

This script runs different types of tests for the Order & Warehouse Management System:
- Unit tests (default): Mock-based tests for API logic and responses
- Integration tests: Real API calls (requires valid API keys)
- All tests: Both unit and integration tests

Usage:
    python run_tests.py                    # Run unit tests only
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --all              # Run all tests
    python run_tests.py --help             # Show help
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime


class TestRunner:
    """Main test runner class"""

    def __init__(self):
        self.start_time = None
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0

    def print_banner(self, title):
        """Print a formatted banner"""
        print("\n" + "=" * 70)
        print(f"{title:^70}")
        print("=" * 70)

    def print_section(self, title):
        """Print a section header"""
        print(f"\n{'-' * 50}")
        print(f"{title}")
        print(f"{'-' * 50}")

    def check_environment(self):
        """Check environment setup"""
        self.print_section("Environment Check")

        # Check Python version
        python_version = f"{
            sys.version_info.major}.{
            sys.version_info.minor}.{
            sys.version_info.micro}"
        print(f"✅ Python version: {python_version}")

        # Check required files
        required_files = [
            "app.py",
            "api/veeqo_api.py",
            "api/easyship_api.py",
            "test_api_responses.py",
            "test_api_integration.py",
        ]

        missing_files = []
        for file in required_files:
            if os.path.exists(file):
                print(f"✅ Found: {file}")
            else:
                print(f"❌ Missing: {file}")
                missing_files.append(file)

        if missing_files:
            print(f"\n❌ Missing required files: {missing_files}")
            return False

        # Check API keys for integration tests
        veeqo_key = os.environ.get("VEEQO_API_KEY")
        easyship_key = os.environ.get("EASYSHIP_API_KEY")

        print(f"\n🔑 API Keys:")
        print(f"  VEEQO_API_KEY: {'SET' if veeqo_key else 'NOT SET'}")
        print(f"  EASYSHIP_API_KEY: {'SET' if easyship_key else 'NOT SET'}")

        return True

    def run_unit_tests(self):
        """Run unit tests"""
        self.print_section("Running Unit Tests")
        print("🧪 Executing mock-based API response tests...")

        try:
            result = subprocess.run(
                [sys.executable, "test_api_responses.py"],
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running unit tests: {e}")
            return False

    def run_integration_tests(self):
        """Run integration tests"""
        self.print_section("Running Integration Tests")

        # Check if integration testing is enabled
        if not os.environ.get("RUN_INTEGRATION_TESTS", "").lower() == "true":
            print("ℹ️  Integration tests disabled.")
            print("   To enable: export RUN_INTEGRATION_TESTS=true")
            return True

        print("🌐 Executing real API integration tests...")
        print(
            "⚠️  This will make real API calls - please ensure you're using test/staging keys!"
        )

        try:
            result = subprocess.run(
                [sys.executable, "test_api_integration.py"],
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running integration tests: {e}")
            return False

    def run_specific_test(self, test_file, test_class=None, test_method=None):
        """Run a specific test file, class, or method"""
        cmd = [sys.executable, test_file]

        if test_class:
            if test_method:
                cmd.extend([f"{test_class}.{test_method}"])
            else:
                cmd.extend([test_class])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running specific test: {e}")
            return False

    def generate_test_report(self, unit_success, integration_success, integration_run):
        """Generate final test report"""
        self.print_banner("TEST REPORT")

        print(
            f"Test execution completed at: {
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if self.start_time:
            duration = time.time() - self.start_time
            print(f"Total execution time: {duration:.2f} seconds")

        print(f"\nTest Results:")
        print(f"  Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")

        if integration_run:
            print(
                f"  Integration Tests: {
                    '✅ PASSED' if integration_success else '❌ FAILED'}"
            )
        else:
            print(f"  Integration Tests: ⏭️  SKIPPED")

        overall_success = unit_success and (
            integration_success if integration_run else True
        )
        print(
            f"\nOverall Result: {
                '✅ SUCCESS' if overall_success else '❌ FAILURE'}"
        )

        if not overall_success:
            print("\n💡 Tips for fixing test failures:")
            print("  1. Check API keys are valid and have proper permissions")
            print("  2. Ensure all required Python packages are installed")
            print("  3. Check network connectivity for integration tests")
            print("  4. Review error messages above for specific issues")

        return overall_success


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Test runner for Order & Warehouse Management System API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run unit tests only
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --all              # Run all tests
  python run_tests.py --specific test_api_responses.py FlaskAPIEndpointsTest

Environment Variables:
  RUN_INTEGRATION_TESTS=true    # Enable integration tests
  VEEQO_API_KEY=your_key       # Veeqo API key
  EASYSHIP_API_KEY=your_key    # Easyship API key
  API_CALL_DELAY=1.0           # Delay between API calls (seconds)
  MAX_API_CALLS=5              # Max API calls per integration test
        """,
    )

    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--unit", action="store_true", help="Run unit tests only (default)"
    )
    test_group.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    test_group.add_argument(
        "--all", action="store_true", help="Run both unit and integration tests"
    )
    test_group.add_argument(
        "--specific",
        nargs="+",
        metavar=("FILE", "CLASS", "METHOD"),
        help="Run specific test file, class, or method",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--check-env", action="store_true", help="Only check environment setup"
    )

    return parser.parse_args()


def main():
    """Main test runner function"""
    args = parse_arguments()
    runner = TestRunner()
    runner.start_time = time.time()

    # Print banner
    runner.print_banner("API TESTING SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check environment
    if not runner.check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return 1

    if args.check_env:
        print("\n✅ Environment check completed successfully.")
        return 0

    # Determine what tests to run
    run_unit = True
    run_integration = False

    if args.integration:
        run_unit = False
        run_integration = True
    elif args.all:
        run_unit = True
        run_integration = True
    elif args.specific:
        # Handle specific test execution
        runner.print_section("Running Specific Test")
        test_file = args.specific[0]
        test_class = args.specific[1] if len(args.specific) > 1 else None
        test_method = args.specific[2] if len(args.specific) > 2 else None

        success = runner.run_specific_test(test_file, test_class, test_method)
        return 0 if success else 1

    # Execute tests
    unit_success = True
    integration_success = True

    if run_unit:
        unit_success = runner.run_unit_tests()

    if run_integration:
        integration_success = runner.run_integration_tests()

    # Generate report
    overall_success = runner.generate_test_report(
        unit_success, integration_success, run_integration
    )

    return 0 if overall_success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
