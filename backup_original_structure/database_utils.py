import json
import os
from typing import Dict, List, Any
from models import db, Product, Warehouse, ProductInventory
from datetime import datetime


def migrate_warehouses_from_json(json_file_path: str = "warehouses.json") -> int:
    """Migrate warehouses from JSON file to database"""
    if not os.path.exists(json_file_path):
        print(f"❌ Warehouses JSON file not found: {json_file_path}")
        return 0

    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)

        migrated_count = 0

        # Migrate Veeqo warehouses
        if "veeqo" in data:
            for warehouse_data in data["veeqo"]:
                existing = Warehouse.query.filter_by(
                    external_id=str(warehouse_data.get("id")), platform="veeqo"
                ).first()

                if not existing:
                    warehouse = Warehouse(
                        external_id=str(warehouse_data.get("id")),
                        name=warehouse_data.get("name", "Unknown Warehouse"),
                        address_line_1=warehouse_data.get("address_line_1", ""),
                        address_line_2=warehouse_data.get("address_line_2", ""),
                        city=warehouse_data.get("city", ""),
                        state=warehouse_data.get("region", ""),
                        postal_code=warehouse_data.get("post_code", ""),
                        country=warehouse_data.get("country", "US"),
                        phone=warehouse_data.get("phone", ""),
                        platform="veeqo",
                    )
                    db.session.add(warehouse)
                    migrated_count += 1

        # Migrate Easyship addresses as warehouses
        if "easyship" in data:
            for address_data in data["easyship"]:
                existing = Warehouse.query.filter_by(
                    external_id=address_data.get("id"), platform="easyship"
                ).first()

                if not existing:
                    warehouse = Warehouse(
                        external_id=address_data.get("id"),
                        name=address_data.get("company_name", "Unknown Warehouse"),
                        address_line_1=address_data.get("line_1", ""),
                        address_line_2=address_data.get("line_2", ""),
                        city=address_data.get("city", ""),
                        state=address_data.get("state", ""),
                        postal_code=address_data.get("postal_code", ""),
                        country=address_data.get("country_alpha2", "US"),
                        phone=address_data.get("contact_phone", ""),
                        platform="easyship",
                    )
                    db.session.add(warehouse)
                    migrated_count += 1

        db.session.commit()
        print(f"✅ Migrated {migrated_count} warehouses from JSON to database")
        return migrated_count

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating warehouses: {str(e)}")
        return 0


def migrate_products_from_json(json_file_path: str = "products.json") -> int:
    """Migrate products from JSON file to database"""
    if not os.path.exists(json_file_path):
        print(f"❌ Products JSON file not found: {json_file_path}")
        return 0

    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)

        migrated_count = 0

        # Migrate Veeqo products
        if "veeqo" in data:
            for product_data in data["veeqo"]:
                sku = product_data.get(
                    "sku_code", f"VEEQO-{product_data.get('id', 'UNKNOWN')}"
                )
                if not sku:  # Skip products without SKU
                    continue

                existing = Product.query.filter_by(sku=sku).first()

                if not existing:
                    # Extract dimensions
                    measurement_attrs = product_data.get("measurement_attributes", {})
                    dimensions_unit = measurement_attrs.get("dimensions_unit", "inches")

                    # Convert inches to cm if needed
                    length = measurement_attrs.get(
                        "width", 0
                    )  # Note: Veeqo uses width as length
                    width = measurement_attrs.get(
                        "depth", 0
                    )  # Note: Veeqo uses depth as width
                    height = measurement_attrs.get("height", 0)

                    if dimensions_unit == "inches":
                        length = length * 2.54 if length else None
                        width = width * 2.54 if width else None
                        height = height * 2.54 if height else None

                    product = Product(
                        sku=sku,
                        title=product_data.get(
                            "product_title",
                            product_data.get("title", "Unknown Product"),
                        ),
                        description=product_data.get("product", {}).get(
                            "description", ""
                        ),
                        weight_grams=product_data.get("weight_grams", 0),
                        length_cm=length,
                        width_cm=width,
                        height_cm=height,
                        price=product_data.get("price", 0),
                        cost_price=product_data.get("cost_price", 0),
                        category=product_data.get("product", {}).get(
                            "category", "Uncategorized"
                        ),
                        brand=product_data.get("brand", ""),
                        veeqo_id=str(product_data.get("id")),
                        hs_code=product_data.get("product", {}).get(
                            "hs_tariff_number", ""
                        ),
                        origin_country=product_data.get("product", {}).get(
                            "origin_country", "US"
                        ),
                        active=not product_data.get("deleted_at"),
                    )
                    db.session.add(product)
                    db.session.flush()  # Get the product ID

                    # Migrate inventory data
                    stock_entries = product_data.get("stock_entries", [])
                    for stock_entry in stock_entries:
                        warehouse_external_id = str(stock_entry.get("warehouse_id"))
                        warehouse = Warehouse.query.filter_by(
                            external_id=warehouse_external_id, platform="veeqo"
                        ).first()

                        if warehouse:
                            inventory = ProductInventory(
                                product_id=product.id,
                                warehouse_id=warehouse.id,
                                quantity=stock_entry.get("physical_stock_level", 0)
                                or 0,
                                allocated_quantity=stock_entry.get(
                                    "allocated_stock_level", 0
                                )
                                or 0,
                                incoming_quantity=stock_entry.get(
                                    "incoming_stock_level", 0
                                )
                                or 0,
                                min_reorder_level=product_data.get(
                                    "min_reorder_level", 0
                                )
                                or 0,
                                reorder_quantity=product_data.get(
                                    "quantity_to_reorder", 0
                                )
                                or 0,
                                location=stock_entry.get("location", ""),
                            )
                            db.session.add(inventory)

                    migrated_count += 1

        # Migrate Easyship products
        if "easyship" in data:
            for product_data in data["easyship"]:
                sku = product_data.get(
                    "identifier",
                    f"EASYSHIP-{
                        product_data.get(
                            'id', 'UNKNOWN')}",
                )
                if not sku:  # Skip products without SKU
                    continue

                existing = Product.query.filter_by(sku=sku).first()

                if not existing:
                    product = Product(
                        sku=sku,
                        title=product_data.get("name", "Unknown Product"),
                        description=product_data.get("comments", ""),
                        weight_grams=(
                            product_data.get("weight", 0) * 1000
                            if product_data.get("weight")
                            else 0
                        ),  # Convert kg to grams
                        length_cm=product_data.get("length", 0),
                        width_cm=product_data.get("width", 0),
                        height_cm=product_data.get("height", 0),
                        price=product_data.get("selling_price", 0),
                        cost_price=product_data.get("cost_price", 0),
                        currency=product_data.get("selling_price_currency", "USD"),
                        easyship_id=product_data.get("id"),
                        hs_code=product_data.get("hs_code", ""),
                        origin_country=product_data.get("origin_country_alpha2", "US"),
                        active=True,
                    )
                    db.session.add(product)
                    migrated_count += 1

        db.session.commit()
        print(f"✅ Migrated {migrated_count} products from JSON to database")
        return migrated_count

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating products: {str(e)}")
        return 0


