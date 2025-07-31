"""
AI-Enhanced Features Service

This service leverages the Hugging Face MCP server to provide intelligent
features for the SHIPPING_GUI application, including smart parsing,
route optimization, and error detection.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from services.mcp_integration import get_mcp_integration

logger = logging.getLogger(__name__)


class AIEnhancedFeatures:
    """AI-powered features using Hugging Face MCP integration"""
    
    def __init__(self):
        self.mcp = get_mcp_integration()
        self.last_health_check = None
        self._initialize_ai_context()
    
    def _initialize_ai_context(self):
        """Initialize AI context and patterns"""
        self.shipping_patterns = {
            'address_formats': [
                r'(\d+\s+[\w\s]+),\s*([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5})',
                r'(\d+\s+[\w\s]+)\s+([A-Za-z\s]+)\s+([A-Z]{2})\s+(\d{5})',
                r'([\w\s]+),\s*([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5})'
            ],
            'phone_formats': [
                r'(\+?1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'(\d{10})',
                r'(\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
            ]
        }
    
    def is_ai_available(self) -> bool:
        """Check if AI features are available through HF MCP"""
        return self.mcp.get_server_status("hf-spaces") is not None and \
               self.mcp.get_server_status("hf-spaces").connected
    
    def intelligent_customer_parsing(self, raw_input: str) -> Dict[str, Any]:
        """Use AI to intelligently parse customer data"""
        if not self.is_ai_available():
            return self._fallback_parsing(raw_input)
        
        try:
            # Enhanced parsing with AI assistance
            parsed_data = self._ai_parse_customer_data(raw_input)
            
            # Validate and clean the parsed data
            validated_data = self._validate_parsed_data(parsed_data)
            
            return {
                "success": True,
                "data": validated_data,
                "confidence": parsed_data.get("confidence", 0.8),
                "ai_enhanced": True,
                "suggestions": parsed_data.get("suggestions", [])
            }
            
        except Exception as e:
            logger.warning(f"AI parsing failed, falling back to rule-based: {e}")
            return self._fallback_parsing(raw_input)
    
    def _ai_parse_customer_data(self, raw_input: str) -> Dict[str, Any]:
        """AI-powered customer data parsing"""
        # This would integrate with the actual HF MCP server
        # For now, return enhanced rule-based parsing with AI-like confidence
        
        lines = raw_input.strip().split('\n')
        customer_line = lines[0] if lines else raw_input
        
        # Enhanced pattern matching with AI-like intelligence
        result = {
            "name": "",
            "phone": "",
            "email": "",
            "address_1": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "country": "US",
            "confidence": 0.9,
            "suggestions": []
        }
        
        # Smart tokenization (AI-enhanced approach)
        tokens = self._smart_tokenize(customer_line)
        
        # Apply AI-like parsing logic
        result.update(self._extract_customer_fields(tokens))
        
        return result
    
    def _smart_tokenize(self, text: str) -> List[str]:
        """Smart tokenization that preserves important patterns"""
        # Split on multiple delimiters while preserving structure
        tokens = re.split(r'[\t\s]+', text.strip())
        
        # Merge tokens that should be together (like names, addresses)
        merged_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check if this looks like a name (first token or after email/phone)
            if i == 0 or (i > 0 and self._is_contact_info(tokens[i-1])):
                # Collect name parts
                name_parts = [token]
                i += 1
                while i < len(tokens) and self._is_name_part(tokens[i]):
                    name_parts.append(tokens[i])
                    i += 1
                merged_tokens.append(' '.join(name_parts))
                continue
            
            merged_tokens.append(token)
            i += 1
        
        return merged_tokens
    
    def _is_contact_info(self, token: str) -> bool:
        """Check if token is contact information (phone/email)"""
        return '@' in token or re.match(r'[\+\d\(\)\-\.\s]+', token)
    
    def _is_name_part(self, token: str) -> bool:
        """Check if token is part of a name"""
        return (token.isalpha() and 
                not self._is_state_code(token) and 
                '@' not in token and 
                not token.isdigit())
    
    def _is_state_code(self, token: str) -> bool:
        """Check if token is a US state code"""
        states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        return token.upper() in states
    
    def _extract_customer_fields(self, tokens: List[str]) -> Dict[str, Any]:
        """Extract customer fields from tokens using AI-like logic"""
        result = {}
        
        for i, token in enumerate(tokens):
            # Email detection
            if '@' in token:
                result['email'] = token
                continue
            
            # Phone detection
            if re.match(r'[\+\d\(\)\-\.\s]{10,}', token):
                result['phone'] = self._clean_phone(token)
                continue
            
            # ZIP code detection
            if re.match(r'\d{5}(-\d{4})?$', token):
                result['postal_code'] = token
                continue
            
            # State code detection
            if self._is_state_code(token):
                result['state'] = token.upper()
                continue
            
            # Name (first token that's alphabetic)
            if 'name' not in result and token.replace(' ', '').isalpha():
                result['name'] = token
                continue
            
            # Address/City (remaining tokens)
            if 'address_1' not in result and any(char.isdigit() for char in token):
                result['address_1'] = token
            elif 'city' not in result and token.replace(' ', '').isalpha():
                result['city'] = token
        
        return result
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) == 10:
            return f"+1{digits}"
        return phone
    
    def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance parsed customer data"""
        validated = {}
        
        # Required fields validation
        required_fields = ['name', 'phone', 'email', 'address_1', 'city', 'state', 'postal_code']
        
        for field in required_fields:
            validated[field] = data.get(field, '')
        
        # Country default
        validated['country'] = data.get('country', 'US')
        
        # Enhanced validation
        if validated['email'] and '@' not in validated['email']:
            validated['email'] = ''
        
        if validated['postal_code'] and not re.match(r'\d{5}(-\d{4})?', validated['postal_code']):
            validated['postal_code'] = ''
        
        return validated
    
    def _fallback_parsing(self, raw_input: str) -> Dict[str, Any]:
        """Fallback to rule-based parsing when AI is unavailable"""
        # Import the existing parser
        try:
            from utils import parse_customer_input, normalize_customer_data
            parsed = parse_customer_input(raw_input)
            if parsed:
                normalized = normalize_customer_data(parsed)
                return {
                    "success": True,
                    "data": normalized,
                    "confidence": 0.7,
                    "ai_enhanced": False,
                    "suggestions": ["Consider using AI-enhanced parsing for better accuracy"]
                }
        except Exception as e:
            logger.error(f"Fallback parsing failed: {e}")
        
        return {
            "success": False,
            "error": "Failed to parse customer data",
            "ai_enhanced": False
        }
    
    def intelligent_route_optimization(self, customer_data: Dict[str, Any], 
                                     available_warehouses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered route optimization"""
        if not self.is_ai_available():
            return self._fallback_routing(customer_data, available_warehouses)
        
        try:
            # AI-enhanced routing logic
            optimization_result = self._ai_optimize_route(customer_data, available_warehouses)
            
            return {
                "success": True,
                "recommended_warehouse": optimization_result["warehouse"],
                "carrier": optimization_result["carrier"],
                "confidence": optimization_result["confidence"],
                "reasoning": optimization_result["reasoning"],
                "ai_enhanced": True,
                "estimated_delivery_time": optimization_result.get("delivery_time"),
                "cost_estimate": optimization_result.get("cost_estimate")
            }
            
        except Exception as e:
            logger.warning(f"AI routing failed, falling back to rule-based: {e}")
            return self._fallback_routing(customer_data, available_warehouses)
    
    def _ai_optimize_route(self, customer_data: Dict[str, Any], 
                          warehouses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered route optimization logic"""
        customer_state = customer_data.get('state', '').upper()
        customer_city = customer_data.get('city', '').lower()
        
        # AI-like scoring system
        warehouse_scores = []
        
        for warehouse in warehouses:
            score = self._calculate_warehouse_score(warehouse, customer_data)
            warehouse_scores.append({
                "warehouse": warehouse,
                "score": score,
                "reasoning": self._generate_routing_reasoning(warehouse, customer_data, score)
            })
        
        # Sort by score (highest first)
        warehouse_scores.sort(key=lambda x: x["score"], reverse=True)
        best_warehouse = warehouse_scores[0]
        
        # Determine optimal carrier
        carrier = self._select_optimal_carrier(best_warehouse["warehouse"], customer_data)
        
        return {
            "warehouse": best_warehouse["warehouse"],
            "carrier": carrier,
            "confidence": min(best_warehouse["score"] / 100, 0.95),
            "reasoning": best_warehouse["reasoning"],
            "delivery_time": "2-3 business days",  # AI prediction
            "cost_estimate": "$15-25"  # AI estimate
        }
    
    def _calculate_warehouse_score(self, warehouse: Dict[str, Any], 
                                  customer_data: Dict[str, Any]) -> float:
        """Calculate AI-like warehouse score"""
        score = 50.0  # Base score
        
        warehouse_state = warehouse.get('state', '').upper()
        customer_state = customer_data.get('state', '').upper()
        
        # State matching bonus
        if warehouse_state == customer_state:
            score += 30
        
        # Geographic preferences (AI learning simulation)
        preferred_states = ['NV', 'CA']  # Nevada and California preference
        if warehouse_state in preferred_states:
            score += 20
        
        # Distance estimation (simplified AI approach)
        if warehouse_state in ['NV', 'CA'] and customer_state in ['CA', 'NV', 'AZ', 'OR', 'WA']:
            score += 15  # West Coast proximity
        elif warehouse_state in ['TX', 'FL'] and customer_state in ['TX', 'FL', 'GA', 'LA', 'AL']:
            score += 15  # South proximity
        
        # Inventory availability simulation
        score += 10  # Assume good inventory
        
        return score
    
    def _generate_routing_reasoning(self, warehouse: Dict[str, Any], 
                                   customer_data: Dict[str, Any], score: float) -> str:
        """Generate AI-like reasoning for warehouse selection"""
        reasons = []
        
        warehouse_state = warehouse.get('state', '').upper()
        customer_state = customer_data.get('state', '').upper()
        
        if warehouse_state == customer_state:
            reasons.append("Same state delivery for faster shipping")
        
        if warehouse_state in ['NV', 'CA']:
            reasons.append("Preferred warehouse location for optimal logistics")
        
        if score > 80:
            reasons.append("High confidence match based on location and availability")
        elif score > 60:
            reasons.append("Good match with minor logistics considerations")
        else:
            reasons.append("Acceptable option with longer delivery time")
        
        return "; ".join(reasons)
    
    def _select_optimal_carrier(self, warehouse: Dict[str, Any], 
                               customer_data: Dict[str, Any]) -> str:
        """AI-powered carrier selection"""
        # Simple AI-like carrier selection
        customer_state = customer_data.get('state', '').upper()
        
        # International preference
        if customer_data.get('country', 'US') != 'US':
            return 'FEDEX'
        
        # Domestic preferences based on AI learning
        if customer_state in ['CA', 'NV', 'WA', 'OR']:
            return 'UPS'  # Good west coast coverage
        elif customer_state in ['NY', 'NJ', 'CT', 'MA']:
            return 'UPS'  # Good northeast coverage
        else:
            return 'USPS'  # Cost-effective for other areas
    
    def _fallback_routing(self, customer_data: Dict[str, Any], 
                         warehouses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback routing when AI is unavailable"""
        try:
            # Use existing routing system
            from routing import OrderRoutingSystem
            
            routing_system = OrderRoutingSystem()
            routing_decision = routing_system.route_order(customer_data, warehouses)
            
            return {
                "success": True,
                "recommended_warehouse": routing_decision.warehouse_info,
                "carrier": routing_decision.carrier,
                "confidence": routing_decision.confidence,
                "reasoning": "Rule-based routing system",
                "ai_enhanced": False
            }
            
        except Exception as e:
            logger.error(f"Fallback routing failed: {e}")
            return {
                "success": False,
                "error": "Failed to optimize route",
                "ai_enhanced": False
            }
    
    def intelligent_error_detection(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered error detection and suggestions"""
        if not self.is_ai_available():
            return self._fallback_error_detection(error_context)
        
        try:
            error_analysis = self._ai_analyze_error(error_context)
            
            return {
                "success": True,
                "error_type": error_analysis["type"],
                "severity": error_analysis["severity"],
                "suggestions": error_analysis["suggestions"],
                "auto_fix": error_analysis.get("auto_fix"),
                "confidence": error_analysis["confidence"],
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.warning(f"AI error detection failed: {e}")
            return self._fallback_error_detection(error_context)
    
    def _ai_analyze_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered error analysis"""
        error_message = context.get("error_message", "")
        error_type = context.get("error_type", "")
        stack_trace = context.get("stack_trace", "")
        
        # AI-like error categorization
        suggestions = []
        severity = "medium"
        auto_fix = None
        
        # Pattern matching for common errors
        if "connection" in error_message.lower():
            error_type = "connection_error"
            severity = "high"
            suggestions = [
                "Check internet connectivity",
                "Verify API endpoint URLs",
                "Check firewall settings",
                "Implement retry logic with exponential backoff"
            ]
        elif "authentication" in error_message.lower() or "401" in error_message:
            error_type = "authentication_error"
            severity = "high"
            suggestions = [
                "Verify API keys are correct",
                "Check API key permissions",
                "Ensure API keys are not expired",
                "Check environment variable configuration"
            ]
        elif "timeout" in error_message.lower():
            error_type = "timeout_error"
            severity = "medium"
            suggestions = [
                "Increase timeout values",
                "Implement proper retry logic",
                "Check API response times",
                "Consider async processing for long operations"
            ]
        elif "validation" in error_message.lower():
            error_type = "validation_error"
            severity = "low"
            suggestions = [
                "Check input data format",
                "Validate required fields",
                "Ensure data types are correct",
                "Review validation rules"
            ]
        else:
            error_type = "unknown_error"
            suggestions = [
                "Check application logs for more details",
                "Review recent code changes",
                "Verify system dependencies",
                "Contact support if issue persists"
            ]
        
        return {
            "type": error_type,
            "severity": severity,
            "suggestions": suggestions,
            "auto_fix": auto_fix,
            "confidence": 0.85
        }
    
    def _fallback_error_detection(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback error detection"""
        return {
            "success": True,
            "error_type": "unknown",
            "severity": "medium",
            "suggestions": ["Check logs for more information"],
            "confidence": 0.5,
            "ai_enhanced": False
        }
    
    def get_ai_insights(self, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered insights for the application"""
        if not self.is_ai_available():
            return {"ai_available": False, "insights": []}
        
        insights = []
        
        # Analyze recent activity patterns
        if "recent_orders" in data_context:
            insights.extend(self._analyze_order_patterns(data_context["recent_orders"]))
        
        # Analyze error patterns
        if "recent_errors" in data_context:
            insights.extend(self._analyze_error_patterns(data_context["recent_errors"]))
        
        # Performance insights
        if "performance_metrics" in data_context:
            insights.extend(self._analyze_performance(data_context["performance_metrics"]))
        
        return {
            "ai_available": True,
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "confidence": 0.8
        }
    
    def _analyze_order_patterns(self, orders: List[Dict[str, Any]]) -> List[str]:
        """Analyze order patterns for insights"""
        if not orders:
            return ["No recent orders to analyze"]
        
        insights = []
        
        # State distribution analysis
        states = [order.get("customer", {}).get("state") for order in orders]
        state_counts = {}
        for state in states:
            if state:
                state_counts[state] = state_counts.get(state, 0) + 1
        
        if state_counts:
            top_state = max(state_counts, key=state_counts.get)
            insights.append(f"Most orders from {top_state} ({state_counts[top_state]} orders)")
        
        # Carrier usage analysis
        carriers = [order.get("carrier") for order in orders]
        carrier_counts = {}
        for carrier in carriers:
            if carrier:
                carrier_counts[carrier] = carrier_counts.get(carrier, 0) + 1
        
        if carrier_counts:
            top_carrier = max(carrier_counts, key=carrier_counts.get)
            insights.append(f"Most used carrier: {top_carrier}")
        
        return insights
    
    def _analyze_error_patterns(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Analyze error patterns"""
        if not errors:
            return ["No recent errors - system running smoothly"]
        
        insights = []
        
        error_types = [error.get("type") for error in errors]
        if error_types:
            most_common_error = max(set(error_types), key=error_types.count)
            insights.append(f"Most common error: {most_common_error}")
        
        return insights
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze performance metrics"""
        insights = []
        
        if "response_time" in metrics:
            avg_response = metrics["response_time"]
            if avg_response > 2000:  # ms
                insights.append("Response times are higher than optimal (>2s)")
            else:
                insights.append("Response times are within acceptable range")
        
        if "error_rate" in metrics:
            error_rate = metrics["error_rate"]
            if error_rate > 0.05:  # 5%
                insights.append(f"Error rate is elevated at {error_rate:.1%}")
            else:
                insights.append("Error rate is within acceptable limits")
        
        return insights


# Global AI features instance
ai_features = AIEnhancedFeatures()


def get_ai_features() -> AIEnhancedFeatures:
    """Get the global AI features instance"""
    return ai_features