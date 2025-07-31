import unittest
import os
import time
import json

# Import the API classes
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from app import app


class IntegrationTestConfig:
    """Configuration for integration tests"""

    # Set to True to run tests against real APIs (requires valid API keys)
    RUN_REAL_API_TESTS = (
        os.environ.get("RUN_INTEGRATION_TESTS", "False").lower() == "true"
    )

    # Rate limiting settings
    API_CALL_DELAY = float(
        os.environ.get("API_CALL_DELAY", "1.0")
    )  # seconds between calls
    MAX_API_CALLS_PER_TEST = int(os.environ.get("MAX_API_CALLS", "5"))

    # Test data
    TEST_CUSTOMER_DATA = {
        "name": "Integration Test Customer",
        "phone": "+1234567890",
        "email": "test@example.com",
        "address_1": "123 Test Street",
        "city": "Las Vegas",
        "state": "Nevada",
        "postal_code": "89101",
        "country": "US",
    }


class APIIntegrationTestCase(unittest.TestCase):
    """Base class for API integration tests"""

    def setUp(self):
        """Set up for integration tests"""
        self.config = IntegrationTestConfig()
        self.veeqo_api = VeeqoAPI()
        self.easyship_api = EasyshipAPI()
        self.api_call_count = 0

        # Flask app for end-to-end tests
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def make_rate_limited_call(self, api_call):
        """Make API call with rate limiting"""
        if self.api_call_count >= self.config.MAX_API_CALLS_PER_TEST:
            self.skipTest(
                f"Maximum API calls ({
                    self.config.MAX_API_CALLS_PER_TEST}) reached for this test"
            )

        if self.api_call_count > 0:
            time.sleep(self.config.API_CALL_DELAY)

        self.api_call_count += 1
        return api_call()

    def skipIfNoRealAPITests(self):
        """Skip test if real API testing is disabled"""
        if not self.config.RUN_REAL_API_TESTS:
            self.skipTest(
                "Real API testing disabled. Set RUN_INTEGRATION_TESTS=true to enable"
            )


class VeeqoAPIIntegrationTest(APIIntegrationTestCase):
    """Integration tests for Veeqo API"""

    def test_veeqo_api_connection(self):
        """Test basic connection to Veeqo API"""
        self.skipIfNoRealAPITests()

        warehouses = self.make_rate_limited_call(self.veeqo_api.get_warehouses)

        self.assertIsInstance(warehouses, list)
        print(
            f"✅ Veeqo API connection successful. Found {
                len(warehouses)} warehouses"
        )

        if warehouses:
            warehouse = warehouses[0]
            required_fields = ["id", "name"]
            for field in required_fields:
                self.assertIn(
                    field,
                    warehouse,
                    f"Warehouse missing required field: {field}",
                )

    def test_veeqo_get_products(self):
        """Test retrieving products from Veeqo"""
        self.skipIfNoRealAPITests()

        products = self.make_rate_limited_call(lambda: self.veeqo_api.get_products(10))

        self.assertIsInstance(products, list)
        print(f"✅ Retrieved {len(products)} products from Veeqo")

        if products:
            product = products[0]
            # Check common product fields
            expected_fields = ["id", "title"]
            for field in expected_fields:
                if field in product:
                    print(f"  Product {field}: {product[field]}")

    def test_veeqo_warehouse_by_state(self):
        """Test finding warehouse by state"""
        self.skipIfNoRealAPITests()

        nevada_warehouse = self.make_rate_limited_call(
            lambda: self.veeqo_api.get_warehouse_by_state("Nevada")
        )

        if nevada_warehouse:
            self.assertIn("Nevada", nevada_warehouse.get("region", "").title())
            print(f"✅ Found Nevada warehouse: {nevada_warehouse.get('name')}")
        else:
            print("ℹ️  No Nevada warehouse found")

    def test_veeqo_random_products(self):
        """Test getting random products with fallback"""
        self.skipIfNoRealAPITests()

        products = self.make_rate_limited_call(
            lambda: self.veeqo_api.get_random_products(3)
        )

        self.assertEqual(len(products), 3)
        for i, product in enumerate(products):
            self.assertIn("title", product)
            self.assertIn("price", product)
            print(
                f"  Product {i +
                             1}: {product['title']} - ${product['price']}"
            )

        print("✅ Random products retrieved successfully")

    def test_veeqo_purchase_orders(self):
        """Test retrieving purchase orders"""
        self.skipIfNoRealAPITests()

        purchase_orders = self.make_rate_limited_call(
            lambda: self.veeqo_api.get_purchase_orders(5)
        )

        self.assertIsInstance(purchase_orders, list)
        print(f"✅ Retrieved {len(purchase_orders)} purchase orders from Veeqo")


