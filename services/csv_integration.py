import csv
import logging
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from models import Product, Warehouse, Order

# Configure logging
logger = logging.getLogger("csv_integration")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("csv_integration.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class CSVProcessor:
    def __init__(self, db_session):
        self.db_session = db_session
        self.progress = 0
        self.errors = []

    @staticmethod
    def lb_to_grams(lb):
        return round(Decimal(lb) * Decimal("453.592"), 2)

    @staticmethod
    def oz_to_grams(oz):
        return round(Decimal(oz) * Decimal("28.3495"), 2)

    @staticmethod
    def inches_to_cm(inches):
        return round(Decimal(inches) * Decimal("2.54"), 2)

    @staticmethod
    def normalize_sku(sku):
        if sku and sku.startswith("DENIM-"):
            return sku.upper()
        return None

    def process_products_csv(self, file_path, source="easyship"):
        logger.info(f"Processing products CSV: {file_path} (source={source})")
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            products = []
            for row in reader:
                try:
                    sku = self.normalize_sku(
                        row.get("SKU / ASIN / ID") or row.get("sku_code")
                    )
                    if not sku:
                        raise ValueError("Invalid SKU format")
                    # Weight conversion
                    if source == "easyship":
                        weight_grams = self.lb_to_grams(row["Product Weight (lb)"])
                    else:
                        weight_grams = self.oz_to_grams(row["weight"])
                    # Dimensions
                    length_cm = self.inches_to_cm(row.get("Length (in)", 0))
                    width_cm = self.inches_to_cm(row.get("Width (in)", 0))
                    height_cm = self.inches_to_cm(row.get("Height (in)", 0))
                    # Price
                    sales_price = Decimal(row.get("sales_price") or 0)
                    cost_price = Decimal(row.get("cost_price") or 0)
                    # Boolean fields
                    contains_liquid = row.get("Contain Liquid", "No").lower() == "yes"
                    contains_battery = row.get("Contain Battery", "No").lower() == "yes"
                    hazmat = row.get("hazmat", "No").lower() == "yes"
                    # Create product
                    product = Product(
                        sku=sku,
                        title=row.get("Product Description")
                        or row.get("product_title"),
                        weight_grams=weight_grams,
                        length_cm=length_cm,
                        width_cm=width_cm,
                        height_cm=height_cm,
                        price=sales_price,
                        cost_price=cost_price,
                        brand=row.get("Brand") or row.get("brand"),
                        category=row.get("Easyship category") or row.get("tariff_code"),
                        description=row.get("Product Description")
                        or row.get("description"),
                        active=True,
                    )
                    products.append(product)
                except Exception as e:
                    logger.error(f"Error processing product row: {row} | {e}")
                    self.errors.append(str(e))
            self.bulk_insert_products(products)

    def bulk_insert_products(self, products):
        logger.info(f"Bulk inserting {len(products)} products.")
        try:
            for product in products:
                existing = (
                    self.db_session.query(Product).filter_by(sku=product.sku).first()
                )
                if not existing:
                    self.db_session.add(product)
            self.db_session.commit()
            logger.info("Product import committed.")
        except SQLAlchemyError as e:
            logger.error(f"Bulk insert failed: {e}")
            self.db_session.rollback()
            self.errors.append(str(e))

    def process_warehouses_csv(self, file_path, source="veeqo"):
        logger.info(f"Processing warehouses CSV: {file_path} (source={source})")
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            warehouses = []
            for row in reader:
                try:
                    state = row.get("region") or row.get("state")
                    routing = (
                        "veeqo"
                        if state == "NV"
                        else "easyship" if state == "CA" else None
                    )
                    warehouse = Warehouse(
                        external_id=row.get("external_id"),
                        name=row.get("name") or row.get("company"),
                        address_line_1=row.get("address1") or row.get("street1"),
                        address_line_2=row.get("address2") or row.get("street2"),
                        city=row.get("city"),
                        state=state,
                        postal_code=row.get("postal_code"),
                        country=row.get("country_code"),
                        phone=row.get("phone"),
                        platform=routing,
                    )
                    warehouses.append(warehouse)
                except Exception as e:
                    logger.error(f"Error processing warehouse row: {row} | {e}")
                    self.errors.append(str(e))
            self.bulk_insert_warehouses(warehouses)

    def bulk_insert_warehouses(self, warehouses):
        logger.info(f"Bulk inserting {len(warehouses)} warehouses.")
        try:
            for warehouse in warehouses:
                existing = (
                    self.db_session.query(Warehouse)
                    .filter_by(external_id=warehouse.external_id)
                    .first()
                )
                if not existing:
                    self.db_session.add(warehouse)
            self.db_session.commit()
            logger.info("Warehouse import committed.")
        except SQLAlchemyError as e:
            logger.error(f"Bulk insert failed: {e}")
            self.db_session.rollback()
            self.errors.append(str(e))

    def get_progress(self):
        return self.progress

    def get_errors(self):
        return self.errors

    def export_orders_csv(self, file_path: str, filters: Dict = None) -> bool:
        """Export orders to CSV file with optional filters"""
        logger.info(f"Exporting orders to CSV: {file_path}")
        
        try:
            # Build query with filters
            query = self.db_session.query(Order)
            
            if filters:
                if filters.get('carrier'):
                    query = query.filter(Order.carrier == filters['carrier'].upper())
                if filters.get('status'):
                    query = query.filter(Order.order_status == filters['status'].lower())
                if filters.get('start_date'):
                    query = query.filter(Order.created_at >= filters['start_date'])
                if filters.get('end_date'):
                    query = query.filter(Order.created_at <= filters['end_date'])
                if filters.get('country'):
                    query = query.filter(Order.country == filters['country'].upper())
            
            orders = query.order_by(Order.created_at.desc()).all()
            
            if not orders:
                logger.warning("No orders found matching the criteria")
                self.errors.append("No orders found matching the criteria")
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Get CSV headers from the first order
                if orders:
                    fieldnames = list(orders[0].to_csv_dict().keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for order in orders:
                        writer.writerow(order.to_csv_dict())
            
            logger.info(f"Successfully exported {len(orders)} orders to {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to export orders to CSV: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False

    def export_fedex_orders_csv(self, file_path: str, date_range: Optional[Dict] = None) -> bool:
        """Export FedEx orders specifically to CSV"""
        filters = {'carrier': 'FEDEX'}
        if date_range:
            filters.update(date_range)
        
        return self.export_orders_csv(file_path, filters)

    def get_order_export_summary(self, filters: Dict = None) -> Dict:
        """Get summary of orders that would be exported"""
        try:
            query = self.db_session.query(Order)
            
            if filters:
                if filters.get('carrier'):
                    query = query.filter(Order.carrier == filters['carrier'].upper())
                if filters.get('status'):
                    query = query.filter(Order.order_status == filters['status'].lower())
                if filters.get('start_date'):
                    query = query.filter(Order.created_at >= filters['start_date'])
                if filters.get('end_date'):
                    query = query.filter(Order.created_at <= filters['end_date'])
                if filters.get('country'):
                    query = query.filter(Order.country == filters['country'].upper())
            
            orders = query.all()
            
            # Calculate summary statistics
            total_orders = len(orders)
            total_value = sum(float(order.total_value or 0) for order in orders)
            total_cost = sum(float(order.total_cost or 0) for order in orders)
            
            status_breakdown = {}
            country_breakdown = {}
            carrier_breakdown = {}
            
            for order in orders:
                # Status breakdown
                status = order.order_status
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
                
                # Country breakdown
                country = order.country
                country_breakdown[country] = country_breakdown.get(country, 0) + 1
                
                # Carrier breakdown
                carrier = order.carrier
                carrier_breakdown[carrier] = carrier_breakdown.get(carrier, 0) + 1
            
            return {
                'total_orders': total_orders,
                'total_value': total_value,
                'total_cost': total_cost,
                'status_breakdown': status_breakdown,
                'country_breakdown': country_breakdown,
                'carrier_breakdown': carrier_breakdown,
                'date_range': {
                    'earliest': min(order.created_at for order in orders).isoformat() if orders else None,
                    'latest': max(order.created_at for order in orders).isoformat() if orders else None
                }
            }
            
        except Exception as e:
            error_msg = f"Failed to get order export summary: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {}
