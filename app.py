from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from routing import OrderRoutingSystem
from validation import validate_order_data
from utils import parse_customer_input, format_customer_data, normalize_customer_data
from fedex_orders import FedExOrderProcessor
from veeqo_orders import VeeqoOrderProcessor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'unified_order_system_2025')

# Initialize API clients and routing system
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()
fedex_processor = FedExOrderProcessor()
veeqo_processor = VeeqoOrderProcessor()

# Initialize advanced product sync system
from advanced_product_sync import AdvancedProductSync
from inventory_monitor import RealTimeInventoryMonitor

product_sync = AdvancedProductSync(veeqo_api, easyship_api)
inventory_monitor = RealTimeInventoryMonitor(veeqo_api, easyship_api)

# Start inventory monitoring
inventory_monitor.start_monitoring(check_interval=300)  # Check every 5 minutes

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    """Order creation page"""
    if request.method == 'POST':
        # Parse customer input
        customer_input = request.form.get('customer_input', '').strip()
        selected_carrier = request.form.get('carrier', '').upper()
        
        if not customer_input:
            flash('Please enter customer details', 'error')
            return render_template('create_order.html', carriers=routing_system.get_carrier_options())
        
        # Parse customer data
        customer_data = parse_customer_input(customer_input)
        if not customer_data:
            flash('Could not parse customer details. Please check format.', 'error')
            return render_template('create_order.html', carriers=routing_system.get_carrier_options())
        
        # Normalize customer data (fix phone, postal code formats)
        customer_data = normalize_customer_data(customer_data)
        
        try:
            # Get warehouses based on routing decision
            if selected_carrier == 'FEDEX':
                warehouses = easyship_api.get_addresses()
                products = easyship_api.get_random_products(3)
            else:
                warehouses = veeqo_api.get_warehouses()
                products = veeqo_api.get_random_products(3)
            
            # Route the order
            routing_decision = routing_system.route_order(customer_data, warehouses)
            
            # Override with user selection if provided
            if selected_carrier:
                routing_decision.carrier = selected_carrier
                routing_decision.platform = routing_system.get_platform_for_carrier(selected_carrier)
            
            # Validate order data
            validation_result = validate_order_data(customer_data, routing_decision.warehouse_info, products)
            
            if not validation_result.is_valid:
                for error in validation_result.errors:
                    flash(error, 'error')
                return render_template('create_order.html', carriers=routing_system.get_carrier_options())
            
            # Show warnings
            for warning in validation_result.warnings:
                flash(warning, 'warning')
            
            # Create the order
            order_result = None
            if routing_decision.platform == 'EASYSHIP':
                origin_address = easyship_api.get_address_by_state('Nevada')  # Prefer Nevada
                if origin_address:
                    order_result = easyship_api.create_shipment(customer_data, products, origin_address.get('id'))
            else:
                warehouse = veeqo_api.get_warehouse_by_state('Nevada') or veeqo_api.get_warehouse_by_state('California')
                if warehouse:
                    order_result = veeqo_api.create_order(customer_data, products, warehouse.get('id'), routing_decision.carrier)
            
            if order_result:
                flash('Order created successfully!', 'success')
                return render_template('order_success.html', 
                                    order=order_result, 
                                    customer=customer_data,
                                    routing=routing_decision,
                                    products=products)
            else:
                flash('Failed to create order. Please try again.', 'error')
                
        except Exception as e:
            flash(f'Error processing order: {str(e)}', 'error')
    
    return render_template('create_order.html', carriers=routing_system.get_carrier_options())

@app.route('/sync_data')
def sync_data():
    """Sync products and warehouses from both platforms"""
    try:
        # Sync Veeqo data
        veeqo_warehouses = veeqo_api.get_warehouses()
        veeqo_products = veeqo_api.get_products()
        
        # Sync Easyship data
        easyship_addresses = easyship_api.get_addresses()
        easyship_products = easyship_api.get_products()
        
        # Save to local cache files
        with open('warehouses.json', 'w') as f:
            json.dump({
                'veeqo': veeqo_warehouses,
                'easyship': easyship_addresses,
                'last_updated': str(datetime.now())
            }, f, indent=2)
        
        with open('products.json', 'w') as f:
            json.dump({
                'veeqo': veeqo_products,
                'easyship': easyship_products,
                'last_updated': str(datetime.now())
            }, f, indent=2)
        
        flash('Data synchronized successfully!', 'success')
        return jsonify({
            'status': 'success',
            'veeqo_warehouses': len(veeqo_warehouses),
            'veeqo_products': len(veeqo_products),
            'easyship_addresses': len(easyship_addresses),
            'easyship_products': len(easyship_products)
        })
        
    except Exception as e:
        flash(f'Sync failed: {str(e)}', 'error')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/parse_customer', methods=['POST'])
