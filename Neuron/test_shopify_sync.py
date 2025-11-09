#!/usr/bin/env python3
"""
Test script to verify Shopify integration functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shopify_integration import ShopifyProductSync, sync_product_to_shopify, delete_product_from_shopify

def test_shopify_connection():
    """Test basic Shopify connection"""
    print("Testing Shopify connection...")
    
    try:
        sync = ShopifyProductSync()
        result = sync.get_all_products()
        
        if result["success"]:
            print(f"✓ Connected to Shopify successfully!")
            print(f"✓ Found {len(result['data'])} products in Shopify store")
            return True
        else:
            print(f"✗ Failed to connect to Shopify: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to Shopify: {str(e)}")
        return False

def test_product_sync():
    """Test product synchronization"""
    print("\nTesting product synchronization...")
    
    # Sample product data
    sample_product = {
        'id': 999,
        'name': 'Test Product for Sync',
        'description': 'This is a test product to verify Shopify synchronization',
        'price': 29.99,
        'stock_quantity': 50,
        'category': 'Test Category',
        'technical_details': 'This is for testing purposes only',
        'photo': None  # No photo for this test
    }
    
    try:
        result = sync_product_to_shopify(sample_product)
        
        if result["success"]:
            print(f"✓ Product synchronized to Shopify successfully!")
            print(f"✓ Shopify Product ID: {result['shopify_product_id']}")
            
            # Try to delete the test product
            delete_result = delete_product_from_shopify(result['shopify_product_id'])
            if delete_result["success"]:
                print(f"✓ Test product cleaned up from Shopify")
            else:
                print(f"⚠ Test product cleanup failed: {delete_result.get('error', 'Unknown error')}")
                
            return True
        else:
            print(f"✗ Product sync failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error during product sync: {str(e)}")
        return False

if __name__ == "__main__":
    print("Shopify Integration Test")
    print("="*50)
    
    success = True
    success &= test_shopify_connection()
    success &= test_product_sync()
    
    print("\n" + "="*50)
    if success:
        print("✓ All tests passed! Shopify integration is working correctly.")
    else:
        print("✗ Some tests failed. Please check your Shopify configuration.")
    
    print("\nNote: The application is running on http://127.0.0.1:5001")
    print("You can now access the product management features with Shopify sync enabled.")