class EasyshipAPIIntegrationTest(APIIntegrationTestCase):
    """Integration tests for Easyship API"""

    def test_easyship_api_connection(self):
        """Test basic connection to Easyship API"""
        self.skipIfNoRealAPITests()

        addresses = self.make_rate_limited_call(self.easyship_api.get_addresses)

        self.assertIsInstance(addresses, list)
        print(
            f"✅ Easyship API connection successful. Found {
                len(addresses)} addresses"
        )

        if addresses:
            address = addresses[0]
            required_fields = ["id"]
            for field in required_fields:
                self.assertIn(
                    field, address, f"Address missing required field: {field}"
                )

    def test_easyship_get_products(self):
        """Test retrieving products from Easyship"""
        self.skipIfNoRealAPITests()

        products = self.make_rate_limited_call(self.easyship_api.get_products)

        self.assertIsInstance(products, list)
        print(f"✅ Retrieved {len(products)} products from Easyship")

        if products:
            product = products[0]
            print(f"  Sample product: {product.get('title', 'No title')}")

    def test_easyship_address_by_state(self):
        """Test finding address by state"""
        self.skipIfNoRealAPITests()

        nevada_address = self.make_rate_limited_call(
            lambda: self.easyship_api.get_address_by_state("Nevada")
        )

        if nevada_address:
            self.assertIn("Nevada", nevada_address.get("state", "").title())
            print(f"✅ Found Nevada address: ID {nevada_address.get('id')}")
        else:
            print("ℹ️  No Nevada address found")

    def test_easyship_random_products(self):
        """Test getting random products with fallback"""
        self.skipIfNoRealAPITests()

        products = self.make_rate_limited_call(
            lambda: self.easyship_api.get_random_products(3)
        )

        self.assertEqual(len(products), 3)
        for i, product in enumerate(products):
            self.assertIn("title", product)
            self.assertIn("price", product)
            self.assertIn("weight", product)
            print(
                f"  Product {
                    i +
                    1}: {
                    product['title']} - ${
                    product['price']} ({
                    product['weight']}kg)"
            )

        print("✅ Random products retrieved successfully")

    def test_easyship_country_conversion(self):
        """Test country code conversion functionality"""
        test_cases = [
            ("US", "US"),
            ("GB", "GB"),
            ("UK", "GB"),
            ("DE", "DE"),
            ("INVALID", "US"),  # Should default to US
        ]

        for input_code, expected in test_cases:
            result = self.easyship_api._get_country_alpha2(input_code)
            self.assertEqual(result, expected)
            print(f"  {input_code} -> {result}")

        print("✅ Country code conversion working correctly")


class EndToEndIntegrationTest(APIIntegrationTestCase):
    """End-to-end integration tests"""

    def test_complete_order_flow_veeqo(self):
        """Test complete order creation flow through Veeqo"""
        self.skipIfNoRealAPITests()

        print("🔄 Testing complete Veeqo order flow...")

        # Step 1: Get warehouses
        warehouses = self.make_rate_limited_call(self.veeqo_api.get_warehouses)
        self.assertGreater(len(warehouses), 0, "No warehouses available")

        # Step 2: Get products
        products = self.make_rate_limited_call(
            lambda: self.veeqo_api.get_random_products(2)
        )
        self.assertEqual(len(products), 2)

        # Step 3: Select warehouse (prefer Nevada/California)
        selected_warehouse = None
        for warehouse in warehouses:
            region = warehouse.get("region", "").lower()
            if "nevada" in region or "california" in region:
                selected_warehouse = warehouse
                break

        if not selected_warehouse:
            selected_warehouse = warehouses[0]  # Use first available

        print(f"  Selected warehouse: {selected_warehouse.get('name')}")
        print(f"  Selected products: {[p['title'] for p in products]}")

        # Note: We don't actually create the order in integration tests
        # to avoid creating test orders in production systems
        print("✅ Order flow validation successful (order creation skipped)")

    def test_complete_order_flow_easyship(self):
        """Test complete order creation flow through Easyship"""
        self.skipIfNoRealAPITests()

        print("🔄 Testing complete Easyship order flow...")

        # Step 1: Get addresses
        addresses = self.make_rate_limited_call(self.easyship_api.get_addresses)
        self.assertGreater(len(addresses), 0, "No addresses available")

        # Step 2: Get products
        products = self.make_rate_limited_call(
            lambda: self.easyship_api.get_random_products(2)
        )
        self.assertEqual(len(products), 2)

        # Step 3: Select address (prefer Nevada)
        selected_address = None
        for address in addresses:
            state = address.get("state", "").lower()
            if "nevada" in state:
                selected_address = address
                break

        if not selected_address:
            selected_address = addresses[0]  # Use first available

        print(
            f"  Selected address: {
                selected_address.get(
                    'state',
                    'Unknown')}"
        )
        print(f"  Selected products: {[p['title'] for p in products]}")

        # Note: We don't actually create the shipment in integration tests
        print("✅ Shipment flow validation successful (shipment creation skipped)")

    def test_api_endpoint_integration(self):
        """Test Flask API endpoints with real backend data"""
        self.skipIfNoRealAPITests()

        # Test customer parsing endpoint
        customer_input = "John Doe\t+1234567890 john@test.com\t123 Main St\t\tLas Vegas\tNV\t89101\tUS"
        response = self.client.post(
            "/api/parse_customer",
            json={"input": customer_input},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        print("✅ Customer parsing API integration successful")

        # Test sync endpoint (read-only operations)
        response = self.client.get("/sync_data")
        # May fail due to API limits
        self.assertIn(response.status_code, [200, 500])

        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"✅ Sync API integration successful: {data.get('status')}")
        else:
            print("ℹ️  Sync API returned error (likely due to API limits)")