def api_parse_customer():
    """API endpoint to parse customer input"""
    data = request.get_json()
    customer_input = data.get('input', '')
    
    parsed = parse_customer_input(customer_input)
    if parsed:
        return jsonify({'status': 'success', 'data': parsed})
    else:
        return jsonify({'status': 'error', 'message': 'Could not parse input'}), 400

@app.route('/dashboard')
def dashboard():
    """System dashboard"""
    try:
        # Get basic stats
        veeqo_warehouses = veeqo_api.get_warehouses()
        easyship_addresses = easyship_api.get_addresses()
        
        stats = {
            'veeqo_warehouses': len(veeqo_warehouses),
            'easyship_addresses': len(easyship_addresses),
            'total_locations': len(veeqo_warehouses) + len(easyship_addresses),
            'routing_rules': len(routing_system.carrier_platform_mapping)
        }
        
        return render_template('dashboard.html', stats=stats)
        
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'error')
        return render_template('dashboard.html', stats={})

@app.route('/enhanced_dashboard')
def enhanced_dashboard():
    """Enhanced system dashboard with advanced features"""
    try:
        # Get comprehensive stats for enhanced dashboard
        veeqo_warehouses = veeqo_api.get_warehouses()
        easyship_addresses = easyship_api.get_addresses()
        
        # Enhanced stats with more detailed information
        stats = {
            'veeqo_warehouses': len(veeqo_warehouses),
            'easyship_addresses': len(easyship_addresses),
            'total_locations': len(veeqo_warehouses) + len(easyship_addresses),
            'routing_rules': len(routing_system.carrier_platform_mapping),
            'orders_today': 145,  # This would come from your order database
            'revenue_today': '12567',  # This would come from your order database
            'avg_processing_time': '2.4'  # This would come from your processing metrics
        }
        
        return render_template('enhanced_dashboard.html', stats=stats)
        
    except Exception as e:
        flash(f'Enhanced dashboard error: {str(e)}', 'error')
        # Return with default stats if there's an error
        default_stats = {
            'veeqo_warehouses': 0,
            'easyship_addresses': 0,
            'total_locations': 0,
            'routing_rules': 0,
            'orders_today': 0,
            'revenue_today': '0',
            'avg_processing_time': '0'
        }
        return render_template('enhanced_dashboard.html', stats=default_stats)

@app.route('/fedex_orders')
def fedex_orders():
    """FedEx orders management page"""
    try:
        customers = fedex_processor.get_fedex_customers()
        summary = fedex_processor.get_fedex_customer_summary()
        
        return render_template('fedex_orders.html', 
                             customers=customers, 
                             summary=summary)
    except Exception as e:
        flash(f'FedEx orders error: {str(e)}', 'error')
        return render_template('fedex_orders.html', customers=[], summary={})

@app.route('/process_fedex_orders', methods=['POST'])
def process_fedex_orders():
    """Process all FedEx orders"""
    try:
        results = fedex_processor.process_all_fedex_orders()
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        flash(f'Processed {successful}/{total} FedEx orders successfully!', 'success')
        
        return jsonify({
            'status': 'success',
            'processed': total,
            'successful': successful,
            'results': results
        })
        
    except Exception as e:
        flash(f'FedEx processing error: {str(e)}', 'error')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/create_fedex_order/<customer_name>', methods=['POST'])
def create_fedex_order(customer_name):
    """Create a single FedEx order for specific customer"""
    try:
        customer = fedex_processor.get_fedex_customer_by_name(customer_name)
        if not customer:
            return jsonify({'status': 'error', 'message': 'Customer not found'}), 404
        
        result = fedex_processor.create_fedex_shipment(customer)
        
        if result:
            flash(f'FedEx order created for {customer_name}!', 'success')
            return jsonify({'status': 'success', 'result': result})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create shipment'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/veeqo_orders')
def veeqo_orders():
    """Veeqo orders management page"""
    try:
        customers = veeqo_processor.get_veeqo_customers()
        summary = veeqo_processor.get_veeqo_customer_summary()
        
        return render_template('veeqo_orders.html', 
                             customers=customers, 
                             summary=summary)
    except Exception as e:
        flash(f'Veeqo orders error: {str(e)}', 'error')
        return render_template('veeqo_orders.html', customers=[], summary={})

