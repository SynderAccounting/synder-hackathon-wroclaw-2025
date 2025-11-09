#!/usr/bin/env python3
"""
Script to import retail price data from CSV into the products database
"""
import sqlite3
import pandas as pd
import os

def import_retail_prices_to_db():
    # Connect to the database
    conn = sqlite3.connect('retail_crms.db')
    cursor = conn.cursor()
    
    print("Reading retail prices data from CSV...")
    # Read the CSV file
    df = pd.read_csv('products_prices/Retail_Prices_of _Products.csv')
    
    # Filter for unique products by name to avoid duplicates
    unique_products = df[['Products', 'Product Category', 'VALUE']].drop_duplicates(subset=['Products'])
    
    print(f"Found {len(unique_products)} unique products in the CSV")
    
    # Get existing products to avoid duplicates
    cursor.execute("SELECT name FROM products")
    existing_products = set(row[0] for row in cursor.fetchall())
    
    print(f"Found {len(existing_products)} existing products in database")
    
    # Prepare products to add
    products_to_add = []
    for _, row in unique_products.iterrows():
        product_name = row['Products']
        category = row['Product Category']
        price = float(row['VALUE'])
        
        # Only add if it doesn't already exist in the database
        if product_name not in existing_products:
            products_to_add.append((product_name, category, price))
    
    print(f"Adding {len(products_to_add)} new products to the database...")
    
    # Insert new products into the database
    for product_name, category, price in products_to_add:
        try:
            cursor.execute("""
                INSERT INTO products (name, description, price, category, stock_quantity, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                product_name, 
                f"Product category: {category}", 
                price,
                category,
                100  # Default stock quantity
            ))
        except Exception as e:
            print(f"Error adding product {product_name}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Successfully added {len(products_to_add)} new products to the database!")

if __name__ == "__main__":
    if not os.path.exists('products_prices/Retail_Prices_of _Products.csv'):
        print("CSV file not found! Please check the path.")
        exit(1)
    
    import_retail_prices_to_db()