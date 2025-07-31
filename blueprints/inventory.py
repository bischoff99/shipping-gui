"""
Manual Inventory Management Blueprint
Simple interface for adjusting stock levels across warehouses
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
)
from sqlalchemy import func, and_
from models import db, Product, Warehouse, ProductInventory
from typing import Dict, List

inventory_bp = Blueprint("inventory", __name__)


class InventoryService:
    """Service class for inventory management operations"""

    @staticmethod
    def get_inventory_summary() -> Dict:
        """Get comprehensive inventory summary"""
        # Total products and warehouses
        total_products = Product.query.filter_by(active=True).count()
        total_warehouses = Warehouse.query.count()

        # Total inventory value
        total_value = (
            db.session.query(func.sum(ProductInventory.quantity * Product.price))
            .join(Product)
            .filter(Product.active == True)
            .scalar()
            or 0
        )

        # Low stock items
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

        # Out of stock items
        out_of_stock_count = (
            ProductInventory.query.join(Product)
            .filter(and_(ProductInventory.quantity == 0, Product.active == True))
            .count()
        )

        # Inventory by region
        nevada_inventory = (
            db.session.query(func.sum(ProductInventory.quantity))
            .join(Warehouse)
            .filter(Warehouse.state.like("%Nevada%"))
            .scalar()
            or 0
        )

        california_inventory = (
            db.session.query(func.sum(ProductInventory.quantity))
            .join(Warehouse)
            .filter(Warehouse.state.like("%California%"))
            .scalar()
            or 0
        )

        return {
            "total_products": total_products,
            "total_warehouses": total_warehouses,
            "total_value": float(total_value),
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "nevada_inventory": int(nevada_inventory),
            "california_inventory": int(california_inventory),
        }

    @staticmethod
    def get_inventory_list(page: int = 1, per_page: int = 20, search: str = "") -> Dict:
        """Get paginated inventory list with search"""
        query = (
            db.session.query(Product, ProductInventory, Warehouse)
            .join(ProductInventory, ProductInventory.product_id == Product.id)
            .join(Warehouse, Warehouse.id == ProductInventory.warehouse_id)
            .filter(Product.active == True)
        )

        # Apply search filter
        if search:
            query = query.filter(
                Product.title.contains(search)
                | Product.sku.contains(search)
                | Warehouse.name.contains(search)
            )

        # Order by low stock first, then by product title
        query = query.order_by(ProductInventory.quantity.asc(), Product.title.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        inventory_items = []
        for product, inventory, warehouse in pagination.items:
            inventory_items.append(
                {
                    "product_id": product.id,
                    "inventory_id": inventory.id,
                    "sku": product.sku,
                    "title": product.title,
                    "price": float(product.price) if product.price else 0,
                    "warehouse_name": warehouse.name,
                    "warehouse_state": warehouse.state,
                    "quantity": inventory.quantity,
                    "allocated_quantity": inventory.allocated_quantity,
                    "available_quantity": inventory.available_quantity,
                    "min_reorder_level": inventory.min_reorder_level,
                    "stock_status": inventory.stock_status,
                    "needs_reorder": inventory.needs_reorder,
                }
            )

        return {
            "items": inventory_items,
            "pagination": {
                "page": pagination.page,
                "pages": pagination.pages,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        }

    @staticmethod
    def update_inventory(inventory_id: int, new_quantity: int) -> bool:
        """Update inventory quantity"""
        try:
            inventory = ProductInventory.query.get_or_404(inventory_id)
            inventory.quantity = max(0, new_quantity)  # Ensure non-negative
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating inventory: {e}")
            return False

    @staticmethod
    def bulk_update_inventory(updates: List[Dict]) -> Dict:
        """Bulk update inventory levels"""
        success_count = 0
        errors = []

        try:
            for update in updates:
                inventory_id = update.get("inventory_id")
                new_quantity = update.get("quantity")

                if not inventory_id or new_quantity is None:
                    errors.append(f"Invalid update data: {update}")
                    continue

                inventory = ProductInventory.query.get(inventory_id)
                if not inventory:
                    errors.append(f"Inventory record {inventory_id} not found")
                    continue

                inventory.quantity = max(0, int(new_quantity))
                success_count += 1

            db.session.commit()

            return {
                "success": True,
                "updated_count": success_count,
                "errors": errors,
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e), "updated_count": 0}

    @staticmethod
    def transfer_inventory(
        from_inventory_id: int, to_warehouse_id: int, quantity: int
    ) -> bool:
        """Transfer inventory between warehouses"""
        try:
            from_inventory = ProductInventory.query.get_or_404(from_inventory_id)

            # Check if enough quantity available
            if from_inventory.available_quantity < quantity:
                return False

            # Find or create target inventory record
            to_inventory = ProductInventory.query.filter_by(
                product_id=from_inventory.product_id,
                warehouse_id=to_warehouse_id,
            ).first()

            if not to_inventory:
                to_inventory = ProductInventory(
                    product_id=from_inventory.product_id,
                    warehouse_id=to_warehouse_id,
                    quantity=0,
                )
                db.session.add(to_inventory)

            # Perform transfer
            from_inventory.quantity -= quantity
            to_inventory.quantity += quantity

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Error transferring inventory: {e}")
            return False


@inventory_bp.route("/inventory")
def inventory_dashboard():
    """Main inventory management dashboard"""
    try:
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "", type=str)

        # Get inventory summary
        summary = InventoryService.get_inventory_summary()

        # Get inventory list
        inventory_data = InventoryService.get_inventory_list(
            page=page, per_page=20, search=search
        )

        return render_template(
            "inventory/dashboard.html",
            summary=summary,
            inventory_items=inventory_data["items"],
            pagination=inventory_data["pagination"],
            search=search,
        )

    except Exception as e:
        flash(f"Error loading inventory dashboard: {str(e)}", "error")
        return render_template(
            "inventory/dashboard.html",
            summary={},
            inventory_items=[],
            pagination={},
        )


@inventory_bp.route("/inventory/quick_adjust")
def quick_adjust():
    """Quick inventory adjustment interface"""
    try:
        # Get warehouses for dropdown
        warehouses = Warehouse.query.all()
        warehouse_data = [
            {"id": w.id, "name": f"{w.name} ({w.state})"} for w in warehouses
        ]

        # Get products with low stock
        low_stock_items = (
            db.session.query(Product, ProductInventory, Warehouse)
            .join(ProductInventory, ProductInventory.product_id == Product.id)
            .join(Warehouse, Warehouse.id == ProductInventory.warehouse_id)
            .filter(
                ProductInventory.quantity <= ProductInventory.min_reorder_level,
                Product.active == True,
            )
            .limit(10)
            .all()
        )

        low_stock_data = []
        for product, inventory, warehouse in low_stock_items:
            low_stock_data.append(
                {
                    "inventory_id": inventory.id,
                    "sku": product.sku,
                    "title": product.title,
                    "warehouse_name": warehouse.name,
                    "current_quantity": inventory.quantity,
                    "min_reorder_level": inventory.min_reorder_level,
                    "suggested_quantity": inventory.min_reorder_level + 10,
                }
            )

        return render_template(
            "inventory/quick_adjust.html",
            warehouses=warehouse_data,
            low_stock_items=low_stock_data,
        )

    except Exception as e:
        flash(f"Error loading quick adjust: {str(e)}", "error")
        return redirect(url_for("inventory.inventory_dashboard"))


@inventory_bp.route("/api/inventory/update", methods=["POST"])
def api_update_inventory():
    """API endpoint to update inventory"""
    try:
        data = request.get_json()
        inventory_id = data.get("inventory_id")
        new_quantity = data.get("quantity")

        if not inventory_id or new_quantity is None:
            return jsonify({"error": "Missing inventory_id or quantity"}), 400

        success = InventoryService.update_inventory(inventory_id, int(new_quantity))

        if success:
            return jsonify(
                {"success": True, "message": "Inventory updated successfully"}
            )
        else:
            return jsonify({"error": "Failed to update inventory"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/api/inventory/bulk_update", methods=["POST"])
def api_bulk_update():
    """API endpoint for bulk inventory updates"""
    try:
        data = request.get_json()
        updates = data.get("updates", [])

        if not updates:
            return jsonify({"error": "No updates provided"}), 400

        result = InventoryService.bulk_update_inventory(updates)

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "message": f"Updated {result['updated_count']} items",
                    "errors": result["errors"],
                }
            )
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/api/inventory/transfer", methods=["POST"])
def api_transfer_inventory():
    """API endpoint to transfer inventory between warehouses"""
    try:
        data = request.get_json()
        from_inventory_id = data.get("from_inventory_id")
        to_warehouse_id = data.get("to_warehouse_id")
        quantity = data.get("quantity")

        if not all([from_inventory_id, to_warehouse_id, quantity]):
            return jsonify({"error": "Missing required parameters"}), 400

        success = InventoryService.transfer_inventory(
            from_inventory_id, to_warehouse_id, int(quantity)
        )

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "Inventory transferred successfully",
                }
            )
        else:
            return jsonify({"error": "Failed to transfer inventory"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/api/inventory/search")
def api_search_inventory():
    """API endpoint to search inventory"""
    try:
        query = request.args.get("q", "")
        limit = request.args.get("limit", 10, type=int)

        if not query:
            return jsonify({"results": []})

        # Search products and their inventory
        results = (
            db.session.query(Product, ProductInventory, Warehouse)
            .join(ProductInventory, ProductInventory.product_id == Product.id)
            .join(Warehouse, Warehouse.id == ProductInventory.warehouse_id)
            .filter(
                Product.title.contains(query) | Product.sku.contains(query),
                Product.active == True,
            )
            .limit(limit)
            .all()
        )

        search_results = []
        for product, inventory, warehouse in results:
            search_results.append(
                {
                    "product_id": product.id,
                    "inventory_id": inventory.id,
                    "sku": product.sku,
                    "title": product.title,
                    "warehouse_name": warehouse.name,
                    "quantity": inventory.quantity,
                    "available_quantity": inventory.available_quantity,
                }
            )

        return jsonify({"results": search_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
