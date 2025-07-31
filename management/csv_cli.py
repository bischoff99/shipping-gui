import argparse
import sys
from services.csv_integration import CSVProcessor
from models import db
from flask import Flask
import subprocess


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    return app


def main():
    parser = argparse.ArgumentParser(description="CSV Management CLI")
    parser.add_argument("--import-products", type=str, help="Import products from CSV")
    parser.add_argument(
        "--import-warehouses", type=str, help="Import warehouses from CSV"
    )
    parser.add_argument("--export-products", type=str, help="Export products to CSV")
    parser.add_argument(
        "--export-warehouses", type=str, help="Export warehouses to CSV"
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        processor = CSVProcessor(db.session)
        if args.import_products:
            processor.process_products_csv(args.import_products)
            print("Products import complete.")
        if args.import_warehouses:
            processor.process_warehouses_csv(args.import_warehouses)
            print("Warehouses import complete.")
        # Export and other CLI features can be implemented here


if __name__ == "__main__":
    # If running as CLI, ensure .venv Python is used
    venv_python = r"c:/Users/Zubru/shipping gui/.venv/Scripts/python.exe"
    if sys.executable.lower() != venv_python.lower():
        # Re-run with .venv Python
        subprocess.run([venv_python] + sys.argv)
        sys.exit(0)

    main()
