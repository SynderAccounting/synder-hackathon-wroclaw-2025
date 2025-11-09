#!/usr/bin/env python3

# Read the content of app.py
with open('/home/dvdarch/Repos/Synder/app.py', 'r') as f:
    lines = f.readlines()

# Find the line with "return redirect(url_for('products'))" in the product editing function
# This should be around line 924 in the edit_product function
target_line_index = None
for i, line in enumerate(lines):
    if 'return redirect(url_for(\'products\'))' in line and i > 920 and i < 930:
        # Check if this is in the edit_product function context (after shopify sync)
        context = lines[max(0, i-30):i]
        has_shopify = any('Synchronize product changes to Shopify' in l or 'sync_product_to_shopify' in l for l in context)
        if has_shopify:
            target_line_index = i
            break

if target_line_index is not None:
    # Insert WooCommerce sync code before the return redirect
    woocommerce_sync_code = [
        '            # Synchronize product changes to WooCommerce if enabled\n',
        '            if WOOCOMMERCE_ENABLED:\n',
        '                try:\n',
        '                    # Get the updated product data\n',
        '                    updated_product = cursor.execute(\'SELECT * FROM products WHERE id = ?\', (product_id,)).fetchone()\n',
        '                    \n',
        '                    if updated_product:\n',
        '                        woocommerce_product_id = updated_product[\'woocommerce_product_id\']\n',
        '                        \n',
        '                        if woocommerce_product_id:  # Only sync if the product was previously synchronized\n',
        '                            product_data = {\n',
        '                                \'id\': product_id,\n',
        '                                \'name\': updated_product[\'name\'],\n',
        '                                \'description\': updated_product[\'description\'],\n',
        '                                \'price\': updated_product[\'price\'],\n',
        '                                \'stock_quantity\': updated_product[\'stock_quantity\'],\n',
        '                                \'category\': updated_product[\'category\'],\n',
        '                                \'technical_details\': updated_product[\'technical_details\'],\n',
        '                                \'photo\': updated_product[\'photo\']\n',
        '                            }\n',
        '                            \n',
        '                            sync_result = sync_product_to_woocommerce(product_data, woocommerce_product_id=woocommerce_product_id)\n',
        '                            \n',
        '                            if sync_result.get(\'success\'):\n',
        '                                print(f"Product updated in WooCommerce: {sync_result.get(\'message\')}")\n',
        '                            else:\n',
        '                                print(f"Failed to update product in WooCommerce: {sync_result.get(\'message\', sync_result.get(\'error\', \'Unknown error\'))}")\n',
        '                        else:\n',
        '                            # If no woocommerce_product_id was found, create it in WooCommerce\n',
        '                            product_data = {\n',
        '                                \'id\': product_id,\n',
        '                                \'name\': updated_product[\'name\'],\n',
        '                                \'description\': updated_product[\'description\'],\n',
        '                                \'price\': updated_product[\'price\'],\n',
        '                                \'stock_quantity\': updated_product[\'stock_quantity\'],\n',
        '                                \'category\': updated_product[\'category\'],\n',
        '                                \'technical_details\': updated_product[\'technical_details\'],\n',
        '                                \'photo\': updated_product[\'photo\']\n',
        '                            }\n',
        '                            \n',
        '                            sync_result = sync_product_to_woocommerce(product_data)\n',
        '                            \n',
        '                            if sync_result.get(\'success\'):\n',
        '                                woocommerce_product_id = sync_result.get(\'woocommerce_product_id\')\n',
        '                                if woocommerce_product_id:\n',
        '                                    cursor.execute("""\n',
        '                                        UPDATE products\n',
        '                                        SET woocommerce_product_id = ?\n',
        '                                        WHERE id = ?\n',
        '                                    """, (woocommerce_product_id, product_id))\n',
        '                                    conn.commit()\n',
        '                                    print(f"Product synchronized to WooCommerce: {sync_result.get(\'message\')}")\n',
        '                            else:\n',
        '                                print(f"Failed to sync product to WooCommerce: {sync_result.get(\'message\', sync_result.get(\'error\', \'Unknown error\'))}")\n',
        '                except Exception as woocommerce_error:\n',
        '                    print(f"WooCommerce sync error: {str(woocommerce_error)}")\n',
        '\n'
    ]
    
    # Insert the code at the target location
    for i, code_line in enumerate(woocommerce_sync_code):
        lines.insert(target_line_index + i, code_line)

# Write the modified content back to the file
with open('/home/dvdarch/Repos/Synder/app.py', 'w') as f:
    f.writelines(lines)

print("WooCommerce sync code added to product editing function!")