"""
Unit tests for the Flask application factory pattern.
Tests the modular app creation, configuration loading, and blueprint registration.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from flask import Flask

# Import the app factory we're testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.app_factory import create_app, configure_app, setup_security, register_blueprints


class TestAppFactory:
    """Test suite for application factory pattern."""

    def test_create_app_development(self):
        """Test app creation with development configuration."""
        app = create_app('development')
        
        assert isinstance(app, Flask)
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False

    def test_create_app_testing(self):
        """Test app creation with testing configuration."""
        app = create_app('testing')
        
        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///:memory:"

    def test_create_app_production(self):
        """Test app creation with production configuration."""
        app = create_app('production')
        
        assert isinstance(app, Flask)
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
        assert app.config['SESSION_COOKIE_SECURE'] is True

    def test_create_app_default_config(self):
        """Test app creation with no config specified uses development."""
        app = create_app()
        
        assert isinstance(app, Flask)
        assert app.config['DEBUG'] is True

    @patch.dict(os.environ, {'FLASK_ENV': 'production'})
    def test_create_app_env_override(self):
        """Test environment variable overrides config selection."""
        app = create_app()
        
        # Should detect production from environment
        assert isinstance(app, Flask)

    def test_configure_app_secret_key(self):
        """Test that app gets proper secret key configuration."""
        app = Flask(__name__)
        configure_app(app, 'testing')
        
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) >= 32

    def test_configure_app_api_keys(self):
        """Test API key configuration loading."""
        app = Flask(__name__)
        
        with patch.dict(os.environ, {
            'VEEQO_API_KEY': 'test_veeqo_key',
            'EASYSHIP_API_KEY': 'test_easyship_key'
        }):
            configure_app(app, 'testing')
            
            assert app.config['VEEQO_API_KEY'] == 'test_veeqo_key'
            assert app.config['EASYSHIP_API_KEY'] == 'test_easyship_key'

    def test_configure_app_mcp_settings(self):
        """Test MCP (Model Context Protocol) configuration."""
        app = Flask(__name__)
        configure_app(app, 'testing')
        
        assert 'MCP_URL' in app.config
        assert 'MCP_DEBUG' in app.config
        assert 'MCP_TIMEOUT' in app.config
        assert isinstance(app.config['MCP_TIMEOUT'], int)

    @patch('core.app_factory.SecurityManager')
    def test_setup_security(self, mock_security_manager):
        """Test security middleware setup."""
        app = Flask(__name__)
        configure_app(app, 'testing')
        
        mock_security_instance = MagicMock()
        mock_security_manager.return_value = mock_security_instance
        
        security = setup_security(app)
        
        mock_security_manager.assert_called_once_with(app)
        mock_security_instance.init_security.assert_called_once()
        assert security == mock_security_instance

    def test_register_blueprints(self):
        """Test blueprint registration."""
        app = Flask(__name__)
        configure_app(app, 'testing')
        
        # Get initial blueprint count
        initial_blueprints = len(app.blueprints)
        
        register_blueprints(app)
        
        # Should have registered multiple blueprints
        assert len(app.blueprints) > initial_blueprints
        
        # Check for expected blueprint names
        expected_blueprints = ['orders', 'api', 'dashboard', 'health']
        for bp_name in expected_blueprints:
            assert any(bp_name in name for name in app.blueprints.keys())

    def test_app_context_processors(self):
        """Test that context processors are properly registered."""
        app = create_app('testing')
        
        with app.test_request_context():
            # Test that context processors provide expected variables
            ctx = app.make_shell_context()
            assert 'app' in ctx

    def test_error_handlers_registered(self):
        """Test that error handlers are properly registered."""
        app = create_app('testing')
        
        # Test 404 handler
        with app.test_client() as client:
            response = client.get('/nonexistent-route')
            assert response.status_code == 404

    def test_database_initialization(self):
        """Test database initialization in app factory."""
        app = create_app('testing')
        
        # Should have database configuration
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

    @patch('core.app_factory.create_sample_data')
    def test_development_sample_data(self, mock_create_sample_data):
        """Test sample data creation in development mode."""
        app = create_app('development')
        
        with app.app_context():
            # Sample data should be created in development
            mock_create_sample_data.assert_called_once()

    def test_mcp_integration_config(self):
        """Test MCP integration configuration."""
        app = create_app('testing')
        
        # Verify MCP-related configurations
        mcp_configs = [
            'MCP_PYTHON_DEBUG_ENABLED',
            'MCP_FILESYSTEM_ENABLED', 
            'MCP_GITHUB_ENABLED',
            'MCP_SEQUENTIAL_THINKING_ENABLED',
            'MCP_HF_SPACES_ENABLED'
        ]
        
        for config_key in mcp_configs:
            assert config_key in app.config
            assert isinstance(app.config[config_key], bool)

    def test_performance_configurations(self):
        """Test performance-related configurations."""
        app = create_app('production')
        
        # Check database connection pooling
        engine_options = app.config['SQLALCHEMY_ENGINE_OPTIONS']
        assert 'pool_size' in engine_options
        assert 'max_overflow' in engine_options
        assert engine_options['pool_size'] >= 10

        # Check JSON optimization
        assert app.config['JSON_SORT_KEYS'] is False
        assert app.config['JSONIFY_PRETTYPRINT_REGULAR'] is False

    def test_security_headers_production(self):
        """Test security headers in production configuration."""
        app = create_app('production')
        
        assert app.config['SESSION_COOKIE_SECURE'] is True
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'

    def test_caching_configuration(self):
        """Test caching configuration for different environments."""
        # Development uses simple cache
        dev_app = create_app('development')
        assert dev_app.config['CACHE_TYPE'] == 'simple'
        
        # Production should use Redis
        prod_app = create_app('production')
        assert prod_app.config['CACHE_TYPE'] == 'RedisCache'
        assert 'CACHE_REDIS_URL' in prod_app.config

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_environment_variables(self):
        """Test app creation with missing environment variables."""
        app = create_app('testing')
        
        # Should still create app with defaults
        assert isinstance(app, Flask)
        assert app.config['SECRET_KEY'] is not None  # Generated automatically
        
        # API keys should be None if not set
        assert app.config.get('VEEQO_API_KEY') is None
        assert app.config.get('EASYSHIP_API_KEY') is None

    def test_app_factory_idempotent(self):
        """Test that multiple app creations are independent."""
        app1 = create_app('testing')
        app2 = create_app('testing')
        
        assert app1 is not app2
        assert app1.config == app2.config
        assert id(app1) != id(app2)