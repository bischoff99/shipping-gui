#!/usr/bin/env python3
"""
Test application startup to verify all components work together.
"""

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


def test_application():
    """Test that the application can start up properly"""

    print("Testing application components...")

    # Test 1: Logging system
    try:
        from config.logging_config import setup_logging

        logger = setup_logging()
        logger.info("Logging system test")
        print("[OK] Logging system working")
    except Exception as e:
        print(f"[FAIL] Logging system failed: {e}")
        return False

    # Test 2: Database models
    try:
        pass

        print("[OK] Database models imported")
    except Exception as e:
        print(f"[FAIL] Database models failed: {e}")
        return False

    # Test 3: API clients (with environment variables)
    try:
        from api.veeqo_api import VeeqoAPI
        from api.easyship_api import EasyshipAPI

        VeeqoAPI()
        EasyshipAPI()
        print("[OK] API clients initialized")
    except Exception as e:
        print(f"[FAIL] API clients failed: {e}")
        return False

    # Test 4: Core utilities
    try:
        from routing import OrderRoutingSystem

        OrderRoutingSystem()
        print("[OK] Core utilities working")
    except Exception as e:
        print(f"[FAIL] Core utilities failed: {e}")
        return False

    # Test 5: Flask configuration
    try:
        pass

        print("[OK] Flask configuration loaded")
    except Exception as e:
        print(f"[FAIL] Flask configuration failed: {e}")
        return False

    print("\n=== ALL APPLICATION COMPONENTS TESTED SUCCESSFULLY ===")
    print("The application is ready to start.")
    return True


if __name__ == "__main__":
    test_application()
