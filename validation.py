"""
Validation utilities for Unified Order & Warehouse Management System.

Provides input validation for customer, warehouse, and product data.

Classes:
    ValidationResult: Encapsulates validation results, errors, and warnings.

Functions:
    validate_customer_data: Validate customer input data.
    validate_warehouse_data: Validate warehouse data.

Typical usage example:
    result = validate_customer_data(customer_dict)
    if result.is_valid:
        # proceed
"""

import re
from typing import Dict, List


class ValidationResult:
    """Encapsulates validation results, errors, and warnings."""

    def __init__(
        self,
        is_valid: bool,
        errors: List[str] = None,
        warnings: List[str] = None,
    ):
        """
        Initialize ValidationResult.

        Args:
            is_valid (bool): Indicates if the validation passed.
            errors (List[str], optional): List of error messages. Defaults to None.
            warnings (List[str], optional): List of warning messages. Defaults to None.
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []


def validate_customer_data(customer_data: Dict) -> ValidationResult:
    """Validate customer input data"""
    errors = []
    warnings = []

    # Required fields
    if not customer_data.get("name"):
        errors.append("Customer name is required")

    if not customer_data.get("address_1"):
        errors.append("Address is required")

    if not customer_data.get("city"):
        errors.append("City is required")

    if not customer_data.get("country"):
        warnings.append("Country not specified, assuming US")

    # Phone validation
    phone = customer_data.get("phone", "")
    if phone and not _validate_phone(phone):
        warnings.append("Phone format may be invalid")

    # Email validation
    email = customer_data.get("email", "")
    if email and not _validate_email(email):
        errors.append("Email format is invalid")

    # Postal code validation
    postal_code = customer_data.get("postal_code", "")
    country = customer_data.get("country", "US")
    if postal_code and not _validate_postal_code(postal_code, country):
        warnings.append("Postal code format may be invalid")

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_warehouse_data(warehouse: Dict) -> ValidationResult:
    """Validate warehouse data"""
    errors = []
    warnings = []

    if not warehouse:
        errors.append("No warehouse selected")
        return ValidationResult(False, errors)

    required_fields = ["id", "name"]
    for field in required_fields:
        if not warehouse.get(field):
            errors.append(f"Warehouse {field} is missing")

    # Check if warehouse has address info
    if not warehouse.get("address_line_1"):
        warnings.append("Warehouse address information incomplete")

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_products(products: List[Dict]) -> ValidationResult:
    """Validate product selection"""
    errors = []
    warnings = []

    if not products:
        errors.append("No products selected")
        return ValidationResult(False, errors)

    if len(products) < 1:
        errors.append("At least 1 product required")

    for i, product in enumerate(products):
        # Only require ID as critical error, make title optional
        if not product.get("id") and not product.get("title"):
            errors.append(f"Product {i + 1} missing both ID and title")

        # Make title optional but warn if missing
        if not product.get("title"):
            # Auto-generate title if missing
            product["title"] = f"Fashion Item {i + 1}"
            warnings.append(f"Product {i + 1} title auto-generated")

        # Check price and provide default if needed
        price = product.get("price")
        if not price:
            product["price"] = "25.00"  # Default price
            warnings.append(f"Product {i + 1} using default price $25.00")
        else:
            try:
                float_price = float(price)
                if float_price <= 0:
                    product["price"] = "25.00"
                    msg = f"Product {
                        i + 1} invalid price, using default $25.00"
                    warnings.append(msg)
            except (ValueError, TypeError):
                product["price"] = "25.00"
                msg = f"Product {
                    i + 1} price format invalid, using default $25.00"
                warnings.append(msg)

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_order_data(
    customer_data: Dict, warehouse: Dict, products: List[Dict]
) -> ValidationResult:
    """Comprehensive order validation"""
    all_errors = []
    all_warnings = []

    # Validate each component
    customer_result = validate_customer_data(customer_data)
    warehouse_result = validate_warehouse_data(warehouse)
    products_result = validate_products(products)

    # Combine results
    all_errors.extend(customer_result.errors)
    all_errors.extend(warehouse_result.errors)
    all_errors.extend(products_result.errors)

    all_warnings.extend(customer_result.warnings)
    all_warnings.extend(warehouse_result.warnings)
    all_warnings.extend(products_result.warnings)

    return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)


def _validate_phone(phone: str) -> bool:
    """Validate phone number format - flexible for international numbers"""
    if not phone:
        return False

    # Remove all spaces, hyphens, parentheses for validation
    cleaned_phone = re.sub(r"[\s\-\(\)]+", "", phone.strip())

    # Accept international phone numbers with or without + prefix
    # Length between 7-15 digits, may start with +
    phone_pattern = r"^[+]?[0-9]{7,15}$"
    return bool(re.match(phone_pattern, cleaned_phone))


def _validate_email(email: str) -> bool:
    """Validate email format - improved version"""
    if not email:
        return False
    
    # Clean the email
    email = email.strip().lower()
    
    # More flexible email pattern that handles common formats
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    # Basic length check
    if len(email) < 5 or len(email) > 254:
        return False
    
    # Check for basic email structure
    if email.count('@') != 1:
        return False
    
    local, domain = email.split('@')
    
    # Local part validation
    if len(local) < 1 or len(local) > 64:
        return False
    
    # Domain part validation
    if len(domain) < 3 or domain.count('.') < 1:
        return False
    
    return bool(re.match(email_pattern, email))


def _validate_postal_code(postal_code: str, country: str) -> bool:
    """Validate postal code based on country - more flexible"""
    if not postal_code:
        return False

    postal_code = postal_code.strip()
    country = country.upper()

    # Country-specific patterns
    patterns = {
        "US": r"^\d{5}(-\d{4})?$",  # US ZIP: 12345 or 12345-6789
        "GB": r"^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$",
        "CA": r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$",  # Canada: K1A 0A6
        "DE": r"^\d{5}$",  # Germany: 12345
        "FR": r"^\d{5}$",  # France: 75001
        "IE": r"^[A-Z]\d{2}\s?[A-Z0-9]{4}$",  # Ireland: D02 XY45
        "PH": r"^\d{4}$",  # Philippines: 1234
    }

    if country in patterns:
        return bool(re.match(patterns[country], postal_code.upper()))

    # Default validation - at least 3 characters with digits or letters
    return len(postal_code) >= 3 and bool(re.search(r"[0-9A-Za-z]", postal_code))
