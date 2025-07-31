#!/bin/bash

# Enhanced SHIPPING_GUI Project Setup Script with MCP Integration
# This script sets up the complete development environment with MCP server validation
# Compatible with Linux/WSL2 environments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_NAME="venv"
PYTHON_VERSION="python3"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check system prerequisites
check_prerequisites() {
    log_step "Checking system prerequisites..."
    
    # Check Python
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    local python_version=$($PYTHON_VERSION --version 2>&1 | awk '{print $2}')
    log_info "Found Python version: $python_version"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    # Check Node.js and npm for MCP servers
    if ! command -v node &> /dev/null; then
        log_warn "Node.js not found. Some MCP servers may not work."
    else
        local node_version=$(node --version)
        log_info "Found Node.js version: $node_version"
    fi
    
    if ! command -v npm &> /dev/null; then
        log_warn "npm not found. Some MCP servers may not work."
    else
        local npm_version=$(npm --version)
        log_info "Found npm version: $npm_version"
    fi
    
    # Check if Claude Code is available
    if command -v claude &> /dev/null; then
        log_info "Claude Code is available"
    else
        log_warn "Claude Code not found in PATH. MCP integration may be limited."
    fi
    
    log_info "Prerequisites check completed"
}

# Create and activate virtual environment
setup_virtual_environment() {
    log_step "Setting up Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "$VENV_NAME" ]]; then
        log_info "Creating virtual environment..."
        $PYTHON_VERSION -m venv "$VENV_NAME"
        log_info "Virtual environment created at $PROJECT_ROOT/$VENV_NAME"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    log_info "Virtual environment activated"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install uv for faster package management (used by MCP servers)
    log_info "Installing uv for MCP server support..."
    pip install uv
}

# Install Python dependencies
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing from requirements.txt..."
        pip install -r requirements.txt
        log_info "Requirements installed successfully"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install additional MCP-related dependencies
    log_info "Installing MCP-related dependencies..."
    pip install mcp-pdb requests structlog
}

# Setup environment configuration
setup_environment() {
    log_step "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env file from template if it doesn't exist
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp ".env.example" ".env"
            log_info ".env file created from .env.example template"
        else
            log_warn ".env.example not found, creating basic .env file"
            create_basic_env_file
        fi
    else
        log_info ".env file already exists"
    fi
    
    # Update .env file with MCP-specific settings
    update_env_for_mcp
    
    log_info "Environment configuration completed"
}

# Create basic .env file
create_basic_env_file() {
    cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true

# Database Configuration
DATABASE_URL=sqlite:///instance/shipping_automation.db

# External API Keys (replace with actual values)
VEEQO_API_KEY=your-veeqo-api-key
EASYSHIP_API_KEY=your-easyship-api-key

# Hugging Face Token for MCP integration
HF_TOKEN=your-huggingface-token

# MCP Configuration
MCP_URL=http://localhost:3000
MCP_DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_TO_STDOUT=true
EOF
    log_info "Basic .env file created"
}

# Update .env file for MCP integration
update_env_for_mcp() {
    local env_file=".env"
    
    # Add MCP-specific environment variables if they don't exist
    if ! grep -q "MCP_URL" "$env_file"; then
        echo "" >> "$env_file"
        echo "# MCP Server Configuration" >> "$env_file"
        echo "MCP_URL=http://localhost:3000" >> "$env_file"
        echo "MCP_DEBUG=true" >> "$env_file"
        echo "MCP_TIMEOUT=30" >> "$env_file"
        log_info "Added MCP configuration to .env file"
    fi
}

# Validate MCP servers
validate_mcp_servers() {
    log_step "Validating MCP server connections..."
    
    if ! command -v claude &> /dev/null; then
        log_warn "Claude Code not available. Skipping MCP validation."
        return 0
    fi
    
    log_info "Checking MCP server health..."
    if claude mcp list > /dev/null 2>&1; then
        log_info "MCP servers are accessible"
        
        # Show MCP server status
        log_info "MCP Server Status:"
        claude mcp list || log_warn "Could not retrieve MCP server details"
    else
        log_warn "MCP servers may not be properly configured"
        log_info "Run 'claude mcp list' to check MCP server status"
    fi
}

# Create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    
    cd "$PROJECT_ROOT"
    
    # Create directories that might be missing
    mkdir -p instance
    mkdir -p logs
    mkdir -p data/exports
    mkdir -p temp
    
    log_info "Directory structure created"
}

# Initialize database
initialize_database() {
    log_step "Initializing database..."
    
    cd "$PROJECT_ROOT"
    
    # Check if database initialization script exists
    if [[ -f "tools/init_db.py" ]]; then
        log_info "Running database initialization..."
        python tools/init_db.py
        log_info "Database initialized"
    else
        log_info "No database initialization script found, skipping..."
    fi
}

# Validate installation
validate_installation() {
    log_step "Validating installation..."
    
    cd "$PROJECT_ROOT"
    
    # Test basic imports
    log_info "Testing Python imports..."
    python -c "
import flask
import requests
import sqlalchemy
print('✓ Core dependencies imported successfully')
" || {
        log_error "Failed to import core dependencies"
        exit 1
    }
    
    # Test Flask app startup (without running server)
    log_info "Testing Flask app initialization..."
    python -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✓ Flask app initialized successfully')
except Exception as e:
    print(f'✗ Flask app initialization failed: {e}')
    sys.exit(1)
" || {
        log_warn "Flask app initialization test failed. Check your configuration."
    }
    
    log_info "Installation validation completed"
}

# Display completion message
show_completion_message() {
    log_step "Setup completed successfully!"
    
    echo ""
    echo -e "${GREEN}🎉 SHIPPING_GUI MCP-Enhanced Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Configure your API keys in .env file:"
    echo "   - VEEQO_API_KEY"
    echo "   - EASYSHIP_API_KEY"
    echo "   - HF_TOKEN (for AI features)"
    echo ""
    echo "3. Start the development server:"
    echo "   python app.py"
    echo ""
    echo "4. Access the application:"
    echo "   http://127.0.0.1:5000/"
    echo ""
    echo "5. Check MCP server status:"
    echo "   claude mcp list"
    echo ""
    echo -e "${BLUE}MCP Integration Features:${NC}"
    echo "- Real-time Python debugging with mcp-pdb"
    echo "- AI-enhanced development with Hugging Face"
    echo "- Automated Git workflows"
    echo "- Intelligent file operations"
    echo "- Step-by-step development planning"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🚀 SHIPPING_GUI MCP-Enhanced Setup${NC}"
    echo "======================================"
    echo ""
    
    check_prerequisites
    setup_virtual_environment
    install_dependencies
    setup_environment
    create_directories
    initialize_database
    validate_mcp_servers
    validate_installation
    show_completion_message
}

# Handle script arguments
case "${1:-setup}" in
    "setup"|"")
        main
        ;;
    "check")
        check_prerequisites
        validate_mcp_servers
        ;;
    "env")
        setup_environment
        ;;
    "deps")
        setup_virtual_environment
        install_dependencies
        ;;
    "validate")
        validate_installation
        validate_mcp_servers
        ;;
    *)
        echo "Usage: $0 {setup|check|env|deps|validate}"
        echo ""
        echo "Commands:"
        echo "  setup    - Complete project setup (default)"
        echo "  check    - Check prerequisites and MCP servers"
        echo "  env      - Setup environment configuration only"
        echo "  deps     - Install dependencies only"
        echo "  validate - Validate installation and MCP servers"
        exit 1
        ;;
esac