def bulk_update_inventory(updates: List[Dict[str, Any]]) -> int:
    """Bulk update inventory levels"""
    updated_count = 0

    try:
        for update in updates:
            inventory = ProductInventory.get_by_product_warehouse(
                update["product_id"], update["warehouse_id"]
            )

            if inventory:
                for field, value in update.items():
                    if field not in ["product_id", "warehouse_id"] and hasattr(
                        inventory, field
                    ):
                        setattr(inventory, field, value)
                updated_count += 1

        db.session.commit()
        print(f"✅ Bulk updated {updated_count} inventory records")
        return updated_count

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in bulk inventory update: {str(e)}")
        return 0


def sync_product_with_external(
    product: Product, external_data: Dict, platform: str
) -> bool:
    """Sync product data with external platform data"""
    try:
        # Update basic product info
        if "title" in external_data or "name" in external_data:
            product.title = external_data.get(
                "title", external_data.get("name", product.title)
            )

        if "description" in external_data:
            product.description = external_data.get("description", product.description)

        if "price" in external_data:
            product.price = external_data.get("price", product.price)

        if "weight_grams" in external_data:
            product.weight_grams = external_data.get(
                "weight_grams", product.weight_grams
            )
        elif "weight" in external_data and platform == "easyship":
            # Easyship weight is in kg, convert to grams
            product.weight_grams = external_data.get("weight", 0) * 1000

        # Update external ID
        if platform == "veeqo":
            product.veeqo_id = str(external_data.get("id", product.veeqo_id))
        elif platform == "easyship":
            product.easyship_id = external_data.get("id", product.easyship_id)

        product.updated_at = datetime.utcnow()
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(
            f"❌ Error syncing product {
                product.sku} with {platform}: {
                str(e)}"
        )
        return False


def get_low_stock_report(threshold: int = None) -> List[Dict]:
    """Generate low stock report"""
    low_stock_items = ProductInventory.get_low_stock_items(threshold)

    report = []
    for item in low_stock_items:
        report.append(
            {
                "product_sku": item.product.sku,
                "product_title": item.product.title,
                "warehouse_name": item.warehouse.name,
                "current_quantity": item.quantity,
                "allocated_quantity": item.allocated_quantity,
                "available_quantity": item.available_quantity,
                "min_reorder_level": item.min_reorder_level,
                "reorder_quantity": item.reorder_quantity,
                "stock_status": item.stock_status,
            }
        )

    return report


def export_products_to_json(file_path: str = "products_export.json") -> bool:
    """Export products from database to JSON file"""
    try:
        products = Product.query.all()
        export_data = []

        for product in products:
            product_dict = product.to_dict(include_inventory=True)

            # Add warehouse details for inventory
            inventory_details = []
            for inv_item in product.inventory_items:
                inventory_details.append(
                    {
                        "warehouse_id": inv_item.warehouse_id,
                        "warehouse_name": inv_item.warehouse.name,
                        "quantity": inv_item.quantity,
                        "allocated_quantity": inv_item.allocated_quantity,
                        "available_quantity": inv_item.available_quantity,
                        "location": inv_item.location,
                        "stock_status": inv_item.stock_status,
                    }
                )

            product_dict["inventory_details"] = inventory_details
            export_data.append(product_dict)

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"✅ Exported {len(products)} products to {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error exporting products: {str(e)}")
        return False
