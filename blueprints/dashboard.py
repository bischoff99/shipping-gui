"""
Simplified Shipping Dashboard Blueprint
Comprehensive overview of shipping operations and inventory
"""

from flask import Blueprint, render_template, jsonify
from sqlalchemy import func, and_, or_
from datetime import datetime
from models import db, Product, Warehouse, ProductInventory
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from typing import Dict

dashboard_bp = Blueprint("dashboard", __name__)


class DashboardService:
    """Service class for dashboard data aggregation"""

    @staticmethod
    def get_shipping_overview() -> Dict:
        """Get comprehensive shipping overview"""
        # Current inventory status
        total_inventory = (
            db.session.query(func.sum(ProductInventory.quantity)).scalar() or 0
        )

        total_value = (
            db.session.query(func.sum(ProductInventory.quantity * Product.price))
            .join(Product)
            .filter(Product.active == True)
            .scalar()
            or 0
        )

        # Platform distribution
        nevada_warehouses = Warehouse.query.filter(
            or_(Warehouse.state.like("%Nevada%"), Warehouse.platform == "veeqo")
        ).count()

        california_warehouses = Warehouse.query.filter(
            or_(
                Warehouse.state.like("%California%"),
                Warehouse.platform == "easyship",
            )
        ).count()

        # Stock alerts
        low_stock_count = (
            ProductInventory.query.join(Product)
            .filter(
                and_(
                    ProductInventory.quantity <= ProductInventory.min_reorder_level,
                    Product.active == True,
                )
            )
            .count()
        )

        out_of_stock_count = (
            ProductInventory.query.join(Product)
            .filter(and_(ProductInventory.quantity == 0, Product.active == True))
            .count()
        )

        return {
            "total_inventory": int(total_inventory),
            "total_value": float(total_value),
            "nevada_warehouses": nevada_warehouses,
            "california_warehouses": california_warehouses,
            "low_stock_alerts": low_stock_count,
            "out_of_stock_alerts": out_of_stock_count,
            "total_products": Product.query.filter_by(active=True).count(),
            "total_warehouses": Warehouse.query.count(),
        }

    @staticmethod
    def get_platform_status() -> Dict:
        """Get Veeqo and Easyship platform status"""
        veeqo_api = VeeqoAPI()
        easyship_api = EasyshipAPI()

        # Test API connections and get basic stats
        veeqo_status = {
            "connected": False,
            "warehouses": 0,
            "products": 0,
            "last_sync": "Never",
        }

        easyship_status = {
            "connected": False,
            "addresses": 0,
            "products": 0,
            "last_sync": "Never",
        }

        try:
            veeqo_warehouses = veeqo_api.get_warehouses()
            if veeqo_warehouses:
                veeqo_status["connected"] = True
                veeqo_status["warehouses"] = len(veeqo_warehouses)
                veeqo_status["last_sync"] = datetime.now().strftime("%H:%M")
        except Exception as e:
            print(f"Veeqo API error: {e}")

        try:
            easyship_addresses = easyship_api.get_addresses()
            if easyship_addresses:
                easyship_status["connected"] = True
                easyship_status["addresses"] = len(easyship_addresses)
                easyship_status["last_sync"] = datetime.now().strftime("%H:%M")
        except Exception as e:
            print(f"Easyship API error: {e}")

        return {"veeqo": veeqo_status, "easyship": easyship_status}

    @staticmethod
    def get_inventory_distribution() -> Dict:
        """Get inventory distribution by state/platform"""
        # Nevada (Veeqo) inventory
        nevada_inventory = (
            db.session.query(func.sum(ProductInventory.quantity))
            .join(Warehouse)
            .filter(
                or_(
                    Warehouse.state.like("%Nevada%"),
                    Warehouse.platform == "veeqo",
                )
            )
            .scalar()
            or 0
        )

        # California (Easyship) inventory
        california_inventory = (
            db.session.query(func.sum(ProductInventory.quantity))
            .join(Warehouse)
            .filter(
                or_(
                    Warehouse.state.like("%California%"),
                    Warehouse.platform == "easyship",
                )
            )
            .scalar()
            or 0
        )

        # Top products by inventory
        top_products = (
            db.session.query(
                Product.title,
                Product.sku,
                func.sum(ProductInventory.quantity).label("total_qty"),
            )
            .join(ProductInventory)
            .filter(Product.active == True)
            .group_by(Product.id)
            .order_by(func.sum(ProductInventory.quantity).desc())
            .limit(5)
            .all()
        )

        # Low stock products
        low_stock_products = (
            db.session.query(
                Product.title,
                Product.sku,
                ProductInventory.quantity,
                ProductInventory.min_reorder_level,
                Warehouse.name.label("warehouse_name"),
            )
            .join(ProductInventory)
            .join(Warehouse)
            .filter(
                and_(
                    ProductInventory.quantity <= ProductInventory.min_reorder_level,
                    Product.active == True,
                )
            )
            .limit(5)
            .all()
        )

        return {
            "nevada_inventory": int(nevada_inventory),
            "california_inventory": int(california_inventory),
            "top_products": [
                {"title": p.title, "sku": p.sku, "quantity": int(p.total_qty)}
                for p in top_products
            ],
            "low_stock_products": [
                {
                    "title": p.title,
                    "sku": p.sku,
                    "current_qty": p.quantity,
                    "min_level": p.min_reorder_level,
                    "warehouse": p.warehouse_name,
                }
                for p in low_stock_products
            ],
        }

    @staticmethod
    def get_shipping_rates_preview() -> Dict:
        """Get sample shipping rates for common routes"""
        # Mock shipping rates for demonstration
        # In production, this would call actual APIs
        return {
            "nevada_to_california": {
                "ups": "$8.50",
                "dhl": "$9.25",
                "usps": "$7.75",
            },
            "nevada_to_newyork": {
                "ups": "$12.50",
                "dhl": "$14.25",
                "usps": "$10.50",
            },
            "california_to_florida": {
                "fedex_ground": "$11.75",
                "fedex_express": "$18.50",
            },
        }


