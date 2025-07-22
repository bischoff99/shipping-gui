"""
Real-time Inventory Monitoring System
Advanced inventory tracking with alerts and automated reordering
"""
import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class InventoryAlert:
    id: str
    product_sku: str
    product_name: str
    warehouse_id: str
    warehouse_name: str
    current_stock: int
    threshold: int
    alert_type: str  # 'low_stock', 'out_of_stock', 'overstock'
    severity: str  # 'low', 'medium', 'high', 'critical'
    created_at: str
    resolved: bool = False
    
@dataclass
class InventoryMovement:
    id: str
    product_sku: str
    warehouse_id: str
    movement_type: str  # 'in', 'out', 'adjustment'
    quantity: int
    reference: str  # order_id, shipment_id, adjustment_id
    timestamp: str
    notes: str = ""

class RealTimeInventoryMonitor:
    def __init__(self, veeqo_api, easyship_api):
        self.veeqo_api = veeqo_api
        self.easyship_api = easyship_api
        self.alerts = []
        self.movements = []
        self.thresholds = {}  # sku: threshold
        self.monitoring_active = False
        self.logger = self._setup_logger()
        
        # Default thresholds
        self.default_low_stock = 10
        self.default_critical_stock = 0
        self.default_overstock_multiplier = 10
        
    def _setup_logger(self):
        logger = logging.getLogger('InventoryMonitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('inventory_monitor.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def start_monitoring(self, check_interval: int = 60):
        """Start real-time inventory monitoring"""
        self.monitoring_active = True
        
        def monitor_worker():
            while self.monitoring_active:
                try:
                    self._check_inventory_levels()
                    time.sleep(check_interval)
                except Exception as e:
                    self.logger.error(f"Monitoring error: {str(e)}")
                    time.sleep(check_interval)
        
        thread = threading.Thread(target=monitor_worker, daemon=True)
        thread.start()
        self.logger.info(f"Inventory monitoring started with {check_interval}s interval")
    
    def stop_monitoring(self):
        """Stop real-time inventory monitoring"""
        self.monitoring_active = False
        self.logger.info("Inventory monitoring stopped")
    
    def _check_inventory_levels(self):
        """Check current inventory levels against thresholds"""
        try:
            # Get current inventory from Veeqo
            warehouses = self.veeqo_api.get_warehouses()
            products = self.veeqo_api.get_products()
            
            for product in products:
                sku = product.get('sku', '')
                if not sku:
                    continue
                
                product_name = product.get('title', 'Unknown Product')
                sellables = product.get('sellables', [])
                
                for sellable in sellables:
                    stock_entries = sellable.get('stock_entries', [])
                    
                    for entry in stock_entries:
                        warehouse_id = str(entry.get('warehouse_id', ''))
                        available = int(entry.get('available', 0))
                        allocated = int(entry.get('allocated', 0))
                        
                        # Find warehouse name
                        warehouse_name = 'Unknown Warehouse'
                        for warehouse in warehouses:
                            if str(warehouse.get('id')) == warehouse_id:
                                warehouse_name = warehouse.get('name', 'Unknown Warehouse')
                                break
                        
                        # Check thresholds
                        threshold = self.thresholds.get(sku, self.default_low_stock)
                        
                        # Generate alerts
                        if available == 0:
                            self._create_alert(sku, product_name, warehouse_id, warehouse_name, 
                                            available, 0, 'out_of_stock', 'critical')
                        elif available <= threshold:
                            severity = 'high' if available <= threshold * 0.5 else 'medium'
                            self._create_alert(sku, product_name, warehouse_id, warehouse_name,
                                            available, threshold, 'low_stock', severity)
                        elif available > threshold * self.default_overstock_multiplier:
                            self._create_alert(sku, product_name, warehouse_id, warehouse_name,
                                            available, threshold * self.default_overstock_multiplier,
                                            'overstock', 'low')
            
        except Exception as e:
            self.logger.error(f"Error checking inventory levels: {str(e)}")
    
    def _create_alert(self, sku: str, product_name: str, warehouse_id: str, 
                     warehouse_name: str, current_stock: int, threshold: int,
                     alert_type: str, severity: str):
        """Create inventory alert if not already exists"""
        alert_id = f"{sku}_{warehouse_id}_{alert_type}"
        
        # Check if alert already exists
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                return  # Alert already exists
        
        alert = InventoryAlert(
            id=alert_id,
            product_sku=sku,
            product_name=product_name,
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name,
            current_stock=current_stock,
            threshold=threshold,
            alert_type=alert_type,
            severity=severity,
            created_at=datetime.now().isoformat()
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"New {severity} alert: {alert_type} for {sku} at {warehouse_name}")
    
    def get_active_alerts(self, severity_filter: str = None) -> List[InventoryAlert]:
        """Get active inventory alerts"""
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        if severity_filter:
            active_alerts = [alert for alert in active_alerts if alert.severity == severity_filter]
        
        return sorted(active_alerts, key=lambda x: x.created_at, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.logger.info(f"Alert {alert_id} resolved")
                return True
        return False
    
    def set_product_threshold(self, sku: str, threshold: int):
        """Set custom stock threshold for product"""
        self.thresholds[sku] = threshold
        self.logger.info(f"Threshold for {sku} set to {threshold}")
    
    def record_movement(self, product_sku: str, warehouse_id: str, movement_type: str,
                       quantity: int, reference: str, notes: str = ""):
        """Record inventory movement"""
        movement = InventoryMovement(
            id=f"{product_sku}_{warehouse_id}_{int(time.time())}",
            product_sku=product_sku,
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            quantity=quantity,
            reference=reference,
            timestamp=datetime.now().isoformat(),
            notes=notes
        )
        
        self.movements.append(movement)
        self.logger.info(f"Movement recorded: {movement_type} {quantity} units of {product_sku}")
    
    def get_movements(self, product_sku: str = None, warehouse_id: str = None, 
                     hours: int = 24) -> List[InventoryMovement]:
        """Get recent inventory movements"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_movements = []
        
        for movement in self.movements:
            movement_time = datetime.fromisoformat(movement.timestamp)
            if movement_time >= cutoff_time:
                if product_sku and movement.product_sku != product_sku:
                    continue
                if warehouse_id and movement.warehouse_id != warehouse_id:
                    continue
                recent_movements.append(movement)
        
        return sorted(recent_movements, key=lambda x: x.timestamp, reverse=True)
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get comprehensive inventory summary"""
        try:
            products = self.veeqo_api.get_products()
            warehouses = self.veeqo_api.get_warehouses()
            
            total_products = len(products)
            total_value = 0
            out_of_stock = 0
            low_stock = 0
            
            warehouse_totals = {}
            
            for product in products:
                price = float(product.get('selling_price', 0))
                sellables = product.get('sellables', [])
                
                product_total_stock = 0
                for sellable in sellables:
                    stock_entries = sellable.get('stock_entries', [])
                    for entry in stock_entries:
                        available = int(entry.get('available', 0))
                        warehouse_id = str(entry.get('warehouse_id', ''))
                        
                        product_total_stock += available
                        total_value += available * price
                        
                        # Warehouse totals
                        if warehouse_id not in warehouse_totals:
                            warehouse_totals[warehouse_id] = {'products': 0, 'total_stock': 0}
                        warehouse_totals[warehouse_id]['products'] += 1
                        warehouse_totals[warehouse_id]['total_stock'] += available
                
                # Check stock levels
                if product_total_stock == 0:
                    out_of_stock += 1
                elif product_total_stock <= self.thresholds.get(product.get('sku', ''), self.default_low_stock):
                    low_stock += 1
            
            return {
                'total_products': total_products,
                'total_inventory_value': total_value,
                'out_of_stock_products': out_of_stock,
                'low_stock_products': low_stock,
                'warehouse_breakdown': warehouse_totals,
                'active_alerts': len(self.get_active_alerts()),
                'critical_alerts': len(self.get_active_alerts('critical')),
                'recent_movements': len(self.get_movements())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting inventory summary: {str(e)}")
            return {}
    
    def generate_reorder_suggestions(self) -> List[Dict[str, Any]]:
        """Generate automatic reorder suggestions"""
        suggestions = []
        
        try:
            products = self.veeqo_api.get_products()
            
            for product in products:
                sku = product.get('sku', '')
                if not sku:
                    continue
                
                name = product.get('title', 'Unknown Product')
                sellables = product.get('sellables', [])
                
                total_stock = 0
                for sellable in sellables:
                    stock_entries = sellable.get('stock_entries', [])
                    for entry in stock_entries:
                        total_stock += int(entry.get('available', 0))
                
                threshold = self.thresholds.get(sku, self.default_low_stock)
                
                if total_stock <= threshold:
                    # Calculate suggested reorder quantity
                    # Simple logic: order enough for 30 days based on average daily usage
                    suggested_quantity = max(threshold * 2, 50)  # At least double threshold or 50 units
                    
                    suggestions.append({
                        'sku': sku,
                        'product_name': name,
                        'current_stock': total_stock,
                        'threshold': threshold,
                        'suggested_quantity': suggested_quantity,
                        'priority': 'high' if total_stock == 0 else 'medium',
                        'estimated_cost': float(product.get('cost_price', 0)) * suggested_quantity
                    })
            
            return sorted(suggestions, key=lambda x: x['current_stock'])
            
        except Exception as e:
            self.logger.error(f"Error generating reorder suggestions: {str(e)}")
            return []
    
    def export_inventory_report(self, format: str = 'json') -> str:
        """Export comprehensive inventory report"""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_inventory_summary(),
                'active_alerts': [asdict(alert) for alert in self.get_active_alerts()],
                'recent_movements': [asdict(movement) for movement in self.get_movements()],
                'reorder_suggestions': self.generate_reorder_suggestions(),
                'thresholds': self.thresholds
            }
            
            if format == 'json':
                return json.dumps(report_data, indent=2, default=str)
            
            # Could add CSV, Excel exports here
            return json.dumps(report_data, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Error exporting inventory report: {str(e)}")
            return "{}"
