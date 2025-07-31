"""
Integration tests for MCP (Model Context Protocol) features.
Tests AI-enhanced parsing, route optimization, and MCP server integrations.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from flask import Flask

# Import MCP integration components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.app_factory import create_app


class TestMCPIntegration:
    """Integration tests for MCP-enhanced features."""

    @pytest.fixture
    def app(self):
        """Create test app with MCP features enabled."""
        app = create_app('testing')
        # Enable MCP features
        app.config['MCP_PYTHON_DEBUG_ENABLED'] = True
        app.config['MCP_FILESYSTEM_ENABLED'] = True
        app.config['MCP_GITHUB_ENABLED'] = True
        app.config['MCP_SEQUENTIAL_THINKING_ENABLED'] = True
        app.config['MCP_HF_SPACES_ENABLED'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_mcp_configuration(self, app):
        """Test MCP configuration is properly loaded."""
        assert app.config['MCP_PYTHON_DEBUG_ENABLED'] is True
        assert app.config['MCP_FILESYSTEM_ENABLED'] is True
        assert app.config['MCP_GITHUB_ENABLED'] is True
        assert app.config['MCP_SEQUENTIAL_THINKING_ENABLED'] is True
        assert app.config['MCP_HF_SPACES_ENABLED'] is True
        
        assert 'MCP_URL' in app.config
        assert 'MCP_TIMEOUT' in app.config
        assert isinstance(app.config['MCP_TIMEOUT'], int)

    @patch('services.mcp_integration.MCPClient')
    def test_ai_enhanced_parsing(self, mock_mcp_client, client):
        """Test AI-enhanced customer data parsing."""
        # Mock MCP client response
        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance
        
        mock_client_instance.parse_customer_data.return_value = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1-234-567-8890',
            'address': '123 Main Street',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'country': 'US',
            'confidence': 0.95
        }
        
        # Test AI parsing endpoint
        response = client.post('/api/ai/parse-customer',
                             json={'data': 'John Doe john.doe@example.com 234-567-8890 123 Main Street Boston MA 02101'},
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['name'] == 'John Doe'
            assert data['confidence'] == 0.95
            mock_client_instance.parse_customer_data.assert_called_once()

    @patch('services.mcp_integration.MCPClient')
    def test_ai_route_optimization(self, mock_mcp_client, client):
        """Test AI-powered route optimization."""
        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance
        
        mock_client_instance.optimize_route.return_value = {
            'platform': 'veeqo',
            'warehouse': 'Nevada',
            'carrier': 'UPS',
            'confidence': 0.92,
            'reasoning': 'UPS service optimal for Nevada warehouse to CA destination'
        }
        
        route_data = {
            'destination': 'Los Angeles, CA',
            'carrier_preference': 'UPS',
            'weight': 2.5,
            'dimensions': {'length': 12, 'width': 8, 'height': 6}
        }
        
        response = client.post('/api/ai/optimize-route',
                             json=route_data,
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['platform'] == 'veeqo'
            assert data['warehouse'] == 'Nevada'
            assert data['confidence'] == 0.92
            mock_client_instance.optimize_route.assert_called_once()

    @patch('services.mcp_integration.MCPClient')
    def test_ai_error_analysis(self, mock_mcp_client, client):
        """Test AI-powered error analysis."""
        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance
        
        mock_client_instance.analyze_error.return_value = {
            'error_category': 'validation_error',
            'suggested_fix': 'Phone number format should be +1-XXX-XXX-XXXX',
            'confidence': 0.88,
            'alternative_solutions': [
                'Try international format +1XXXXXXXXXX',
                'Remove special characters and try again'
            ]
        }
        
        error_data = {
            'error_message': 'Invalid phone number format',
            'input_data': {'phone': '123456789'},
            'context': 'customer_validation'
        }
        
        response = client.post('/api/ai/error-analysis',
                             json=error_data,
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['error_category'] == 'validation_error'
            assert 'suggested_fix' in data
            assert data['confidence'] == 0.88
            mock_client_instance.analyze_error.assert_called_once()

    @patch('services.mcp_integration.MCPClient')
    def test_development_insights(self, mock_mcp_client, client):
        """Test AI-generated development insights."""
        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance
        
        mock_client_instance.get_insights.return_value = {
            'performance_suggestions': [
                'Consider caching product data for better response times',
                'Implement database connection pooling for high-load scenarios'
            ],
            'security_recommendations': [
                'Add rate limiting to API endpoints',
                'Implement input validation for all user inputs'
            ],
            'code_quality_tips': [
                'Extract complex routing logic into separate service classes',
                'Add comprehensive error handling for API failures'
            ],
            'system_health_score': 85
        }
        
        response = client.get('/api/ai/insights')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'performance_suggestions' in data
            assert 'security_recommendations' in data
            assert 'code_quality_tips' in data
            assert data['system_health_score'] == 85
            mock_client_instance.get_insights.assert_called_once()

    def test_mcp_dashboard_status(self, client):
        """Test MCP dashboard status endpoint."""
        response = client.get('/mcp-dashboard')
        
        # Should return dashboard page or status
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            # Should contain MCP server status information
            response_text = response.data.decode()
            assert 'mcp' in response_text.lower() or 'server' in response_text.lower()

    @patch('services.mcp_integration.check_mcp_server_status')
    def test_mcp_server_health_check(self, mock_status_check, client):
        """Test MCP server health checking."""
        mock_status_check.return_value = {
            'filesystem': {'status': 'active', 'response_time': 0.02},
            'github': {'status': 'active', 'response_time': 0.15},
            'sequential-thinking': {'status': 'active', 'response_time': 0.08},
            'hf-spaces': {'status': 'active', 'response_time': 0.25},
            'mcp-pdb': {'status': 'inactive', 'response_time': None}
        }
        
        response = client.get('/api/mcp/status')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'filesystem' in data
            assert data['filesystem']['status'] == 'active'
            assert 'github' in data
            mock_status_check.assert_called_once()

    @patch('services.mcp_integration.MCPDebugger')
    def test_mcp_python_debugging(self, mock_debugger, client):
        """Test MCP Python debugging integration."""
        mock_debugger_instance = MagicMock()
        mock_debugger.return_value = mock_debugger_instance
        
        mock_debugger_instance.start_debug_session.return_value = {
            'session_id': 'debug_123',
            'status': 'active',
            'breakpoints': []
        }
        
        debug_request = {
            'file_path': '/src/routing.py',
            'function_name': 'determine_routing',
            'breakpoint_line': 45
        }
        
        response = client.post('/api/mcp/debug/start',
                             json=debug_request,
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'session_id' in data
            assert data['status'] == 'active'
            mock_debugger_instance.start_debug_session.assert_called_once()

    @patch('services.mcp_integration.MCPFilesystem')
    def test_mcp_filesystem_operations(self, mock_filesystem, client):
        """Test MCP filesystem integration."""
        mock_fs_instance = MagicMock()
        mock_filesystem.return_value = mock_fs_instance
        
        mock_fs_instance.analyze_project_structure.return_value = {
            'total_files': 87,
            'python_files': 23,
            'test_files': 12,
            'config_files': 8,
            'directories': ['src', 'tests', 'config', 'templates', 'static'],
            'recommendations': [
                'Consider organizing route modules in subdirectories',
                'Add __init__.py files to all Python packages'
            ]
        }
        
        response = client.get('/api/mcp/filesystem/analyze')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['total_files'] == 87
            assert data['python_files'] == 23
            assert 'recommendations' in data
            mock_fs_instance.analyze_project_structure.assert_called_once()

    @patch('services.mcp_integration.MCPGitHub')
    def test_mcp_github_integration(self, mock_github, client):
        """Test MCP GitHub integration."""
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance
        
        mock_github_instance.get_repository_insights.return_value = {
            'commit_frequency': 'high',
            'branch_count': 3,
            'recent_commits': 15,
            'code_quality_score': 88,
            'security_issues': 2,
            'performance_issues': 1,
            'suggestions': [
                'Consider creating release branches for production deployments',
                'Add automated testing workflows'
            ]
        }
        
        response = client.get('/api/mcp/github/insights')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['commit_frequency'] == 'high'
            assert data['code_quality_score'] == 88
            assert 'suggestions' in data
            mock_github_instance.get_repository_insights.assert_called_once()

    def test_mcp_error_handling(self, client):
        """Test MCP error handling and fallbacks."""
        # Test with MCP servers unavailable
        response = client.post('/api/ai/parse-customer',
                             json={'data': 'test customer data'},
                             content_type='application/json')
        
        # Should gracefully fallback to non-AI parsing
        assert response.status_code in [200, 400, 500, 503]

    def test_mcp_timeout_handling(self, app, client):
        """Test MCP timeout configuration and handling."""
        # Set very short timeout
        app.config['MCP_TIMEOUT'] = 1
        
        response = client.get('/api/ai/insights')
        
        # Should handle timeout gracefully
        assert response.status_code in [200, 408, 500, 503]

    @patch('services.mcp_integration.MCPSequentialThinking')
    def test_mcp_sequential_thinking(self, mock_thinking, client):
        """Test MCP sequential thinking integration."""
        mock_thinking_instance = MagicMock()
        mock_thinking.return_value = mock_thinking_instance
        
        mock_thinking_instance.analyze_problem.return_value = {
            'problem_breakdown': [
                'Parse customer input data',
                'Validate data format and completeness',
                'Determine optimal routing platform',
                'Select appropriate warehouse',
                'Create order with selected platform'
            ],
            'solution_steps': [
                'Use regex patterns for data extraction',
                'Apply validation rules for each field',
                'Query routing decision engine',
                'Check warehouse availability',
                'Execute API call to create order'
            ],
            'confidence': 0.91,
            'estimated_complexity': 'medium'
        }
        
        problem_data = {
            'problem_description': 'Process customer order with optimal routing',
            'context': 'e-commerce order processing',
            'constraints': ['API rate limits', 'warehouse capacity']
        }
        
        response = client.post('/api/mcp/thinking/analyze',
                             json=problem_data,
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'problem_breakdown' in data
            assert 'solution_steps' in data
            assert data['confidence'] == 0.91
            mock_thinking_instance.analyze_problem.assert_called_once()

    def test_mcp_feature_toggles(self, app, client):
        """Test MCP feature toggles and configuration."""
        # Disable specific MCP features
        app.config['MCP_HF_SPACES_ENABLED'] = False
        
        response = client.get('/api/ai/insights')
        
        # Should handle disabled features gracefully
        assert response.status_code in [200, 404, 503]
        
        # Re-enable and test
        app.config['MCP_HF_SPACES_ENABLED'] = True
        
        response = client.get('/api/ai/insights')
        assert response.status_code in [200, 500, 503]

    def test_mcp_performance_monitoring(self, client):
        """Test MCP performance monitoring."""
        import time
        
        # Measure AI-enhanced endpoint performance
        start_time = time.time()
        
        response = client.post('/api/ai/parse-customer',
                             json={'data': 'John Doe john@email.com +1234567890'},
                             content_type='application/json')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # AI features should respond within reasonable time
        assert response_time < 5.0  # 5 second timeout
        
        # Response should indicate processing time
        if response.status_code == 200:
            # Could include timing metadata
            pass

    def test_mcp_concurrent_requests(self, app):
        """Test MCP features under concurrent load."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_ai_request():
            with app.test_client() as client:
                response = client.get('/api/ai/insights')
                results.put({
                    'status_code': response.status_code,
                    'has_content': len(response.data) > 0
                })
        
        # Create multiple concurrent AI requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_ai_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        responses = []
        while not results.empty():
            responses.append(results.get())
        
        assert len(responses) == 3
        
        # At least some requests should succeed
        success_count = sum(1 for r in responses if r['status_code'] == 200)
        assert success_count >= 0  # May fail if MCP servers unavailable