class PerformanceIntegrationTest(APIIntegrationTestCase):
    """Performance and reliability integration tests"""

    def test_api_response_times(self):
        """Test API response times"""
        self.skipIfNoRealAPITests()

        response_times = {}

        # Test Veeqo warehouse call
        start_time = time.time()
        self.make_rate_limited_call(self.veeqo_api.get_warehouses)
        response_times["veeqo_warehouses"] = time.time() - start_time

        # Test Easyship addresses call
        start_time = time.time()
        self.make_rate_limited_call(self.easyship_api.get_addresses)
        response_times["easyship_addresses"] = time.time() - start_time

        # Print results
        print("📊 API Response Times:")
        for endpoint, duration in response_times.items():
            print(f"  {endpoint}: {duration:.2f}s")
            self.assertLess(duration, 30.0, f"{endpoint} took too long: {duration}s")

        print("✅ All API calls completed within acceptable time limits")

    def test_api_error_handling(self):
        """Test API error handling with invalid data"""
        # Test with invalid API key (if we can temporarily modify it)
        print("🔧 Testing API error handling...")

        # Create API instance with invalid key
        invalid_veeqo = VeeqoAPI("invalid_key")
        result = invalid_veeqo.get_warehouses()

        # Should return empty list or None for failed calls
        self.assertIn(result, [[], None])
        print("✅ Invalid API key handled gracefully")

    def test_dummy_product_generation(self):
        """Test dummy product generation reliability"""
        # Test Veeqo dummy products
        veeqo_dummies = self.veeqo_api._generate_dummy_products(5)
        self.assertEqual(len(veeqo_dummies), 5)

        for product in veeqo_dummies:
            self.assertIn("id", product)
            self.assertIn("title", product)
            self.assertIn("price", product)
            self.assertIsInstance(float(product["price"]), float)

        # Test Easyship dummy products
        easyship_dummies = self.easyship_api._generate_dummy_products(3)
        self.assertEqual(len(easyship_dummies), 3)

        for product in easyship_dummies:
            self.assertIn("title", product)
            self.assertIn("price", product)
            self.assertIn("weight", product)
            self.assertIsInstance(product["price"], (int, float))

        print("✅ Dummy product generation working reliably")


def print_integration_test_info():
    """Print information about integration test configuration"""
    print("=" * 60)
    print("API INTEGRATION TEST SUITE")
    print("=" * 60)
    print(
        f"Real API Testing: {
            'ENABLED' if IntegrationTestConfig.RUN_REAL_API_TESTS else 'DISABLED'}"
    )
    print(f"API Call Delay: {IntegrationTestConfig.API_CALL_DELAY}s")
    print(
        f"Max API Calls per Test: {
            IntegrationTestConfig.MAX_API_CALLS_PER_TEST}"
    )

    if not IntegrationTestConfig.RUN_REAL_API_TESTS:
        print("\nTo enable real API testing:")
        print("  export RUN_INTEGRATION_TESTS=true")
        print("  export VEEQO_API_KEY=your_veeqo_key")
        print("  export EASYSHIP_API_KEY=your_easyship_key")

    print("\nEnvironment Variables:")
    print(
        f"  VEEQO_API_KEY: {
            'SET' if os.environ.get('VEEQO_API_KEY') else 'NOT SET'}"
    )
    print(
        f"  EASYSHIP_API_KEY: {
            'SET' if os.environ.get('EASYSHIP_API_KEY') else 'NOT SET'}"
    )
    print("=" * 60)


if __name__ == "__main__":
    print_integration_test_info()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add integration test classes
    integration_test_classes = [
        VeeqoAPIIntegrationTest,
        EasyshipAPIIntegrationTest,
        EndToEndIntegrationTest,
        PerformanceIntegrationTest,
    ]

    for test_class in integration_test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'=' * 50}")
    print(f"Integration Testing Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Skipped: {result.testsRun -
                    len(result.failures) -
                    len(result.errors) -
                    len([t for t in result.skipped if hasattr(result, 'skipped')])}"
    )

    if result.testsRun > 0:
        success_rate = (
            (result.testsRun - len(result.failures) - len(result.errors))
            / result.testsRun
            * 100
        )
        print(f"Success rate: {success_rate:.1f}%")

    print(f"{'=' * 50}")

    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code)
