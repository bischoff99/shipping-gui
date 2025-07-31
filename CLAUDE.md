# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Unified Order & Warehouse Management System - A Flask web application that integrates Veeqo and Easyship APIs for intelligent shipping automation, order routing, and warehouse management.

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # or: .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment variables required in .env:
# VEEQO_API_KEY=your_veeqo_key
# EASYSHIP_API_KEY=your_easyship_key
# FLASK_SECRET_KEY=your_secret_key
```

### Running the Application
```bash
# Development server
python app.py

# Production server
gunicorn app:app

# Access at: http://127.0.0.1:5000/

# MCP-Enhanced Setup (recommended)
bash scripts/setup_project.sh
```

### Testing
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_app.py
pytest tests/test_api_integration.py

# Run tests with coverage
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Format code (Black configured for line-length=88)
black .

# Type checking (if using mypy)
mypy app.py routing.py validation.py
```

## Architecture Overview

### Core Routing Logic (`routing.py`)
- **Carrier-Platform Mapping**: FedEx → Easyship, UPS/DHL/USPS → Veeqo
- **Geographic Warehouse Selection**: Prioritizes Nevada/California warehouses
- **Intelligent Decision Making**: Uses confidence scoring for routing decisions

### API Integration Pattern
- **Dual Platform Support**: Seamless switching between Veeqo and Easyship APIs
- **Error Handling**: Comprehensive try-catch blocks with user-friendly error messages
- **Data Caching**: JSON files for warehouses/products with atomic writes using tempfile

### Order Processing Workflow
1. **Input Parsing** (`utils.py`): Handles tab-separated and space-separated customer data
2. **Validation** (`validation.py`): Customer data and order validation with detailed error reporting
3. **Routing Decision** (`routing.py`): Platform and warehouse selection based on carrier/location
4. **Order Creation**: Platform-specific API calls (Veeqo or Easyship)

### Database Architecture (`models.py`)
- SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- Optimized connection pooling and performance settings
- Sample data generation for development environment

## Key Integration Points

### Flask App Structure
- **Blueprints**: `intelligent_orders_bp` for modular route organization
- **Template Rendering**: Consistent error/success message handling with flash()
- **API Endpoints**: RESTful endpoints for AJAX interactions (`/api/parse_customer`, `/api/get_products`)

### MCP Server Configuration
The project uses several MCP servers for enhanced development:
- **filesystem**: File operations in `/root/projects`
- **github**: Git operations and repository management  
- **hf-spaces**: Hugging Face integration for AI features
- **sequential-thinking**: Step-by-step planning assistance
- **mcp-pdb**: Python debugging support

#### MCP Integration Features
- **AI-Enhanced Parsing**: Intelligent customer data parsing (`/api/ai/parse-customer`)
- **Smart Route Optimization**: AI-powered shipping route selection (`/api/ai/optimize-route`)
- **Intelligent Error Detection**: AI-powered error analysis (`/api/ai/error-analysis`)
- **Development Insights**: AI-generated development suggestions (`/api/ai/insights`)
- **Real-time Debugging**: Interactive Python debugging with mcp-pdb
- **MCP Dashboard**: Real-time MCP server status at `/mcp-dashboard`

#### MCP Development Tools
```bash
# Check MCP server status
claude mcp list

# Start interactive debug session
python tools/mcp_debug_helper.py --file app.py

# Debug specific API
python tools/mcp_debug_helper.py --api veeqo --method get_products

# Debug order workflow
python tools/mcp_debug_helper.py --workflow routing
```

### Error Handling Strategy
- **Graceful Degradation**: Default values and empty states when APIs fail
- **User Feedback**: Flash messages for success/error states
- **Logging**: Structured logging with `config/logging_config.py`

## Development Patterns

### Customer Data Processing
Expected input formats:
- Tab-separated: `John Doe\t+1234567890\tjohn@email.com\t123 Main St\tBoston\tMA\t02101\tUS`
- Space-separated: `John Doe +1234567890 john@email.com 123 Main St Boston MA 02101 US`

### API Client Pattern
Both `api/veeqo_api.py` and `api/easyship_api.py` implement:
- Connection testing methods
- Random product selection
- Warehouse/address management
- Order/shipment creation with consistent interfaces

### Testing Strategy
- **Integration Tests**: Full workflow testing with mock APIs
- **Unit Tests**: Individual component testing
- **API Tests**: Connection and response validation
- **Configuration Tests**: Environment variable validation

## Deployment Configuration
- **Docker**: Multi-stage builds with production optimizations
- **Gunicorn**: WSGI server configuration in `gunicorn_config.py`
- **Environment Configs**: Development/Production/Testing configurations in `config.py`

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.