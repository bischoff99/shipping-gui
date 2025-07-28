#!/usr/bin/env python3
"""
Automated Postman Testing Script
Order & Warehouse Management System

This script automates the complete Postman testing process including:
- Environment verification
- Flask server startup
- Newman test execution
- Results reporting
"""

import os
import sys
import json
import time
import subprocess
import threading
import requests
from datetime import datetime
from pathlib import Path

class TestConfig:
    """Configuration for automated testing"""
    BASE_URL = "http://localhost:5000"
    FLASK_APP = "app.py"
    COLLECTION_FILE = "postman_collection.json"
    ENV_FILE = ".env"
    RESULTS_DIR = "test_results"
    SERVER_STARTUP_TIMEOUT = 30  # seconds
    SERVER_CHECK_INTERVAL = 2   # seconds

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message, color=Colors.WHITE):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.END}")

def print_header(title):
    """Print formatted header"""
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f" {title}", Colors.BOLD + Colors.WHITE)
    print_colored("=" * 60, Colors.CYAN)
    print()

class EnvironmentChecker:
    """Verify testing environment prerequisites"""
    
    @staticmethod
    def check_python_version():
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print_colored("❌ Python 3.7+ required", Colors.RED)
            return False
        print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
        return True
    
    @staticmethod
    def check_dependencies():
        """Check if required Python packages are installed"""
        required_packages = ['flask', 'requests', 'python-dotenv']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print_colored(f"✅ {package} installed", Colors.GREEN)
            except ImportError:
                print_colored(f"❌ {package} missing", Colors.RED)
                missing_packages.append(package)
        
        if missing_packages:
            print_colored("\nInstall missing packages:", Colors.YELLOW)
            print_colored(f"pip install {' '.join(missing_packages)}", Colors.WHITE)
            return False
        
        return True
    
    @staticmethod
    def check_newman():
        """Check if Newman CLI is available"""
        try:
            result = subprocess.run(['newman', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print_colored(f"✅ Newman {version}", Colors.GREEN)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print_colored("⚠️  Newman CLI not found", Colors.YELLOW)
        print_colored("Install with: npm install -g newman", Colors.WHITE)
        return False
    
    @staticmethod
    def check_files():
        """Check if required files exist"""
        required_files = [
            TestConfig.FLASK_APP,
            TestConfig.COLLECTION_FILE,
            'requirements.txt'
        ]
        
        all_exist = True
        for file_path in required_files:
            if Path(file_path).exists():
                print_colored(f"✅ {file_path} found", Colors.GREEN)
            else:
                print_colored(f"❌ {file_path} missing", Colors.RED)
                all_exist = False
        
        return all_exist
    
    @staticmethod
    def check_environment_variables():
        """Check environment variables configuration"""
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['VEEQO_API_KEY', 'EASYSHIP_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value.strip() and not value.startswith('your-'):
                print_colored(f"✅ {var} configured", Colors.GREEN)
            else:
                print_colored(f"⚠️  {var} not configured", Colors.YELLOW)
                missing_vars.append(var)
        
        if missing_vars:
            print_colored("\nNote: Some API tests may fail without valid API keys", Colors.YELLOW)
        
        return True  # Don't fail on missing API keys, just warn

class FlaskServerManager:
    """Manage Flask server lifecycle for testing"""
    
    def __init__(self):
        self.server_process = None
        self.server_thread = None
        self.server_running = False
    
    def start_server(self):
        """Start Flask server in background"""
        print_colored("🚀 Starting Flask server...", Colors.BLUE)
        
        try:
            # Start server in subprocess
            self.server_process = subprocess.Popen(
                [sys.executable, TestConfig.FLASK_APP],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            if self._wait_for_server():
                print_colored("✅ Flask server started successfully", Colors.GREEN)
                self.server_running = True
                return True
            else:
                print_colored("❌ Flask server failed to start", Colors.RED)
                self._stop_server()
                return False
                
        except Exception as e:
            print_colored(f"❌ Error starting server: {e}", Colors.RED)
            return False
    
    def _wait_for_server(self):
        """Wait for server to become available"""
        start_time = time.time()
        
        while time.time() - start_time < TestConfig.SERVER_STARTUP_TIMEOUT:
            try:
                response = requests.get(f"{TestConfig.BASE_URL}/", timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK, means server is running
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(TestConfig.SERVER_CHECK_INTERVAL)
            print_colored("⏳ Waiting for server...", Colors.YELLOW)
        
        return False
    
    def _stop_server(self):
        """Stop Flask server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            finally:
                self.server_process = None
        
        self.server_running = False
    
    def stop_server(self):
        """Public method to stop server"""
        if self.server_running:
            print_colored("🛑 Stopping Flask server...", Colors.BLUE)
            self._stop_server()
            print_colored("✅ Flask server stopped", Colors.GREEN)

class NewmanTestRunner:
    """Execute Newman tests and collect results"""
    
    def __init__(self):
        self.results = {}
        self.test_start_time = None
        self.test_end_time = None
    
    def run_tests(self):
        """Execute Newman tests"""
        print_colored("🧪 Running Postman tests with Newman...", Colors.BLUE)
        
        # Create results directory
        Path(TestConfig.RESULTS_DIR).mkdir(exist_ok=True)
        
        # Set up environment variables for Newman
        env_vars = self._get_environment_variables()
        
        # Build Newman command
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = f"{TestConfig.RESULTS_DIR}/test_report_{timestamp}.html"
        json_report = f"{TestConfig.RESULTS_DIR}/test_results_{timestamp}.json"
        
        newman_cmd = [
            'newman', 'run', TestConfig.COLLECTION_FILE,
            '--reporters', 'cli,html,json',
            '--reporter-html-export', html_report,
            '--reporter-json-export', json_report,
            '--delay-request', '1000',  # 1 second delay between requests
            '--timeout-request', '30000'  # 30 second timeout
        ]
        
        # Add environment variables
        for key, value in env_vars.items():
            newman_cmd.extend(['--env-var', f"{key}={value}"])
        
        try:
            self.test_start_time = datetime.now()
            
            # Run Newman
            result = subprocess.run(
                newman_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for entire test suite
            )
            
            self.test_end_time = datetime.now()
            
            # Parse results
            self._parse_results(result, json_report)
            
            print_colored(f"📊 Test reports generated:", Colors.GREEN)
            print_colored(f"   HTML: {html_report}", Colors.WHITE)
            print_colored(f"   JSON: {json_report}", Colors.WHITE)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print_colored("❌ Newman tests timed out", Colors.RED)
            return False
        except FileNotFoundError:
            print_colored("❌ Newman not found. Install with: npm install -g newman", Colors.RED)
            return False
        except Exception as e:
            print_colored(f"❌ Error running Newman tests: {e}", Colors.RED)
            return False
    
    def _get_environment_variables(self):
        """Get environment variables for Newman"""
        from dotenv import load_dotenv
        load_dotenv()
        
        return {
            'base_url': TestConfig.BASE_URL,
            'VEEQO_API_KEY': os.getenv('VEEQO_API_KEY', 'test-key'),
            'EASYSHIP_API_KEY': os.getenv('EASYSHIP_API_KEY', 'test-key')
        }
    
    def _parse_results(self, result, json_report_path):
        """Parse Newman test results"""
        self.results = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'start_time': self.test_start_time,
            'end_time': self.test_end_time,
            'duration': (self.test_end_time - self.test_start_time).total_seconds(),
            'summary': {}
        }
        
        # Try to parse JSON report for detailed results
        try:
            if Path(json_report_path).exists():
                with open(json_report_path, 'r') as f:
                    json_data = json.load(f)
                    
                run_stats = json_data.get('run', {}).get('stats', {})
                self.results['summary'] = {
                    'requests': run_stats.get('requests', {}).get('total', 0),
                    'tests': run_stats.get('tests', {}).get('total', 0),
                    'assertions': run_stats.get('assertions', {}).get('total', 0),
                    'passed': run_stats.get('assertions', {}).get('passed', 0),
                    'failed': run_stats.get('assertions', {}).get('failed', 0)
                }
        except Exception:
            # If JSON parsing fails, extract from stdout
            self._parse_stdout_results()
    
    def _parse_stdout_results(self):
        """Parse results from Newman stdout"""
        stdout = self.results.get('stdout', '')
        
        # Extract basic stats from Newman output
        import re
        
        requests_match = re.search(r'requests\s+│\s+(\d+)', stdout)
        tests_match = re.search(r'test-scripts\s+│\s+(\d+)', stdout)
        assertions_match = re.search(r'assertions\s+│\s+(\d+)', stdout)
        
        self.results['summary'] = {
            'requests': int(requests_match.group(1)) if requests_match else 0,
            'tests': int(tests_match.group(1)) if tests_match else 0,
            'assertions': int(assertions_match.group(1)) if assertions_match else 0,
            'passed': 0,  # Would need more complex parsing
            'failed': 0
        }

class PostmanTestSuite:
    """Main test suite orchestrator"""
    
    def __init__(self):
        self.env_checker = EnvironmentChecker()
        self.server_manager = FlaskServerManager()
        self.test_runner = NewmanTestRunner()
    
    def run_complete_test_suite(self):
        """Execute complete testing workflow"""
        print_header("POSTMAN AUTOMATED TESTING SUITE")
        print_colored("Order & Warehouse Management System", Colors.BOLD)
        print_colored(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.WHITE)
        print()
        
        try:
            # Step 1: Environment verification
            print_header("STEP 1: ENVIRONMENT VERIFICATION")
            if not self._verify_environment():
                print_colored("❌ Environment verification failed", Colors.RED)
                return False
            
            # Step 2: Start Flask server
            print_header("STEP 2: FLASK SERVER STARTUP")
            if not self.server_manager.start_server():
                print_colored("❌ Server startup failed", Colors.RED)
                return False
            
            # Step 3: Run tests
            print_header("STEP 3: POSTMAN TEST EXECUTION")
            test_success = self.test_runner.run_tests()
            
            # Step 4: Generate report
            print_header("STEP 4: TEST RESULTS SUMMARY")
            self._generate_report()
            
            return test_success
            
        except KeyboardInterrupt:
            print_colored("\n⚠️  Testing interrupted by user", Colors.YELLOW)
            return False
        except Exception as e:
            print_colored(f"❌ Unexpected error: {e}", Colors.RED)
            return False
        finally:
            # Always stop server
            self.server_manager.stop_server()
    
    def _verify_environment(self):
        """Verify all environment prerequisites"""
        checks = [
            ("Python Version", self.env_checker.check_python_version),
            ("Dependencies", self.env_checker.check_dependencies),
            ("Required Files", self.env_checker.check_files),
            ("Environment Variables", self.env_checker.check_environment_variables),
            ("Newman CLI", self.env_checker.check_newman)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print_colored(f"\n🔍 Checking {check_name}:", Colors.BLUE)
            if not check_func():
                all_passed = False
        
        return all_passed
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        results = self.test_runner.results
        summary = results.get('summary', {})
        
        print_colored("📋 TEST EXECUTION SUMMARY", Colors.BOLD + Colors.CYAN)
        print_colored("-" * 40, Colors.CYAN)
        
        # Basic info
        print_colored(f"Status: {'✅ SUCCESS' if results.get('success') else '❌ FAILED'}", 
                     Colors.GREEN if results.get('success') else Colors.RED)
        
        if results.get('start_time') and results.get('end_time'):
            print_colored(f"Duration: {results.get('duration', 0):.2f} seconds", Colors.WHITE)
        
        # Test statistics
        if summary:
            print_colored(f"Requests: {summary.get('requests', 0)}", Colors.WHITE)
            print_colored(f"Tests: {summary.get('tests', 0)}", Colors.WHITE)
            print_colored(f"Assertions: {summary.get('assertions', 0)}", Colors.WHITE)
            
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            total = passed + failed
            
            if total > 0:
                pass_rate = (passed / total) * 100
                print_colored(f"Passed: {passed}/{total} ({pass_rate:.1f}%)", 
                             Colors.GREEN if pass_rate >= 80 else Colors.YELLOW)
                
                if failed > 0:
                    print_colored(f"Failed: {failed}", Colors.RED)
        
        # Recommendations
        print_colored("\n💡 RECOMMENDATIONS:", Colors.BOLD + Colors.YELLOW)
        if results.get('success'):
            print_colored("• All tests completed successfully!", Colors.GREEN)
            print_colored("• Review HTML report for detailed results", Colors.WHITE)
        else:
            print_colored("• Check server logs for errors", Colors.WHITE)
            print_colored("• Verify API keys are valid", Colors.WHITE)
            print_colored("• Ensure all dependencies are installed", Colors.WHITE)
        
        print_colored("\n📁 Find detailed reports in:", Colors.BLUE)
        print_colored(f"   {TestConfig.RESULTS_DIR}/", Colors.WHITE)

def main():
    """Main entry point"""
    test_suite = PostmanTestSuite()
    success = test_suite.run_complete_test_suite()
    
    print_header("TESTING COMPLETE")
    if success:
        print_colored("🎉 All tests completed successfully!", Colors.GREEN + Colors.BOLD)
        sys.exit(0)
    else:
        print_colored("❌ Some tests failed or encountered errors", Colors.RED + Colors.BOLD)
        sys.exit(1)

if __name__ == "__main__":
    main()
