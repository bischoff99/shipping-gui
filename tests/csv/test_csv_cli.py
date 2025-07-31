import tempfile
import os
import subprocess
import sys


def test_csv_cli_import_products():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(
            "sku_code,product_title,weight,sales_price,cost_price\nDENIM-JACKET-001,Classic Denim Jacket,40,59.99,30.0"
        )
        f.flush()
        temp_path = f.name
    try:
        result = subprocess.run(
            [
                sys.executable,
                "management/csv_cli.py",
                "--import-products",
                temp_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Products import complete." in result.stdout
    finally:
        os.unlink(temp_path)
