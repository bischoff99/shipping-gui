<!-- Copilot Instructions for Unified Order & Warehouse Management System -->

# 🧑‍💻 AI Agent Onboarding: Project-Specific Guidelines

## 1. System Architecture & Major Components

- **Flask-based web app**: All business logic in `app.py`, with modular separation for API integration (`api/`), routing (`routing.py`), validation (`validation.py`), and utility functions (`utils.py`).
- **Blueprints**: Use Flask Blueprints (see `blueprints/`) for modular route organization (e.g., `intelligent_orders_bp`).
- **Service Layer**: Business logic for product sync, inventory, and order processing is in `services/` and `advanced_product_sync.py`.
- **Database**: SQLAlchemy models in `models.py` (Product, Warehouse, Supplier, etc.).
- **API Integrations**: Veeqo (`api/veeqo_api.py`) and Easyship (`api/easyship_api.py`) are the main external APIs.
- **Dashboards**: Jinja2 templates in `templates/` for all UI rendering.

## 2. Developer Workflows

- **Run app (dev)**: `python app.py` or `start_server.bat` (Windows) / `./start_server.sh` (Linux/Mac).
- **Production**: Use Gunicorn (`gunicorn -c gunicorn_config.py app:app`).
- **Sync data**: Use `/sync_data` route or dashboard button to refresh local product/warehouse cache.
- **Testing**:
  - **Python**: `python run_tests.py` (unit/integration), or `pytest tests/`.
  - **Postman**: Import `postman_collection.json` and `postman_environment.json` for manual/automated API tests. Use `run_postman_tests.py` or `newman_test_runner.sh` for automation.
  - **CI/CD**: See `TEST_README.md` and `POSTMAN_TESTING_GUIDE.md` for GitHub Actions and Newman integration.
- **Environment**: All secrets/API keys in `.env` (see `.env.example`). Never hardcode.

## 3. Project Conventions & Patterns

- **Input Parsing**: Use `utils.parse_customer_input` for all customer data (supports tab/space-separated formats).
- **Routing Logic**: Use `OrderRoutingSystem` (`routing.py`) for carrier/platform/warehouse selection. FedEx → Easyship, others → Veeqo.
- **Validation**: Use `validate_order_data` and `ValidationResult` for all input and business logic validation.
- **Product Sync**: Use `AdvancedProductSync` for bidirectional sync and real-time monitoring.
- **Inventory Monitoring**: Use `RealTimeInventoryMonitor` for alerts, thresholds, and reorder suggestions.
- **API Keys**: Always load from environment variables. Never commit real keys.
- **Testing**: Mock external APIs in unit tests; use real keys only for integration tests (see `test_config.py`).
- **Naming**: Test files/classes/methods follow `test_[feature]_[type]` pattern.

## 4. Integration Points & External Dependencies

- **Veeqo API**: Warehouse, product, and order management.
- **Easyship API**: Address, product, and shipment management.
- **Postman/Newman**: For API test automation and CI/CD.
- **Flask Extensions**: SQLAlchemy, CORS, Limiter, Marshmallow, etc. (see `requirements.txt`).

## 5. Examples & Key Files

- **Order creation**: See `/create_order` route in `app.py` and `templates/create_order.html`.
- **Product sync**: See `/api/sync_products` and `advanced_product_sync.py`.
- **Inventory alerts**: See `/api/inventory_alerts` and `services/inventory_monitor.py`.
- **Testing**: See `TEST_README.md`, `POSTMAN_TESTING_GUIDE.md`, and `run_postman_tests.py`.

## 6. Security & Best Practices

- **Never hardcode secrets**; always use `.env`.
- **Validate all user input** before processing.
- **Handle errors with clear feedback** (UI/API).
- **Use atomic file writes** for data sync (see `sync_data` route).
- **Document new endpoints/tests** in the appropriate markdown files.

---

> For more details, see `README.md`, `README_ADVANCED.md`, `TEST_README.md`, and `POSTMAN_TESTING_GUIDE.md`. When in doubt, prefer modularity, explicit validation, and clear error handling.
