#!/usr/bin/env python3
"""Test the price prediction functionality"""

import requests
import json

# Test the prediction endpoint
url = "http://localhost:5000/api/product_price_prediction"

# Test with a product ID (adjust this based on your database)
test_data = {
    "product_id": 1  # Change this to a valid product ID
}

print("Testing product price prediction API...")
print(f"Request: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(url, json=test_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"\nError: {e}")
