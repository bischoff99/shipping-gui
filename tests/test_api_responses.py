from routing import OrderRoutingSystem, RoutingDecision
from utils import parse_customer_input, normalize_customer_data
from validation import validate_customer_data
from api.easyship_api import EasyshipAPI
from api.veeqo_api import VeeqoAPI
from app import app
import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class APITestCase(unittest.TestCase):
    """Base test case with common setup"""

    def setUp(self):
        """Set up test client and mock data"""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Sample test data
        self.sample_customer_data = {
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john@example.com",
            "address_1": "123 Main St",
            "city": "Las Vegas",
            "state": "Nevada",
            "postal_code": "89101",
            "country": "US",
        }

        self.sample_warehouse = {
            "id": 1,
            "name": "Nevada Warehouse",
            "region": "Nevada",
            "address_line_1": "456 Warehouse Ave",
        }

        self.sample_products = [
            {
                "id": "prod1",
                "title": "Fashion Dress",
                "price": "25.00",
                "weight": 0.5,
            },
            {
                "id": "prod2",
                "title": "Designer Jeans",
                "price": "45.00",
                "weight": 0.8,
            },
        ]

    def assertJSONResponse(self, response, expected_status=200):
        """Helper to assert JSON response format"""
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.content_type, "application/json")
        return json.loads(response.data)


class FlaskAPIEndpointsTest(APITestCase):
    """Test Flask API endpoints and their responses"""

    def test_api_parse_customer_success(self):
        """Test successful customer parsing API"""
        test_input = "John Doe\t+1234567890 john@example.com\t123 Main St\t\tLas Vegas\tNevada\t89101\tUS"

        response = self.client.post(
            "/api/parse_customer",
            json={"input": test_input},
            content_type="application/json",
        )

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertEqual(data["data"]["name"], "John Doe")
        self.assertEqual(data["data"]["email"], "john@example.com")

    def test_api_parse_customer_invalid_input(self):
        """Test customer parsing API with invalid input"""
        response = self.client.post(
            "/api/parse_customer",
            json={"input": ""},
            content_type="application/json",
        )

        data = self.assertJSONResponse(response, 400)
        self.assertEqual(data["status"], "error")
        self.assertIn("message", data)

    def test_api_parse_customer_no_json(self):
        """Test customer parsing API without JSON data"""
        response = self.client.post("/api/parse_customer")

        data = self.assertJSONResponse(response, 400)
        self.assertEqual(data["status"], "error")

    @patch("app.veeqo_api.get_warehouses")
    @patch("app.easyship_api.get_addresses")
    @patch("app.veeqo_api.get_products")
    @patch("app.easyship_api.get_products")
    def test_sync_data_success(
        self,
        mock_easyship_products,
        mock_veeqo_products,
        mock_easyship_addresses,
        mock_veeqo_warehouses,
    ):
        """Test successful data synchronization"""
        # Mock API responses
        mock_veeqo_warehouses.return_value = [self.sample_warehouse]
        mock_easyship_addresses.return_value = [{"id": 1, "name": "Easyship Address"}]
        mock_veeqo_products.return_value = self.sample_products
        mock_easyship_products.return_value = [{"title": "Easyship Product"}]

        response = self.client.get("/sync_data")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertIn("veeqo_warehouses", data)
        self.assertIn("easyship_addresses", data)
        self.assertEqual(data["veeqo_warehouses"], 1)
        self.assertEqual(data["easyship_addresses"], 1)

    @patch("app.veeqo_api.get_warehouses")
    def test_sync_data_api_error(self, mock_veeqo_warehouses):
        """Test sync data with API error"""
        mock_veeqo_warehouses.side_effect = Exception("API Error")

        response = self.client.get("/sync_data")

        data = self.assertJSONResponse(response, 500)
        self.assertEqual(data["status"], "error")
        self.assertIn("message", data)

    @patch("app.inventory_monitor.get_active_alerts")
    def test_api_inventory_alerts_success(self, mock_get_alerts):
        """Test inventory alerts API"""
        # Mock alert object
        mock_alert = Mock()
        mock_alert.id = 1
        mock_alert.product_sku = "SKU123"
        mock_alert.product_name = "Test Product"
        mock_alert.warehouse_name = "Test Warehouse"
        mock_alert.current_stock = 5
        mock_alert.threshold = 10
        mock_alert.alert_type = "low_stock"
        mock_alert.severity = "medium"
        mock_alert.created_at = "2024-01-01T00:00:00Z"

        mock_get_alerts.return_value = [mock_alert]

        response = self.client.get("/api/inventory_alerts")

        data = self.assertJSONResponse(response)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["product_sku"], "SKU123")
        self.assertEqual(data[0]["alert_type"], "low_stock")

    @patch("app.inventory_monitor.get_inventory_summary")
    def test_api_inventory_summary(self, mock_get_summary):
        """Test inventory summary API"""
        mock_summary = {
            "total_products": 100,
            "low_stock_items": 5,
            "out_of_stock_items": 2,
            "total_value": 10000.00,
        }
        mock_get_summary.return_value = mock_summary

        response = self.client.get("/api/inventory_summary")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["total_products"], 100)
        self.assertEqual(data["low_stock_items"], 5)

    @patch("app.inventory_monitor.resolve_alert")
    def test_api_resolve_alert_success(self, mock_resolve):
        """Test resolving inventory alert"""
        mock_resolve.return_value = True

        response = self.client.post("/api/resolve_alert/1")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Alert resolved")

    @patch("app.inventory_monitor.resolve_alert")
    def test_api_resolve_alert_not_found(self, mock_resolve):
        """Test resolving non-existent alert"""
        mock_resolve.return_value = False

        response = self.client.post("/api/resolve_alert/999")

        data = self.assertJSONResponse(response, 404)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Alert not found")

    @patch("app.product_sync.get_sync_stats")
    @patch("app.product_sync.get_product_performance")
    @patch("app.product_sync.get_inventory_alerts")
    def test_api_product_stats(self, mock_alerts, mock_performance, mock_stats):
        """Test product statistics API"""
        mock_stats.return_value = {"synced_products": 50}
        mock_performance.return_value = {"top_selling": "Product A"}
        mock_alerts.return_value = [{"alert": "low stock"}]

        response = self.client.get("/api/product_stats")

        data = self.assertJSONResponse(response)
        self.assertIn("stats", data)
        self.assertIn("performance", data)
        self.assertIn("alerts", data)
        self.assertEqual(data["alert_count"], 1)


