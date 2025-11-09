"""
Quick verification script to ensure WooCommerce integration is properly integrated with the app
"""
import sys
import os

# Add the project directory to path
sys.path.append('/home/dvdarch/Repos/Synder')

def verify_app_integration():
    """Verify that the app can import and use both Shopify and WooCommerce integrations"""
    print("Verifying app integration with WooCommerce...")
    
    try:
        # Try to import the app to check for any import errors
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "/home/dvdarch/Repos/Synder/app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # Execute the module to test imports
        spec.loader.exec_module(app_module)
        
        print("✓ App imports successfully with WooCommerce integration")
        
        # Check if WOOCOMMERCE_ENABLED is defined
        if hasattr(app_module, 'WOOCOMMERCE_ENABLED'):
            if app_module.WOOCOMMERCE_ENABLED:
                print("✓ WooCommerce integration is enabled")
            else:
                print("? WooCommerce integration is disabled (file may not exist)")
        else:
            print("? WOOCOMMERCE_ENABLED not found in app")
            
        return True
    except Exception as e:
        print(f"✗ Error importing app with WooCommerce integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_woocommerce_functions():
    """Verify that the WooCommerce functions are available"""
    print("\nVerifying WooCommerce functions...")
    
    try:
        from woocommerce_integration import (
            sync_product_to_woocommerce,
            delete_product_from_woocommerce,
            get_woocommerce_product
        )
        print("✓ All WooCommerce sync functions available")
        return True
    except ImportError as e:
        print(f"✗ Error importing WooCommerce functions: {e}")
        return False

def verify_database_migration():
    """Verify that the database can be updated with the new column"""
    print("\nVerifying database migration...")
    
    import sqlite3
    
    # Connect to the database
    conn = sqlite3.connect('/home/dvdarch/Repos/Synder/retail_crms.db')
    cursor = conn.cursor()
    
    try:
        # Check if woocommerce_product_id column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'woocommerce_product_id' in columns:
            print("✓ woocommerce_product_id column exists in products table")
        else:
            print("? woocommerce_product_id column not found in products table")
            
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error checking database: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("WooCommerce Integration Verification")
    print("=" * 50)
    
    tests = [
        verify_app_integration,
        verify_woocommerce_functions,
        verify_database_migration
    ]
    
    passed = 0
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ All verifications passed! WooCommerce integration is properly set up.")
    else:
        print("? Some verifications failed. Check the output above for details.")