@dashboard_bp.route("/dashboard")
def main_dashboard():
    """Main shipping dashboard"""
    try:
        # Get all dashboard data
        overview = DashboardService.get_shipping_overview()
        platform_status = DashboardService.get_platform_status()
        inventory_dist = DashboardService.get_inventory_distribution()
        shipping_rates = DashboardService.get_shipping_rates_preview()

        return render_template(
            "dashboard/main.html",
            overview=overview,
            platform_status=platform_status,
            inventory_dist=inventory_dist,
            shipping_rates=shipping_rates,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

    except Exception as e:
        # Fallback with empty data
        return render_template(
            "dashboard/main.html",
            overview={},
            platform_status={
                "veeqo": {"connected": False},
                "easyship": {"connected": False},
            },
            inventory_dist={"top_products": [], "low_stock_products": []},
            shipping_rates={},
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            error=str(e),
        )


@dashboard_bp.route("/api/dashboard/refresh")
def api_refresh_dashboard():
    """API endpoint to refresh dashboard data"""
    try:
        overview = DashboardService.get_shipping_overview()
        platform_status = DashboardService.get_platform_status()

        return jsonify(
            {
                "success": True,
                "overview": overview,
                "platform_status": platform_status,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/platform_test")
def api_test_platforms():
    """Test API connections to both platforms"""
    try:
        veeqo_api = VeeqoAPI()
        easyship_api = EasyshipAPI()

        results = {
            "veeqo": {"status": "disconnected", "message": ""},
            "easyship": {"status": "disconnected", "message": ""},
        }

        # Test Veeqo
        try:
            warehouses = veeqo_api.get_warehouses()
            if warehouses:
                results["veeqo"] = {
                    "status": "connected",
                    "message": f"Found {len(warehouses)} warehouses",
                }
            else:
                results["veeqo"] = {
                    "status": "error",
                    "message": "No warehouses returned",
                }
        except Exception as e:
            results["veeqo"] = {"status": "error", "message": str(e)}

        # Test Easyship
        try:
            addresses = easyship_api.get_addresses()
            if addresses:
                results["easyship"] = {
                    "status": "connected",
                    "message": f"Found {len(addresses)} addresses",
                }
            else:
                results["easyship"] = {
                    "status": "error",
                    "message": "No addresses returned",
                }
        except Exception as e:
            results["easyship"] = {"status": "error", "message": str(e)}

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/inventory_alerts")
def api_inventory_alerts():
    """Get current inventory alerts"""
    try:
        # Low stock alerts
        low_stock = (
            db.session.query(
                Product.title,
                Product.sku,
                ProductInventory.quantity,
                ProductInventory.min_reorder_level,
                Warehouse.name.label("warehouse_name"),
                Warehouse.state,
            )
            .join(ProductInventory)
            .join(Warehouse)
            .filter(
                and_(
                    ProductInventory.quantity <= ProductInventory.min_reorder_level,
                    ProductInventory.quantity > 0,
                    Product.active == True,
                )
            )
            .all()
        )

        # Out of stock alerts
        out_of_stock = (
            db.session.query(
                Product.title,
                Product.sku,
                Warehouse.name.label("warehouse_name"),
                Warehouse.state,
            )
            .join(ProductInventory)
            .join(Warehouse)
            .filter(and_(ProductInventory.quantity == 0, Product.active == True))
            .all()
        )

        alerts = {
            "low_stock": [
                {
                    "title": item.title,
                    "sku": item.sku,
                    "current_qty": item.quantity,
                    "min_level": item.min_reorder_level,
                    "warehouse": item.warehouse_name,
                    "state": item.state,
                    "severity": "warning",
                }
                for item in low_stock
            ],
            "out_of_stock": [
                {
                    "title": item.title,
                    "sku": item.sku,
                    "warehouse": item.warehouse_name,
                    "state": item.state,
                    "severity": "critical",
                }
                for item in out_of_stock
            ],
        }

        return jsonify({"success": True, "alerts": alerts})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
