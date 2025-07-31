"""
Advanced Product Synchronization System
Real-time sync between Veeqo and Easyship with inventory management
"""

import os
import json
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import logging


@dataclass
class Product:
    id: str
    name: str
    sku: str
    price: float
    weight: float
    dimensions: Dict[str, float]  # length, width, height
    description: str
    category: str
    brand: str
    inventory: Dict[str, int]  # warehouse_id: quantity
    last_synced: str
    sync_status: str  # 'synced', 'pending', 'error'
    platform: str  # 'veeqo', 'easyship', 'both'
    images: List[str]
    variants: List[Dict]


@dataclass
class SyncStats:
    total_products: int = 0
    synced_products: int = 0
    pending_products: int = 0
    error_products: int = 0
    last_sync_time: str = ""
    sync_duration: float = 0.0
    veeqo_products: int = 0
    easyship_products: int = 0


class AdvancedProductSync:
    def __init__(self, veeqo_api, easyship_api):
        self.veeqo_api = veeqo_api
        self.easyship_api = easyship_api
        self.products_cache = {}
        self.sync_stats = SyncStats()
        self.sync_running = False
        self.auto_sync_enabled = False
        self.sync_interval = 300  # 5 minutes
        self.logger = self._setup_logger()

        # Create products data directory
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _setup_logger(self):
        """Setup logging for sync operations"""
        logger = logging.getLogger("ProductSync")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler("product_sync.log")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def get_all_products(self) -> List[Product]:
        """Get all products from both platforms"""
        self.logger.info("Fetching products from all platforms...")

        # Fetch from both platforms concurrently
        veeqo_products = await self._fetch_veeqo_products()
        easyship_products = await self._fetch_easyship_products()

        # Merge and deduplicate products
        all_products = self._merge_products(veeqo_products, easyship_products)

        self.sync_stats.total_products = len(all_products)
        self.sync_stats.veeqo_products = len(veeqo_products)
        self.sync_stats.easyship_products = len(easyship_products)

        return all_products

    async def _fetch_veeqo_products(self) -> List[Product]:
        """Fetch products from Veeqo"""
        try:
            raw_products = self.veeqo_api.get_products()
            products = []

            for raw_product in raw_products:
                product = Product(
                    id=str(raw_product.get("id", "")),
                    name=raw_product.get("title", "Unknown Product"),
                    sku=raw_product.get("sku", ""),
                    price=float(raw_product.get("selling_price", 0)),
                    weight=float(raw_product.get("weight", 0)),
                    dimensions=self._extract_dimensions(raw_product),
                    description=raw_product.get("description", ""),
                    category=raw_product.get("product_category", "Uncategorized"),
                    brand=raw_product.get("brand", ""),
                    inventory=self._extract_inventory(raw_product),
                    last_synced=datetime.now().isoformat(),
                    sync_status="synced",
                    platform="veeqo",
                    images=raw_product.get("images", []),
                    variants=raw_product.get("sellables", []),
                )
                products.append(product)

            self.logger.info(f"Fetched {len(products)} products from Veeqo")
            return products

        except Exception as e:
            self.logger.error(f"Error fetching Veeqo products: {str(e)}")
            return []

    async def _fetch_easyship_products(self) -> List[Product]:
        """Fetch products from Easyship"""
        try:
            # Easyship doesn't have a direct product catalog
            # We'll simulate or get from shipments
            products = []
            self.logger.info("Fetched 0 products from Easyship (no direct product API)")
            return products

        except Exception as e:
            self.logger.error(f"Error fetching Easyship products: {str(e)}")
            return []

    def _extract_dimensions(self, raw_product: Dict) -> Dict[str, float]:
        """Extract product dimensions"""
        return {
            "length": float(raw_product.get("dimensions", {}).get("length", 0)),
            "width": float(raw_product.get("dimensions", {}).get("width", 0)),
            "height": float(raw_product.get("dimensions", {}).get("height", 0)),
        }

    def _extract_inventory(self, raw_product: Dict) -> Dict[str, int]:
        """Extract inventory levels by warehouse"""
        inventory = {}
        sellables = raw_product.get("sellables", [])

        for sellable in sellables:
            stock_entries = sellable.get("stock_entries", [])
            for entry in stock_entries:
                warehouse_id = str(entry.get("warehouse_id", "unknown"))
                available = int(entry.get("available", 0))
                inventory[warehouse_id] = inventory.get(warehouse_id, 0) + available

        return inventory

    def _merge_products(
        self, veeqo_products: List[Product], easyship_products: List[Product]
    ) -> List[Product]:
        """Merge products from different platforms"""
        merged = {}

        # Add Veeqo products
        for product in veeqo_products:
            merged[product.sku] = product

        # Add Easyship products
        for product in easyship_products:
            if product.sku in merged:
                # Merge information
                merged[product.sku].platform = "both"
            else:
                merged[product.sku] = product

        return list(merged.values())

    async def sync_products_bidirectional(self) -> Dict[str, Any]:
        """Perform bidirectional product sync"""
        if self.sync_running:
            return {"status": "error", "message": "Sync already running"}

        self.sync_running = True
        start_time = time.time()

        try:
            self.logger.info("Starting bidirectional product sync...")

            # Get all products
            all_products = await self.get_all_products()

            # Sync to Veeqo
            veeqo_results = await self._sync_to_veeqo(all_products)

            # Sync to Easyship
            easyship_results = await self._sync_to_easyship(all_products)

            # Update cache
            self.products_cache = {p.sku: p for p in all_products}

            # Save to file
            await self._save_products_to_file(all_products)

            # Update stats
            self.sync_stats.last_sync_time = datetime.now().isoformat()
            self.sync_stats.sync_duration = time.time() - start_time
            self.sync_stats.synced_products = len(
                [p for p in all_products if p.sync_status == "synced"]
            )
            self.sync_stats.pending_products = len(
                [p for p in all_products if p.sync_status == "pending"]
            )
            self.sync_stats.error_products = len(
                [p for p in all_products if p.sync_status == "error"]
            )

            self.logger.info(
                f"Sync completed in {
                    self.sync_stats.sync_duration:.2f} seconds"
            )

            return {
                "status": "success",
                "stats": asdict(self.sync_stats),
                "veeqo_results": veeqo_results,
                "easyship_results": easyship_results,
            }

        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            return {"status": "error", "message": str(e)}

        finally:
            self.sync_running = False

    async def _sync_to_veeqo(self, products: List[Product]) -> Dict:
        """Sync products to Veeqo"""
        results = {"created": 0, "updated": 0, "errors": 0}

        for product in products:
            try:
                # Check if product exists in Veeqo
                existing = self.veeqo_api.get_product_by_sku(product.sku)

                if existing:
                    # Update existing product
                    self.veeqo_api.update_product(
                        existing["id"], self._product_to_veeqo_format(product)
                    )
                    results["updated"] += 1
                else:
                    # Create new product
                    self.veeqo_api.create_product(
                        self._product_to_veeqo_format(product)
                    )
                    results["created"] += 1

                product.sync_status = "synced"

            except Exception as e:
                self.logger.error(
                    f"Error syncing product {product.sku} to Veeqo: {str(e)}"
                )
                product.sync_status = "error"
                results["errors"] += 1

        return results

    async def _sync_to_easyship(self, products: List[Product]) -> Dict:
        """Sync products to Easyship"""
        results = {"created": 0, "updated": 0, "errors": 0}

        # Easyship doesn't have a direct product catalog
        # Products are created during shipment creation

        return results

    def _product_to_veeqo_format(self, product: Product) -> Dict:
        """Convert Product to Veeqo API format"""
        return {
            "title": product.name,
            "sku": product.sku,
            "selling_price": product.price,
            "weight": product.weight,
            "description": product.description,
            "product_category": product.category,
            "brand": product.brand,
            "dimensions": product.dimensions,
        }

    async def _save_products_to_file(self, products: List[Product]):
        """Save products to JSON file for persistence"""
        try:
            products_data = [asdict(p) for p in products]
            with open(os.path.join(self.data_dir, "products.json"), "w") as f:
                json.dump(products_data, f, indent=2, default=str)

            self.logger.info(f"Saved {len(products)} products to file")

        except Exception as e:
            self.logger.error(f"Error saving products to file: {str(e)}")

    async def load_products_from_file(self) -> List[Product]:
        """Load products from JSON file"""
        try:
            file_path = os.path.join(self.data_dir, "products.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    products_data = json.load(f)

                products = []
                for data in products_data:
                    product = Product(**data)
                    products.append(product)

                self.logger.info(f"Loaded {len(products)} products from file")
                return products

        except Exception as e:
            self.logger.error(f"Error loading products from file: {str(e)}")

        return []

    def start_auto_sync(self, interval_minutes: int = 5):
        """Start automatic sync in background"""
        self.auto_sync_enabled = True
        self.sync_interval = interval_minutes * 60

        def auto_sync_worker():
            while self.auto_sync_enabled:
                if not self.sync_running:
                    try:
                        asyncio.run(self.sync_products_bidirectional())
                    except Exception as e:
                        self.logger.error(f"Auto-sync error: {str(e)}")

                time.sleep(self.sync_interval)

        thread = threading.Thread(target=auto_sync_worker, daemon=True)
        thread.start()

        self.logger.info(f"Auto-sync started with {interval_minutes} minute interval")

    def stop_auto_sync(self):
        """Stop automatic sync"""
        self.auto_sync_enabled = False
        self.logger.info("Auto-sync stopped")

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get current sync statistics"""
        return asdict(self.sync_stats)

    def get_inventory_alerts(self, low_stock_threshold: int = 10) -> List[Dict]:
        """Get products with low inventory"""
        alerts = []

        for product in self.products_cache.values():
            total_inventory = sum(product.inventory.values())
            if total_inventory <= low_stock_threshold:
                alerts.append(
                    {
                        "sku": product.sku,
                        "name": product.name,
                        "total_inventory": total_inventory,
                        "warehouse_breakdown": product.inventory,
                        "severity": "critical" if total_inventory == 0 else "warning",
                    }
                )

        return sorted(alerts, key=lambda x: x["total_inventory"])

    def get_product_performance(self) -> Dict[str, Any]:
        """Get product performance analytics"""
        if not self.products_cache:
            return {}

        total_value = sum(
            p.price * sum(p.inventory.values()) for p in self.products_cache.values()
        )
        avg_price = sum(p.price for p in self.products_cache.values()) / len(
            self.products_cache
        )

        return {
            "total_products": len(self.products_cache),
            "total_inventory_value": total_value,
            "average_product_price": avg_price,
            "categories": self._get_category_breakdown(),
            "top_products_by_value": self._get_top_products_by_value(),
            "low_stock_count": len(self.get_inventory_alerts()),
        }

    def _get_category_breakdown(self) -> Dict[str, int]:
        """Get product count by category"""
        categories = {}
        for product in self.products_cache.values():
            category = product.category or "Uncategorized"
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _get_top_products_by_value(self, limit: int = 10) -> List[Dict]:
        """Get top products by inventory value"""
        products_with_value = []

        for product in self.products_cache.values():
            total_qty = sum(product.inventory.values())
            total_value = product.price * total_qty

            products_with_value.append(
                {
                    "sku": product.sku,
                    "name": product.name,
                    "price": product.price,
                    "quantity": total_qty,
                    "total_value": total_value,
                }
            )

        return sorted(
            products_with_value, key=lambda x: x["total_value"], reverse=True
        )[:limit]
