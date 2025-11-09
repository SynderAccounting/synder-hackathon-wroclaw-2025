#!/usr/bin/env python3

# Read the content of app.py
with open('/home/dvdarch/Repos/Synder/app.py', 'r') as f:
    lines = f.readlines()

# Find the line with "return redirect(url_for('products'))" in the product creation function
# This should be around line 774 in the add_product function
target_line_index = None
for i, line in enumerate(lines):
    if 'return redirect(url_for(\'products\'))' in line and i > 700 and i < 800:
        # Check if this is in the add_product function context (after shopify sync)
        if any('Synchronize product to Shopify' in l or 'sync_product_to_shopify' in l for l in lines[max(0, i-30):i]):
            target_line_index = i
            break

if target_line_index is not None:
    # Insert WooCommerce sync code before the return redirect
    woocommerce_sync_code = [
        '            # Synchronize product to WooCommerce if enabled\n',
        '            if WOOCOMMERCE_ENABLED:\n',
        '                try:\n',
        '                    # Get the photo filename for the product\n',
        '                    photo_result = cursor.execute(\'SELECT photo FROM products WHERE id = ?\', (product_id,)).fetchone()\n',
        '                    photo_filename = photo_result[\'photo\'] if photo_result else None\n',
        '                    \n',
        '                    product_data = {\n',
        '                        \'id\': product_id,\n',
        '                        \'name\': data[\'name\'],\n',
        '                        \'description\': data.get(\'description\', \'\'),\n',
        '                        \'price\': float(data[\'price\']),\n',
        '                        \'stock_quantity\': int(data[\'stock_quantity\']),\n',
        '                        \'category\': data.get(\'category\', \'\'),\n',
        '                        \'technical_details\': data.get(\'technical_details\', \'\'),\n',
        '                        \'photo\': photo_filename\n',
        '                    }\n',
        '\n',
        '                    sync_result = sync_product_to_woocommerce(product_data)\n',
        '\n',
        '                    if sync_result.get(\'success\'):\n',
        '                        # Update product with WooCommerce product ID if successful\n',
        '                        woocommerce_product_id = sync_result.get(\'woocommerce_product_id\')\n',
        '                        if woocommerce_product_id:\n',
        '                            cursor.execute("""\n',
        '                                UPDATE products\n',
        '                                SET woocommerce_product_id = ?\n',
        '                                WHERE id = ?\n',
        '                            """, (woocommerce_product_id, product_id))\n',
        '                            conn.commit()\n',
        '                            print(f"Product synchronized to WooCommerce: {sync_result.get(\'message\')}")\n',
        '                    else:\n',
        '                        print(f"Failed to sync product to WooCommerce: {sync_result.get(\'message\', sync_result.get(\'error\', \'Unknown error\'))}")\n',
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

print("WooCommerce sync code added to product creation function!")