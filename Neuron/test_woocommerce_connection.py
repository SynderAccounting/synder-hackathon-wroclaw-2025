#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/dvdarch/Repos/Synder')

# Import the functions we need to test
try:
    from woocommerce_integration import WooCommerceProductSync
    print("✓ Successfully imported WooCommerce integration")
except ImportError as e:
    print(f"✗ Failed to import WooCommerce integration: {e}")
    sys.exit(1)

# Test basic functionality
try:
    sync_client = WooCommerceProductSync()
    print("✓ Successfully created WooCommerce sync client")
    print(f"  Store URL: {sync_client.store_url}")
except Exception as e:
    print(f"✗ Failed to create WooCommerce sync client: {e}")
    sys.exit(1)

# Test making a basic API call (get products)
try:
    result = sync_client.get_all_products()
    if result['success']:
        print(f"✓ Successfully connected to WooCommerce API")
        print(f"  Found {len(result.get('data', []))} products in store")
    else:
        print(f"✗ Failed to connect to WooCommerce API: {result.get('error')}")
except Exception as e:
    print(f"✗ Error testing WooCommerce API connection: {e}")
    sys.exit(1)

print("\nWooCommerce integration test completed.")