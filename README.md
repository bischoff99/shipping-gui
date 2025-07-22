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
This system integrates the best logic from your existing scripts:
- Customer parsing from `test_jojet_gui_fixed.py` and `enhanced_routing_gui.py`
- API integration from `working_easyship_order.py` and `advanced_web_gui.py`
- Routing logic from `carrier_based_routing.py` and related scripts
- Validation patterns from your warehouse and order management scripts

### Extending the System
- Add new carriers in `routing.py`
- Extend validation rules in `validation.py`
- Add new API endpoints in the respective API modules
- Customize UI templates for branding or additional features

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