class ExternalAPITest(APITestCase):
    """Test external API integrations (Veeqo and Easyship)"""

    def setUp(self):
        super().setUp()
        self.veeqo_api = VeeqoAPI()
        self.easyship_api = EasyshipAPI()

    @patch("requests.get")
    def test_veeqo_get_warehouses_success(self, mock_get):
        """Test successful Veeqo warehouse retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_warehouse]
        mock_get.return_value = mock_response

        result = self.veeqo_api.get_warehouses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Nevada Warehouse")
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_veeqo_get_warehouses_error(self, mock_get):
        """Test Veeqo warehouse retrieval with API error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = self.veeqo_api.get_warehouses()

        self.assertEqual(result, [])

    @patch("requests.get")
    def test_veeqo_get_products_success(self, mock_get):
        """Test successful Veeqo product retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_products
        mock_get.return_value = mock_response

        result = self.veeqo_api.get_products()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Fashion Dress")

    @patch("requests.post")
    def test_veeqo_create_order_success(self, mock_post):
        """Test successful Veeqo order creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "status": "created"}
        mock_post.return_value = mock_response

        result = self.veeqo_api.create_order(
            self.sample_customer_data, self.sample_products, 1, "UPS"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["status"], "created")

    @patch("requests.get")
    def test_easyship_get_addresses_success(self, mock_get):
        """Test successful Easyship address retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"addresses": [{"id": 1, "state": "Nevada"}]}
        mock_get.return_value = mock_response

        result = self.easyship_api.get_addresses()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["state"], "Nevada")

    @patch("requests.post")
    def test_easyship_create_shipment_success(self, mock_post):
        """Test successful Easyship shipment creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "ship123",
            "status": "created",
        }
        mock_post.return_value = mock_response

        result = self.easyship_api.create_shipment(
            self.sample_customer_data, self.sample_products, "addr123"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "ship123")

    def test_veeqo_generate_dummy_products(self):
        """Test dummy product generation for Veeqo"""
        products = self.veeqo_api._generate_dummy_products(3)

        self.assertEqual(len(products), 3)
        for product in products:
            self.assertIn("id", product)
            self.assertIn("title", product)
            self.assertIn("price", product)
            self.assertIn("weight", product)

    def test_easyship_generate_dummy_products(self):
        """Test dummy product generation for Easyship"""
        products = self.easyship_api._generate_dummy_products(2)

        self.assertEqual(len(products), 2)
        for product in products:
            self.assertIn("title", product)
            self.assertIn("price", product)
            self.assertIn("weight", product)

    def test_easyship_country_alpha2_conversion(self):
        """Test country code conversion"""
        self.assertEqual(self.easyship_api._get_country_alpha2("US"), "US")
        self.assertEqual(self.easyship_api._get_country_alpha2("GB"), "GB")
        self.assertEqual(self.easyship_api._get_country_alpha2("UK"), "GB")
        self.assertEqual(self.easyship_api._get_country_alpha2("UNKNOWN"), "US")


