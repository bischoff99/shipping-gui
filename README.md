# Unified Order & Warehouse Management System

A Flask-based web application that unifies the best features from your existing GUI scripts into a modern, comprehensive system.

## Features

### 🚀 Core Functionality
- **Order Creation with Paste-In Customer Details**: Supports tab-separated and space-separated formats
- **Intelligent Routing Logic**: 
  - FedEx orders → Easyship platform
  - UPS/DHL/USPS orders → Veeqo platform
- **Smart Warehouse Matching**: Prioritizes Nevada and California warehouses
- **Random Product Selection**: Automatically adds 3 random products to each order
- **Real-time API Sync**: Syncs products and warehouses between veeqo.com and easyship.com
- **Comprehensive Validation**: Input validation, error handling, and user feedback
- **Actual Order Creation**: Creates real orders via both Veeqo and Easyship APIs

### 📊 Dashboard & Monitoring
- Real-time system status
- Warehouse and product sync statistics
- Order routing visualization
- System health monitoring

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   - Copy `.env.template` to `.env`
   - Add your actual API keys for Veeqo and Easyship

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the System**:
   - Open your browser to `http://127.0.0.1:5000/`

## Usage

### Creating Orders
1. Navigate to "Create Order"
2. Paste customer details in one of these formats:

**Tab-separated format**:
```
John Doe    +1234567890 john@email.com    123 Main St    Boston    MA    02101    US
```

**Space-separated format**:
```
John Doe +1234567890 john@email.com 123 Main St Boston MA 02101 US
```

3. Optionally select a preferred carrier
4. Click "Create Order" - the system will:
   - Parse and validate customer data
   - Apply routing logic based on carrier/location
   - Select the best warehouse (Nevada/California preference)
   - Add 3 random products
   - Create the order via appropriate API
   - Display confirmation and tracking info

### Syncing Data
- Use the "Sync Data" feature to refresh products and warehouses from both platforms
- Data is cached locally for faster order processing

## Project Structure

The project is now organized into a clean, modular directory structure:

```
SHIPPING_GUI/
├── 📁 api/                      # API integrations
│   ├── easyship_api.py          # Easyship platform integration
│   └── veeqo_api.py             # Veeqo platform integration
├── 📁 blueprints/               # Flask route blueprints
│   ├── dashboard.py             # Dashboard routes
│   ├── orders.py                # Order management routes
│   └── inventory.py             # Inventory management routes
├── 📁 config/                   # Configuration files
│   ├── celeryconfig.py          # Celery task configuration
│   └── logging_config.py        # Logging setup
├── 📁 data/                     # Data files and exports
│   ├── products.json            # Product catalog cache
│   ├── warehouses.json          # Warehouse data cache
│   └── postman_*.json           # API testing collections
├── 📁 deployment/               # Deployment configurations
│   ├── Dockerfile               # Container configuration
│   ├── docker-compose.yml       # Multi-service setup
│   └── deploy_production.sh     # Production deployment script
├── 📁 docs/                     # Project documentation
│   ├── IMPLEMENTATION_ROADMAP.md
│   ├── GUI_INTEGRATION_README.md
│   └── UNIFIED_SYSTEM_DOCUMENTATION.md
├── 📁 GUI/                      # Desktop GUI components
│   ├── unified_warehouse_system.py
│   └── integration_launcher.py
├── 📁 logs/                     # Application logs
├── 📁 middleware/               # Flask middleware
│   ├── auth.py                  # Authentication
│   ├── error_handling.py        # Error handling
│   └── rate_limit.py            # Rate limiting
├── 📁 services/                 # Business logic services
│   ├── inventory_monitor.py     # Real-time inventory tracking
│   ├── order_processor.py       # Order processing logic
│   └── csv_processor.py         # CSV data processing
├── 📁 templates/                # Jinja2 HTML templates
│   ├── unified_dashboard.html   # Main dashboard
│   ├── create_order.html        # Order creation form
│   └── inventory/               # Inventory-specific templates
├── 📁 tests/                    # Test suite
│   ├── test_api_integration.py  # API integration tests
│   ├── test_app.py              # Application tests
│   └── csv/                     # CSV processing tests
├── 📁 tools/                    # Utility scripts
│   ├── gui_launcher.py          # Desktop launcher
│   ├── validate_setup.py        # Environment validation
│   └── init_db.py               # Database initialization
└── 📁 utils/                    # Utility modules
    ├── input_validation.py      # Input validation helpers
    ├── logging_utils.py         # Logging utilities
    └── api_timeout.py           # API timeout handling
```

## Architecture

### Backend Modules
- **`api/veeqo_api.py`**: Veeqo API integration (warehouses, products, orders)
- **`api/easyship_api.py`**: Easyship API integration (addresses, products, shipments)
- **`routing.py`**: Intelligent order routing logic
- **`validation.py`**: Comprehensive input and data validation
- **`utils.py`**: Customer parsing and utility functions

### Frontend
- **Modern Web Interface**: Responsive design with gradient backgrounds
- **Multi-page Structure**: Dashboard, order creation, success pages
- **Real-time Feedback**: Flash messages, form validation, progress indicators

## Routing Logic

| Carrier | Platform | Use Case |
|---------|----------|----------|
| FedEx | Easyship | International shipping, premium service |
| UPS | Veeqo | Domestic shipping, inventory integration |
| DHL | Veeqo | International express, inventory integration |
| USPS | Veeqo | Cost-effective domestic, inventory integration |

## Warehouse Selection Priority

1. **Same State Match**: Customer state matches warehouse state
2. **Nevada Warehouses**: First preference for US orders
3. **California Warehouses**: Second preference for US orders
4. **Random Selection**: If no geographic match found

## API Integration

### Veeqo Integration
- Warehouse management and sync
- Product/sellable management
- Order creation with line items
- Inventory tracking

### Easyship Integration  
- Address/warehouse sync
- Product catalog sync
- Shipment creation
- Rate shopping and booking
- FedEx integration

## Development

### Reused Components
This system integrates the best logic from legacy scripts (now in `backup_original_structure/`):
- Customer parsing logic from enhanced routing components
- API integration from proven working implementations
- Routing logic from carrier-based routing systems
- Validation patterns from warehouse and order management scripts

### Extending the System
- **Add new carriers**: Update `routing.py` and add configuration
- **Extend validation**: Modify `validation.py` and `utils/input_validation.py`
- **Add API endpoints**: Create new modules in `api/` directory
- **Add new services**: Create business logic in `services/` directory
- **Customize UI**: Modify templates in `templates/` directory
- **Add middleware**: Create new middleware in `middleware/` directory

### Development Tools
- **Database initialization**: `tools/init_db.py`
- **Environment validation**: `tools/validate_setup.py`
- **GUI launcher**: `tools/gui_launcher.py`
- **Production runner**: `tools/run_production.py`

## Troubleshooting

### Common Issues
- **API Connection Errors**: Check your API keys in `.env` file
- **Parsing Failures**: Ensure customer data follows supported formats
- **Order Creation Failures**: Verify warehouse and product availability
- **Sync Issues**: Check internet connection and API rate limits

### Logs and Debugging
- Enable Flask debug mode in `.env` (`DEBUG=True`)
- Check browser console for JavaScript errors
- Monitor Flask console output for API responses

## Security Notes

- API keys are loaded from environment variables
- Never commit actual API keys to version control
- Use HTTPS in production deployments
- Consider rate limiting for production use
