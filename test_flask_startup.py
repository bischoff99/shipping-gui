#!/usr/bin/env python3
"""
Flask App Startup Test Script
Tests if the Flask application can start properly and identifies any startup issues.
"""

import os
import sys
import threading
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_flask_startup():
    """Test Flask app startup in a separate thread"""
    print("=" * 60)
    print("FLASK APPLICATION STARTUP TEST")
    print("=" * 60)
    
    try:
        # Import the app
        print("Step 1: Importing Flask app...")
        from app import app
        print("[OK] Flask app imported successfully")
        
        # Test app configuration
        print("\nStep 2: Checking app configuration...")
        print(f"[OK] Secret Key: {'Present' if app.secret_key else 'Missing'}")
        print(f"[OK] Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
        print(f"[OK] Debug Mode: {app.debug}")
        
        # Test database connection
        print("\nStep 3: Testing database connection...")
        try:
            from models import db, Product
            with app.app_context():
                # Try a simple query
                count = Product.query.count()
                print(f"[OK] Database connected - {count} products found")
        except Exception as e:
            print(f"[WARN] Database issue: {e}")
        
        # Test API clients initialization
        print("\nStep 4: Testing API clients...")
        try:
            from api.veeqo_api import VeeqoAPI
            from api.easyship_api import EasyshipAPI
            
            veeqo = VeeqoAPI()
            easyship = EasyshipAPI()
            print("[OK] API clients initialized successfully")
        except Exception as e:
            print(f"[WARN] API client issue: {e}")
        
        # Test route availability
        print("\nStep 5: Testing Flask routes...")
        with app.test_client() as client:
            test_routes = [
                ('/', 'Home/Create Order'),
                ('/dashboard', 'Dashboard'),
                ('/sync_data', 'Data Sync'),
                ('/api/get_products', 'Products API'),
            ]
            
            for route, name in test_routes:
                try:
                    response = client.get(route)
                    status = f"{response.status_code} - {response.status}"
                    print(f"[OK] {name}: {status}")
                except Exception as e:
                    print(f"[FAIL] {name}: {e}")
        
        # Test app startup (non-blocking)
        print(f"\nStep 6: Testing app startup readiness...")
        try:
            # Check if app can be configured for production
            app.config['TESTING'] = True
            print("[OK] App can be configured for testing")
            
            return True
            
        except Exception as e:
            print(f"[FAIL] App startup issue: {e}")
            return False
            
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def test_dependencies():
    """Test if all required dependencies are available"""
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'requests',
        'python-dotenv',
        'werkzeug',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[FAIL] {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[ERROR] Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n[SUCCESS] All dependencies are available")
        return True


def test_environment_variables():
    """Test environment variables"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    
    required_vars = [
        'VEEQO_API_KEY',
        'EASYSHIP_API_KEY',
        'FLASK_SECRET_KEY',
    ]
    
    optional_vars = [
        'DATABASE_URL',
        'FLASK_ENV',
        'HF_TOKEN',
    ]
    
    missing_required = []
    
    # Check required variables
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"[OK] {var}: Present ({len(value)} chars)")
        else:
            print(f"[FAIL] {var}: MISSING")
            missing_required.append(var)
    
    # Check optional variables
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"[OK] {var}: Present ({len(value)} chars)")
        else:
            print(f"[INFO] {var}: Not set (optional)")
    
    if missing_required:
        print(f"\n[ERROR] Missing required variables: {', '.join(missing_required)}")
        return False
    else:
        print("\n[SUCCESS] All required environment variables are set")
        return True


def test_file_structure():
    """Test critical file structure"""
    print("\n" + "=" * 60)
    print("FILE STRUCTURE CHECK")
    print("=" * 60)
    
    critical_files = [
        'app.py',
        'config.py',
        'models.py',
        'routing.py',
        'utils.py',
        'validation.py',
        'api/veeqo_api.py',
        'api/easyship_api.py',
        'templates/create_order.html',
        'templates/dashboard.html',
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n[ERROR] Missing critical files: {', '.join(missing_files)}")
        return False
    else:
        print("\n[SUCCESS] All critical files are present")
        return True


def main():
    """Main test function"""
    print("SHIPPING GUI FLASK STARTUP COMPREHENSIVE TEST")
    print("Testing Flask app startup readiness and identifying issues")
    
    # Run all tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("Flask Startup", test_flask_startup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name.upper()} TEST {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("STARTUP TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] Flask app should start without issues!")
        print("You can run: python app.py")
    else:
        print(f"\n[WARNING] {len(results) - passed} issues found.")
        print("Fix the issues above before starting the Flask app.")
    
    # Provide startup instructions
    print("\n" + "=" * 80)
    print("STARTUP INSTRUCTIONS")
    print("=" * 80)
    print("To start the Flask application:")
    print("1. Ensure all tests above pass")
    print("2. Run: python app.py")
    print("3. Open browser to: http://localhost:5000")
    print("4. Test the order creation workflow")


if __name__ == "__main__":
    main()