# CSV data processing script for denim products
import csv
import os


def process_csv(file_path):
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        products = [row for row in reader]
    print(f"Loaded {len(products)} products from {file_path}")
    return products


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    csv_file = os.path.join(data_dir, "products.csv")
    if os.path.exists(csv_file):
        process_csv(csv_file)
    else:
        print(f"CSV file not found: {csv_file}")
