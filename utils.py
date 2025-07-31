"""
Utility functions for Unified Order & Warehouse Management System.

Provides parsing, normalization, and helper utilities for customer and order data.

Functions:
    parse_customer_input: Parse customer input from various formats.
    normalize_customer_data: Normalize customer data for processing.
    extract_contact_info: Extract contact info from text.

Typical usage example:
    customer = parse_customer_input(input_text)
"""

# Exported functions for use in app.py and other modules
__all__ = [
    "parse_customer_input",
    "normalize_customer_data",
]

import re
from typing import Dict, Optional


def parse_customer_input(input_text: str) -> Optional[Dict]:
    """Parse various customer input formats (from your GUI scripts)"""
    input_text = input_text.strip()

    if not input_text:
        return None

    # Tab-separated format (primary format)
    # Expected format: Name\tPhone\tEmail\tAddress1\tAddress2\tCity\tState\tPostalCode\tCountry
    if "\t" in input_text:
        parts = input_text.split("\t")
        if len(parts) >= 8:
            return {
                "name": parts[0].strip(),
                "phone": parts[1].strip(),
                "email": parts[2].strip(),
                "address_1": parts[3].strip(),
                "address_2": (parts[4].strip() if len(parts) > 4 else ""),
                "city": parts[5].strip() if len(parts) > 5 else "",
                "state": parts[6].strip() if len(parts) > 6 else "",
                "postal_code": parts[7].strip() if len(parts) > 7 else "",
                "country": parts[8].strip() if len(parts) > 8 else "US",
                "detected_format": "Tab-separated format",
            }

    # Comma-separated format (common format)
    if "," in input_text:
        parts = [p.strip() for p in input_text.split(",")]
        if len(parts) >= 6:
            # Find phone and email in the parts
            phone = ""
            email = ""
            for part in parts:
                if "@" in part and not email:
                    email = part
                elif (("+" in part or part.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").isdigit()) 
                      and len(part.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")) >= 10 and not phone):
                    phone = part

            return {
                "name": parts[0],
                "phone": phone,
                "email": email,
                "address_1": parts[1] if len(parts) > 1 else "",
                "address_2": "",
                "city": parts[2] if len(parts) > 2 else "",
                "state": parts[3] if len(parts) > 3 else "",
                "postal_code": parts[4] if len(parts) > 4 else "",
                "country": parts[5] if len(parts) > 5 else "US",
                "detected_format": "Comma-separated format",
            }

    # Space-separated format (fallback)
    parts = input_text.split()
    if len(parts) >= 4:
        return {
            "name": f"{parts[0]} {parts[1]}" if len(parts) > 1 else parts[0],
            "phone": next(
                (
                    p
                    for p in parts
                    if "+" in p
                    or (p.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").isdigit() 
                        and len(p.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")) >= 10)
                ),
                "",
            ),
            "email": next((p for p in parts if "@" in p), ""),
            "address_1": (
                " ".join(parts[2:5])
                if len(parts) > 4
                else parts[2] if len(parts) > 2 else ""
            ),
            "city": parts[-3] if len(parts) > 2 else "",
            "state": parts[-2] if len(parts) > 1 else "",
            "postal_code": parts[-1] if parts else "",
            "country": "US",
            "detected_format": "Space-separated format",
        }

    return None


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract phone and email from text"""
    phone_pattern = r"[\+]?[\d\-\(\)\s]{10,}"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    phones = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)

    return {
        "phone": phones[0] if phones else "",
        "email": emails[0] if emails else "",
    }


def normalize_customer_data(customer_data: Dict) -> Dict:
    """Normalize customer data for consistency"""
    if not customer_data:
        return {}

    # Normalize phone
    phone = customer_data.get("phone", "")
    if phone:
        # Remove spaces, dashes, parentheses
        phone = re.sub(r"[^\d+]", "", phone)
        customer_data["phone"] = phone

    # Normalize email
    email = customer_data.get("email", "")
    if email:
        customer_data["email"] = email.lower().strip()

    # Normalize state to uppercase
    state = customer_data.get("state", "")
    if state:
        customer_data["state"] = state.upper()

    # Normalize country
    country = customer_data.get("country", "")
    if not country:
        customer_data["country"] = "US"
    else:
        customer_data["country"] = country.upper()

    return customer_data