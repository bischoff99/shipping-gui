from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
    jsonify,
)
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from services.csv_integration import CSVProcessor
from models import db, Order
from fedex_orders import FedExOrderProcessor

csv_management = Blueprint("csv_management", __name__, template_folder="templates")


@csv_management.route("/csv/upload", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected", "danger")
            return redirect(request.url)
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)
        flash(f"File {filename} uploaded successfully.", "success")
        return redirect(url_for("csv_management.preview_csv", filename=filename))
    return render_template("csv_upload.html")


@csv_management.route("/csv/preview/<filename>")
def preview_csv(filename):
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    # Preview first 5 rows
    import csv

    with open(upload_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for i, row in enumerate(reader) if i < 5]
    return render_template("csv_preview.html", filename=filename, rows=rows)


@csv_management.route("/csv/import/<filename>", methods=["POST"])
def import_csv(filename):
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    processor = CSVProcessor(db.session)
    # Determine type by filename or user input
    if "product" in filename.lower():
        processor.process_products_csv(upload_path)
    elif "warehouse" in filename.lower():
        processor.process_warehouses_csv(upload_path)
    else:
        flash("Unknown CSV type.", "danger")
        return redirect(url_for("csv_management.upload_csv"))
    errors = processor.get_errors()
    if errors:
        flash(f"Import completed with errors: {errors}", "warning")
    else:
        flash("Import successful!", "success")
    return redirect(url_for("csv_management.upload_csv"))


@csv_management.route("/csv/history")
def import_history():
    # Placeholder: implement import history tracking
    return render_template("csv_history.html", history=[])


@csv_management.route("/csv/export")
def export_dashboard():
    """CSV export dashboard"""
    processor = CSVProcessor(db.session)
    fedex_processor = FedExOrderProcessor()
    
    # Get summary statistics
    all_orders_summary = processor.get_order_export_summary()
    fedex_summary = fedex_processor.get_fedex_orders_summary()
    
    return render_template("csv_export_dashboard.html", 
                         all_orders_summary=all_orders_summary,
                         fedex_summary=fedex_summary)


@csv_management.route("/csv/export/fedex", methods=["GET", "POST"])
def export_fedex_orders():
    """Export FedEx orders to CSV"""
    if request.method == "POST":
        try:
            fedex_processor = FedExOrderProcessor()
            
            # Get form data for date filtering
            days_back = int(request.form.get('days_back', 30))
            include_all = request.form.get('include_all') == 'true'
            
            if include_all:
                # Export all FedEx orders
                file_path = fedex_processor.export_fedex_orders_to_csv()
            else:
                # Export recent orders
                file_path = fedex_processor.export_recent_fedex_orders(days=days_back)
            
            if file_path:
                flash(f"FedEx orders exported successfully!", "success")
                return send_file(file_path, as_attachment=True, 
                               download_name=os.path.basename(file_path))
            else:
                flash("Failed to export FedEx orders. Check logs for details.", "danger")
                
        except Exception as e:
            flash(f"Export failed: {str(e)}", "danger")
    
    # GET request - show the form
    fedex_processor = FedExOrderProcessor()
    summary = fedex_processor.get_fedex_orders_summary()
    
    return render_template("fedex_csv_export.html", summary=summary)


@csv_management.route("/csv/export/all-orders", methods=["GET", "POST"])
def export_all_orders():
    """Export all orders to CSV with filtering"""
    if request.method == "POST":
        try:
            processor = CSVProcessor(db.session)
            
            # Build filters from form data
            filters = {}
            if request.form.get('carrier'):
                filters['carrier'] = request.form.get('carrier')
            if request.form.get('status'):
                filters['status'] = request.form.get('status')
            if request.form.get('country'):
                filters['country'] = request.form.get('country')
            
            # Date range filtering
            if request.form.get('start_date'):
                filters['start_date'] = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            if request.form.get('end_date'):
                filters['end_date'] = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            # Generate file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exports_dir = os.path.join("data", "exports")
            os.makedirs(exports_dir, exist_ok=True)
            file_path = os.path.join(exports_dir, f"all_orders_{timestamp}.csv")
            
            success = processor.export_orders_csv(file_path, filters)
            
            if success:
                flash("Orders exported successfully!", "success")
                return send_file(file_path, as_attachment=True, 
                               download_name=os.path.basename(file_path))
            else:
                errors = processor.get_errors()
                flash(f"Export failed: {'; '.join(errors)}", "danger")
                
        except Exception as e:
            flash(f"Export failed: {str(e)}", "danger")
    
    # GET request - show the form
    processor = CSVProcessor(db.session)
    summary = processor.get_order_export_summary()
    
    # Get unique values for filter dropdowns
    carriers = db.session.query(Order.carrier).distinct().all()
    countries = db.session.query(Order.country).distinct().all()
    statuses = db.session.query(Order.order_status).distinct().all()
    
    return render_template("all_orders_csv_export.html", 
                         summary=summary,
                         carriers=[c[0] for c in carriers],
                         countries=[c[0] for c in countries],
                         statuses=[s[0] for s in statuses])


@csv_management.route("/api/orders/summary")
def api_orders_summary():
    """API endpoint for orders summary"""
    try:
        processor = CSVProcessor(db.session)
        
        # Get filters from query parameters
        filters = {}
        if request.args.get('carrier'):
            filters['carrier'] = request.args.get('carrier')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('country'):
            filters['country'] = request.args.get('country')
        if request.args.get('days_back'):
            days_back = int(request.args.get('days_back'))
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            filters['start_date'] = start_date
            filters['end_date'] = end_date
        
        summary = processor.get_order_export_summary(filters)
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@csv_management.route("/csv/test-data")
def create_test_data():
    """Create test FedEx orders for CSV export testing"""
    try:
        fedex_processor = FedExOrderProcessor()
        
        # Process a few test orders
        results = []
        for i, customer in enumerate(fedex_processor.fedex_customers[:3]):  # Test with first 3 customers
            print(f"Creating test order {i+1} for {customer['name']}...")
            
            # Create a mock result (without actually calling APIs)
            mock_result = {
                "shipment": {"id": f"test_shipment_{i+1}"},
                "booking": {"tracking_number": f"TEST{datetime.now().strftime('%Y%m%d')}00{i+1}",
                           "service": "FedEx International Priority"}
            }
            
            # Save to database
            products = [
                {"title": "Test Product 1", "weight": 0.5, "price": 25.00},
                {"title": "Test Product 2", "weight": 0.3, "price": 15.00}
            ]
            
            order = fedex_processor.save_order_to_database(customer, mock_result, products)
            if order:
                results.append(f"Created test order ID {order.id} for {customer['name']}")
            else:
                results.append(f"Failed to create test order for {customer['name']}")
        
        flash(f"Test data created: {len(results)} test orders", "success")
        return render_template("test_data_results.html", results=results)
        
    except Exception as e:
        flash(f"Failed to create test data: {str(e)}", "danger")
        return redirect(url_for("csv_management.export_dashboard"))