class BusinessLogicTest(APITestCase):
    """Test business logic, validation, and utility functions"""

    def test_validate_customer_data_valid(self):
        """Test validation with valid customer data"""
        result = validate_customer_data(self.sample_customer_data)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_customer_data_missing_required(self):
        """Test validation with missing required fields"""
        invalid_data = {"phone": "+1234567890"}
        result = validate_customer_data(invalid_data)

        self.assertFalse(result.is_valid)
        self.assertIn("Customer name is required", result.errors)
        self.assertIn("Address is required", result.errors)
        self.assertIn("City is required", result.errors)

    def test_validate_customer_data_invalid_email(self):
        """Test validation with invalid email"""
        invalid_data = self.sample_customer_data.copy()
        invalid_data["email"] = "invalid-email"
        result = validate_customer_data(invalid_data)

        self.assertFalse(result.is_valid)
        self.assertIn("Email format is invalid", result.errors)

    def test_parse_customer_input_tab_format(self):
        """Test parsing tab-separated customer input"""
        input_text = "John Doe\t+1234567890 john@example.com\t123 Main St\t\tLas Vegas\tNevada\t89101\tUS"
        result = parse_customer_input(input_text)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["phone"], "+1234567890")
        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(result["city"], "Las Vegas")
        self.assertEqual(result["detected_format"], "Tab-separated format")

    def test_parse_customer_input_space_format(self):
        """Test parsing space-separated customer input"""
        input_text = "John Doe 123 Main Street LasVegas Nevada 89101"
        result = parse_customer_input(input_text)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["detected_format"], "Space-separated format")

    def test_parse_customer_input_empty(self):
        """Test parsing empty input"""
        result = parse_customer_input("")
        self.assertIsNone(result)

        result = parse_customer_input("   ")
        self.assertIsNone(result)

    def test_normalize_customer_data(self):
        """Test customer data normalization"""
        raw_data = {
            "name": "  John Doe  ",
            "phone": "(123) 456-7890",
            "postal_code": "89101",
            "country": "us",
        }

        normalized = normalize_customer_data(raw_data)

        self.assertEqual(normalized["name"], "John Doe")
        self.assertEqual(normalized["phone"], "+11234567890")
        self.assertEqual(normalized["country"], "US")

    def test_routing_system_route_order(self):
        """Test order routing logic"""
        routing_system = OrderRoutingSystem()
        warehouses = [self.sample_warehouse]

        decision = routing_system.route_order(self.sample_customer_data, warehouses)

        self.assertIsInstance(decision, RoutingDecision)
        self.assertIn(decision.platform, ["VEEQO", "EASYSHIP"])
        self.assertIn(decision.carrier, ["FEDEX", "UPS", "DHL", "USPS"])
        self.assertGreater(decision.confidence, 0)

    def test_routing_system_get_carrier_options(self):
        """Test getting available carrier options"""
        routing_system = OrderRoutingSystem()
        carriers = routing_system.get_carrier_options()

        self.assertIsInstance(carriers, list)
        self.assertIn("FEDEX", carriers)
        self.assertIn("UPS", carriers)

    def test_routing_system_get_platform_for_carrier(self):
        """Test getting platform for specific carrier"""
        routing_system = OrderRoutingSystem()

        self.assertEqual(routing_system.get_platform_for_carrier("FEDEX"), "EASYSHIP")
        self.assertEqual(routing_system.get_platform_for_carrier("UPS"), "VEEQO")
        self.assertEqual(routing_system.get_platform_for_carrier("UNKNOWN"), "VEEQO")


