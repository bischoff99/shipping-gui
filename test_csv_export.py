#!/usr/bin/env python3
"""
Test script for FedEx CSV export functionality
"""

import os
import sys
from datetime import datetime
from flask import Flask
from models import db, Order
from services.csv_integration import CSVProcessor

def create_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_shipping.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def create_sample_order(app):
    """Create a sample FedEx order for testing"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create a sample order
        order = Order(
            easyship_shipment_id="test_123456",
            tracking_number="1Z999AA1234567890",
            customer_name="John Test Customer",
            customer_email="john@test.com",
            customer_phone="+1234567890",
            address_line_1="123 Test Street",
            address_line_2="Apt 4B",
            city="Test City",
            state="CA",
            postal_code="90210",
            country="US",
            carrier="FEDEX",
            service_type="FedEx International Priority",
            total_weight_grams=500.0,
            total_value=50.00,
            order_status="shipped",
            booking_status="confirmed",
            shipping_cost=15.99,
            total_cost=15.99,
            platform="easyship"
        )
        
        db.session.add(order)
        db.session.commit()
        
        print(f"✅ Created sample order with ID: {order.id}")
        return order

def test_csv_export(app):
    """Test CSV export functionality"""
    with app.app_context():
        print("\n🧪 Testing CSV Export Functionality...")
        
        # Initialize processor directly
        processor = CSVProcessor(db.session)
        
        # Test export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file = f"/root/projects/SHIPPING_GUI/data/exports/test_fedex_export_{timestamp}.csv"
        
        success = processor.export_fedex_orders_csv(test_file)
        
        if success and os.path.exists(test_file):
            print(f"✅ CSV export successful: {test_file}")
            
            # Read and display first few lines
            with open(test_file, 'r') as f:
                lines = f.readlines()[:5]  # First 5 lines
                print("\n📄 CSV Content Preview:")
                for i, line in enumerate(lines):
                    print(f"Line {i+1}: {line.strip()}")
            
            print(f"\n📊 File size: {os.path.getsize(test_file)} bytes")
            return True
        else:
            print("❌ CSV export failed")
            errors = processor.get_errors()
            if errors:
                print(f"Errors: {errors}")
            return False

def test_summary_functionality(app):
    """Test summary functionality"""
    with app.app_context():
        print("\n📈 Testing Summary Functionality...")
        
        processor = CSVProcessor(db.session)
        filters = {'carrier': 'FEDEX'}
        summary = processor.get_order_export_summary(filters)
        
        print(f"Total Orders: {summary.get('total_orders', 0)}")
        print(f"Total Value: ${summary.get('total_value', 0):.2f}")
        print(f"Status Breakdown: {summary.get('status_breakdown', {})}")
        print(f"Country Breakdown: {summary.get('country_breakdown', {})}")
        
        return summary

def main():
    """Main test function"""
    print("🚀 Starting FedEx CSV Export Test...")
    
    # Create Flask app
    app = create_app()
    
    try:
        # Create sample data
        sample_order = create_sample_order(app)
        
        # Test CSV export
        export_success = test_csv_export(app)
        
        # Test summary
        summary = test_summary_functionality(app)
        
        if export_success:
            print("\n✅ All tests passed! FedEx CSV export is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the implementation.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()