@app.route('/process_veeqo_orders', methods=['POST'])
def process_veeqo_orders():
    """Process all Veeqo orders"""
    try:
        results = veeqo_processor.process_all_veeqo_orders()
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        flash(f'Processed {successful}/{total} Veeqo orders successfully!', 'success')
        
        return jsonify({
            'status': 'success',
            'processed': total,
            'successful': successful,
            'results': results
        })
        
    except Exception as e:
        flash(f'Veeqo processing error: {str(e)}', 'error')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/create_veeqo_order/<customer_name>', methods=['POST'])
def create_veeqo_order_route(customer_name):
    """Create a single Veeqo order for specific customer"""
    try:
        customer = veeqo_processor.get_veeqo_customer_by_name(customer_name)
        if not customer:
            return jsonify({'status': 'error', 'message': 'Customer not found'}), 404
        
        result = veeqo_processor.create_veeqo_order(customer)
        
        if result:
            flash(f'Veeqo {customer["carrier"]} order created for {customer_name}!', 'success')
            return jsonify({'status': 'success', 'result': result})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create order'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/veeqo_purchase_orders')
def api_veeqo_purchase_orders():
    """API endpoint to get Veeqo purchase orders"""
    try:
        purchase_orders = veeqo_processor.get_purchase_orders()
        return jsonify({
            'status': 'success',
            'purchase_orders': purchase_orders,
            'count': len(purchase_orders)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/product_sync_dashboard')
def product_sync_dashboard():
    """Advanced Product Sync Dashboard"""
    try:
        # Get sync stats
        sync_stats = product_sync.get_sync_stats()
        
        # Get inventory alerts
        inventory_alerts = product_sync.get_inventory_alerts()
        
        # Get performance data
        performance = product_sync.get_product_performance()
        
        return render_template('product_sync_dashboard.html', 
                             sync_stats=sync_stats,
                             inventory_alerts=inventory_alerts,
                             performance=performance)
    
    except Exception as e:
        flash(f'Product sync dashboard error: {str(e)}', 'error')
        return render_template('product_sync_dashboard.html', 
                             sync_stats={}, 
                             inventory_alerts=[], 
                             performance={})

@app.route('/api/sync_products', methods=['POST'])
def api_sync_products():
    """API endpoint to trigger product sync"""
    try:
        import asyncio
        result = asyncio.run(product_sync.sync_products_bidirectional())
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/product_stats')
def api_product_stats():
    """API endpoint for real-time product statistics"""
    try:
        stats = product_sync.get_sync_stats()
        performance = product_sync.get_product_performance()
        alerts = product_sync.get_inventory_alerts()
        
        return jsonify({
            'stats': stats,
            'performance': performance,
            'alerts': alerts,
            'alert_count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/start_auto_sync', methods=['POST'])
def api_start_auto_sync():
    """Start automatic product sync"""
    try:
        interval = request.json.get('interval', 5)  # minutes
        product_sync.start_auto_sync(interval)
        
        return jsonify({
            'status': 'success',
            'message': f'Auto-sync started with {interval} minute interval'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stop_auto_sync', methods=['POST'])
def api_stop_auto_sync():
    """Stop automatic product sync"""
    try:
        product_sync.stop_auto_sync()
        return jsonify({'status': 'success', 'message': 'Auto-sync stopped'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/inventory_alerts')
def api_inventory_alerts():
    """Get active inventory alerts"""
    try:
        alerts = inventory_monitor.get_active_alerts()
        return jsonify([
            {
                'id': alert.id,
                'product_sku': alert.product_sku,
                'product_name': alert.product_name,
                'warehouse_name': alert.warehouse_name,
                'current_stock': alert.current_stock,
                'threshold': alert.threshold,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'created_at': alert.created_at
            } for alert in alerts
        ])
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/inventory_summary')
def api_inventory_summary():
    """Get inventory summary"""
    try:
        summary = inventory_monitor.get_inventory_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reorder_suggestions')
def api_reorder_suggestions():
    """Get reorder suggestions"""
    try:
        suggestions = inventory_monitor.generate_reorder_suggestions()
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/resolve_alert/<alert_id>', methods=['POST'])
def api_resolve_alert(alert_id):
    """Resolve inventory alert"""
    try:
        success = inventory_monitor.resolve_alert(alert_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Alert resolved'})
        else:
            return jsonify({'status': 'error', 'message': 'Alert not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # For local development
    # app.run(debug=True)
    
    # For online deployment - accessible from any IP
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