class OrderProcessingTest(APITestCase):
    """Test order processing endpoints"""

    @patch("app.fedex_processor.process_all_fedex_orders")
    def test_process_fedex_orders_success(self, mock_process):
        """Test successful FedEx order processing"""
        mock_process.return_value = [
            {"customer": "John Doe", "success": True, "order_id": "123"},
            {"customer": "Jane Smith", "success": True, "order_id": "124"},
        ]

        response = self.client.post("/process_fedex_orders")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["processed"], 2)
        self.assertEqual(data["successful"], 2)

    @patch("app.fedex_processor.process_all_fedex_orders")
    def test_process_fedex_orders_partial_success(self, mock_process):
        """Test FedEx order processing with some failures"""
        mock_process.return_value = [
            {"customer": "John Doe", "success": True, "order_id": "123"},
            {"customer": "Jane Smith", "success": False, "error": "API Error"},
        ]

        response = self.client.post("/process_fedex_orders")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["processed"], 2)
        self.assertEqual(data["successful"], 1)

    @patch("app.fedex_processor.create_fedex_shipment")
    def test_create_fedex_order_success(self, mock_create):
        """Test individual FedEx order creation"""
        mock_create.return_value = {"id": "ship123", "status": "created"}

        response = self.client.post("/create_fedex_order/john_doe")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertIn("result", data)

    @patch("app.fedex_processor.create_fedex_shipment")
    def test_create_fedex_order_failure(self, mock_create):
        """Test failed FedEx order creation"""
        mock_create.return_value = None

        response = self.client.post("/create_fedex_order/john_doe")

        data = self.assertJSONResponse(response, 500)
        self.assertEqual(data["status"], "error")

    @patch("app.veeqo_processor.process_all_veeqo_orders")
    def test_process_veeqo_orders_success(self, mock_process):
        """Test successful Veeqo order processing"""
        mock_process.return_value = [
            {"customer": "John Doe", "success": True, "order_id": "123"}
        ]

        response = self.client.post("/process_veeqo_orders")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["processed"], 1)
        self.assertEqual(data["successful"], 1)

    @patch("app.veeqo_processor.get_customer_by_name")
    @patch("app.veeqo_processor.create_veeqo_order")
    def test_create_veeqo_order_success(self, mock_create, mock_get_customer):
        """Test individual Veeqo order creation"""
        mock_get_customer.return_value = {"carrier": "UPS"}
        mock_create.return_value = {"id": "order123", "status": "created"}

        response = self.client.post("/create_veeqo_order/john_doe")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertIn("result", data)

    @patch("app.veeqo_processor.get_purchase_orders")
    def test_api_veeqo_purchase_orders(self, mock_get_pos):
        """Test Veeqo purchase orders API"""
        mock_get_pos.return_value = [
            {"id": 1, "supplier": "Supplier A"},
            {"id": 2, "supplier": "Supplier B"},
        ]

        response = self.client.get("/api/veeqo_purchase_orders")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 2)
        self.assertIn("purchase_orders", data)


