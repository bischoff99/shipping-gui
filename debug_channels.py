#!/usr/bin/env python3
"""
Debug available channels to find one that supports order creation
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI

print("=== DEBUGGING CHANNELS ===")

try:
    veeqo_api = VeeqoAPI()
    
    print("1. Getting all channels...")
    channels = veeqo_api.make_request("/channels")
    
    if channels:
        print(f"   Found {len(channels)} channels")
        
        print("\n2. Channel details:")
        for i, channel in enumerate(channels):
            print(f"\n   Channel {i+1}:")
            print(f"     ID: {channel.get('id')}")
            print(f"     Name: {channel.get('name')}")
            print(f"     Type: {channel.get('type_code')}")
            print(f"     State: {channel.get('state')}")
            
            # Look for channels that might support order creation
            # Usually "direct" or "manual" channels allow order creation
            if channel.get('type_code') in ['direct', 'manual', 'pos']:
                print(f"     *** LIKELY SUPPORTS ORDER CREATION ***")
    
    print("\n3. Looking for channels that typically support order creation...")
    suitable_channels = []
    
    for channel in channels:
        type_code = channel.get('type_code', '').lower()
        state = channel.get('state', '').lower()
        
        # Channel types that typically support order creation
        if type_code in ['direct', 'manual', 'pos', 'phone'] and state == 'active':
            suitable_channels.append(channel)
            print(f"   SUITABLE: {channel.get('name')} (ID: {channel.get('id')}, Type: {type_code})")
    
    if suitable_channels:
        print(f"\n4. Found {len(suitable_channels)} suitable channels for order creation")
        best_channel = suitable_channels[0]
        print(f"   Best channel: {best_channel.get('name')} (ID: {best_channel.get('id')})")
    else:
        print("\n4. No suitable channels found - this might be why order creation is failing")

except Exception as e:
    print(f"ERROR: {e}")

print("\n=== DEBUGGING COMPLETE ===")