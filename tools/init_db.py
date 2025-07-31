#!/usr/bin/env python3
"""
Database initialization script for Shipping GUI application.
This script initializes the database without loading the full Flask app.
"""

from models import db, create_sample_data
from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


def initialize_database():
    """Initialize the database with proper configuration"""
    app = Flask(__name__)

    # Configure app for database initialization
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///shipping_automation.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    with app.app_context():
        db.init_app(app)
        db.create_all()

        # Create sample data if database is empty
        from models import Product

        if not Product.query.first():
            create_sample_data()
            print("Sample data created")
        else:
            print("Database already contains data")

    print("Database initialized successfully!")
    return True


if __name__ == "__main__":
    initialize_database()