class ErrorHandlingTest(APITestCase):
    """Test error handling and edge cases"""

    def test_api_endpoints_with_exceptions(self):
        """Test API endpoints when exceptions occur"""
        with patch(
            "app.inventory_monitor.get_active_alerts",
            side_effect=Exception("Database error"),
        ):
            response = self.client.get("/api/inventory_alerts")
            data = self.assertJSONResponse(response, 500)
            self.assertEqual(data["status"], "error")
            self.assertIn("message", data)

    def test_invalid_json_requests(self):
        """Test endpoints with invalid JSON"""
        response = self.client.post(
            "/api/parse_customer",
            data="invalid json",
            content_type="application/json",
        )

        data = self.assertJSONResponse(response, 400)
        self.assertEqual(data["status"], "error")

    def test_missing_parameters(self):
        """Test endpoints with missing required parameters"""
        response = self.client.post(
            "/api/parse_customer",
            json={},  # Missing 'input' parameter
            content_type="application/json",
        )

        data = self.assertJSONResponse(response, 400)
        self.assertEqual(data["status"], "error")

    def test_nonexistent_customer_order(self):
        """Test creating order for non-existent customer"""
        response = self.client.post("/create_fedex_order/nonexistent_customer")

        # Should return error response
        self.assertIn(response.status_code, [404, 500])

    @patch("app.product_sync.start_auto_sync")
    def test_auto_sync_start_with_custom_interval(self, mock_start):
        """Test starting auto sync with custom interval"""
        response = self.client.post(
            "/api/start_auto_sync",
            json={"interval": 10},
            content_type="application/json",
        )

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        mock_start.assert_called_once_with(10)

    @patch("app.product_sync.start_auto_sync")
    def test_auto_sync_start_default_interval(self, mock_start):
        """Test starting auto sync with default interval"""
        response = self.client.post(
            "/api/start_auto_sync", json={}, content_type="application/json"
        )

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        mock_start.assert_called_once_with(5)  # Default interval

    @patch("app.product_sync.stop_auto_sync")
    def test_auto_sync_stop(self, mock_stop):
        """Test stopping auto sync"""
        response = self.client.post("/api/stop_auto_sync")

        data = self.assertJSONResponse(response)
        self.assertEqual(data["status"], "success")
        mock_stop.assert_called_once()


class ResponseFormatTest(APITestCase):
    """Test API response format consistency"""

    def test_success_response_format(self):
        """Test that success responses follow consistent format"""
        with patch("app.inventory_monitor.get_inventory_summary", return_value={}):
            response = self.client.get("/api/inventory_summary")
            data = self.assertJSONResponse(response)
            # Should return the summary object directly
            self.assertIsInstance(data, dict)

    def test_error_response_format(self):
        """Test that error responses follow consistent format"""
        with patch(
            "app.inventory_monitor.get_inventory_summary",
            side_effect=Exception("Error"),
        ):
            response = self.client.get("/api/inventory_summary")
            data = self.assertJSONResponse(response, 500)
            self.assertEqual(data["status"], "error")
            self.assertIn("message", data)

    def test_list_response_format(self):
        """Test that list responses are properly formatted"""
        with patch("app.inventory_monitor.get_active_alerts", return_value=[]):
            response = self.client.get("/api/inventory_alerts")
            data = self.assertJSONResponse(response)
            self.assertIsInstance(data, list)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        FlaskAPIEndpointsTest,
        ExternalAPITest,
        BusinessLogicTest,
        OrderProcessingTest,
        ErrorHandlingTest,
        ResponseFormatTest,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'=' * 50}")
    print(f"API Testing Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print(f"{'=' * 50}")

    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code)
