# Utility functions (parsing, random selection, etc.)
# Reuse parsing logic from your GUIs

import re
from typing import Dict, Optional

def parse_customer_input(input_text: str) -> Optional[Dict]:
    """Parse various customer input formats (from your GUI scripts)"""
    input_text = input_text.strip()
    
    if not input_text:
        return None
    
    # Tab-separated format (primary format)
    if '\t' in input_text:
        parts = input_text.split('\t')
        if len(parts) >= 8:
            # Handle cases where contact info is in one field
            contact_parts = parts[1].split() if parts[1] else ['', '']
            phone = contact_parts[0] if contact_parts else ''
            email = contact_parts[1] if len(contact_parts) > 1 else ''
            
            return {
                'name': parts[0].strip(),
                'phone': phone,
                'email': email,
                'address_1': parts[2].strip(),
                'address_2': parts[3].strip() if len(parts) > 3 and parts[3] else '',
                'city': parts[4].strip() if len(parts) > 4 else '',
                'state': parts[5].strip() if len(parts) > 5 else '',
                'postal_code': parts[6].strip() if len(parts) > 6 else '',
                'country': parts[7].strip() if len(parts) > 7 else 'US',
                'detected_format': 'Tab-separated format'
            }
    
    # Space-separated format (fallback)
    parts = input_text.split()
    if len(parts) >= 4:
        return {
            'name': f"{parts[0]} {parts[1]}" if len(parts) > 1 else parts[0],
            'phone': next((p for p in parts if '+' in p or p.replace('-', '').replace('(', '').replace(')', '').isdigit()), ''),
            'email': next((p for p in parts if '@' in p), ''),
            'address_1': ' '.join(parts[2:5]) if len(parts) > 4 else parts[2] if len(parts) > 2 else '',
            'city': parts[-3] if len(parts) > 2 else '',
            'state': parts[-2] if len(parts) > 1 else '',
            'postal_code': parts[-1] if parts else '',
            'country': 'US',
            'detected_format': 'Space-separated format'
        }
    
    return None

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract phone and email from text"""
    phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    phone_match = re.search(phone_pattern, text)
    email_match = re.search(email_pattern, text)
    
    return {
        'phone': phone_match.group() if phone_match else '',
        'email': email_match.group() if email_match else ''
    }

def format_customer_data(customer_dict: Dict) -> str:
    """Format customer data for display"""
    return f"""
    Name: {customer_dict.get('name', 'N/A')}
    Phone: {customer_dict.get('phone', 'N/A')}
    Email: {customer_dict.get('email', 'N/A')}
    Address: {customer_dict.get('address_1', 'N/A')}
    City: {customer_dict.get('city', 'N/A')}
    State: {customer_dict.get('state', 'N/A')}
    Postal Code: {customer_dict.get('postal_code', 'N/A')}
    Country: {customer_dict.get('country', 'N/A')}
    """

def format_phone_number(phone: str) -> str:
    """Format phone number to a standard format"""
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # If it starts with 00, replace with +
    if cleaned.startswith('00'):
        cleaned = '+' + cleaned[2:]
    
    # Add country code if missing
    if not cleaned.startswith('+'):
        if len(cleaned) == 10:
            cleaned = '+1' + cleaned
        elif len(cleaned) > 10:
            cleaned = '+' + cleaned
    
    return cleaned

def format_postal_code(postal_code: str, country: str) -> str:
    """Format postal code according to country standards"""
    if not postal_code:
        return ""
    
    postal_code = postal_code.strip().upper()
    country = country.upper()
    
    # Country-specific formatting
    if country == 'GB':
        # UK postal codes: ensure space before last 3 characters if not present
        postal_code = re.sub(r'\s+', '', postal_code)  # Remove existing spaces
        if len(postal_code) > 3:
            postal_code = postal_code[:-3] + ' ' + postal_code[-3:]
    
    elif country == 'CA':
        # Canada: Format as A1A 1A1
        postal_code = re.sub(r'\s+', '', postal_code)
        if len(postal_code) == 6:
            postal_code = postal_code[:3] + ' ' + postal_code[3:]
    
    elif country == 'IE':
        # Ireland: Ensure proper spacing
        if len(postal_code) > 3 and ' ' not in postal_code:
            postal_code = postal_code[:3] + ' ' + postal_code[3:]
    
    return postal_code

def normalize_customer_data(customer_data: Dict) -> Dict:
    """Normalize and format customer data"""
    if not customer_data:
        return customer_data
    
    formatted = customer_data.copy()
    
    # Format phone number
    if 'phone' in formatted:
        formatted['phone'] = format_phone_number(formatted['phone'])
    
    # Format postal code
    if 'postal_code' in formatted and 'country' in formatted:
        formatted['postal_code'] = format_postal_code(formatted['postal_code'], formatted['country'])
    
    # Ensure name is properly formatted
    if 'name' in formatted:
        formatted['name'] = formatted['name'].strip()
    
    # Ensure address fields are properly formatted
    for field in ['address_1', 'address_2', 'city', 'state']:
        if field in formatted:
            formatted[field] = formatted[field].strip()
    
    # Format country code
    if 'country' in formatted:
        formatted['country'] = formatted['country'].strip().upper()
    
    return formatted
