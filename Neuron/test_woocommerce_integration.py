"""
Test script to verify WooCommerce integration functionality
"""
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_woocommerce_import():
    """Test that WooCommerce integration can be imported without errors"""
    try:
        from woocommerce_integration import WooCommerceProductSync
        print("✓ WooCommerce integration imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import WooCommerce integration: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing WooCommerce integration: {e}")
        return False

def test_woocommerce_instance():
    """Test that WooCommerce sync instance can be created"""
    try:
        from woocommerce_integration import woocommerce_sync
        print("✓ WooCommerce sync instance created successfully")
        print(f"  Store URL: {woocommerce_sync.store_url}")
        print("  Consumer key and secret are set")
        return True
    except Exception as e:
        print(f"✗ Error creating WooCommerce sync instance: {e}")
        return False

def test_woocommerce_api_connection():
    """Test basic API connection to WooCommerce"""
    try:
        from woocommerce_integration import woocommerce_sync
        result = woocommerce_sync.get_all_products()
        if result["success"]:
            print("✓ WooCommerce API connection successful")
            print(f"  Found {len(result['data'])} products in WooCommerce store")
            return True
        else:
            print(f"✗ WooCommerce API connection failed: {result['error']}")
            return False
    except Exception as e:
        print(f"✗ Error testing WooCommerce API connection: {e}")
        return False

if __name__ == "__main__":
    print("Testing WooCommerce Integration...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_woocommerce_import),
        ("Instance Creation Test", test_woocommerce_instance),
        ("API Connection Test", test_woocommerce_api_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All WooCommerce integration tests passed!")
    else:
        print("✗ Some tests failed. Check the output above for details.")