import shutil
import logging
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

logger = logging.getLogger("csv_import")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("csv_import.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def backup_database(db_path):
    backup_path = f"{db_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backup created at {backup_path}")
    return backup_path


def import_csv_incremental(session, model, data, unique_field):
    imported = 0
    for item in data:
        exists = (
            session.query(model)
            .filter(getattr(model, unique_field) == getattr(item, unique_field))
            .first()
        )
        if not exists:
            session.add(item)
            imported += 1
    try:
        session.commit()
        logger.info(
            f"Imported {imported} new records into {
                model.__tablename__}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Import failed: {e}")
        session.rollback()
        raise


def validate_product(product):
    assert product.sku and product.sku.startswith("DENIM-"), "Invalid SKU format"
    assert product.weight_grams > 0, "Weight must be positive"
    assert product.sales_price >= 0, "Sales price must be non-negative"
    assert product.cost_price >= 0, "Cost price must be non-negative"
    # Add more model constraints as needed


def validate_warehouse(warehouse):
    assert warehouse.external_id, "Missing external_id"
    assert warehouse.name, "Missing warehouse name"
    assert warehouse.city, "Missing city"
    assert warehouse.state in ("NV", "CA"), "Invalid state for routing"
    # Add more model constraints as needed


def initialize_inventory_levels(session, product, warehouse):
    # Example: set initial inventory to 0 if not present
    if hasattr(product, "inventory_levels"):
        if warehouse.external_id not in product.inventory_levels:
            product.inventory_levels[warehouse.external_id] = 0
            session.commit()
            logger.info(
                f"Initialized inventory for {
                    product.sku} at {
                    warehouse.external_id}"
            )


def audit_log(action, details):
    logger.info(f"AUDIT: {action} | {details}")
