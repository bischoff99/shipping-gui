#!/usr/bin/env python3
"""
WSGI Configuration for Unified Order & Warehouse Management System
Production deployment entry point with enhanced configuration
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set production environment variables
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', '0')

# Import the Flask application
from app import app

# Production WSGI application instance
application = app

# Configure for production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    app.run(host='0.0.0.0', port=port, debug=False)
