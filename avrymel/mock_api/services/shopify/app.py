"""Shopify API Mock Server

A Flask server that mocks the Shopify API.
Provides a /get_order/ endpoint that returns randomly generated order data.
"""

from flask import Flask, jsonify
import json
import sys
import os

# Add parent directories to path to import order_generator and models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from order_generator import OrderGenerator
from models import ShopifyOrder

app = Flask(__name__)
generator = OrderGenerator()


@app.route("/get_order/", methods=["GET"])
def get_order():
    """Generate and return a random order in JSON format."""
    # Generate base order data
    order_data = generator.generate_order_data()

    # Convert to Shopify-specific order
    shopify_order = ShopifyOrder(
        order_id=order_data.order_id,
        created_at=order_data.created_at,
        updated_at=order_data.updated_at,
        currency=order_data.currency,
        financial_status=order_data.financial_status,
        subtotal=order_data.subtotal,
        discount=order_data.discount,
        total_tax=order_data.total_tax,
        final_price=order_data.final_price,
        billing_address=order_data.billing_address,
        shipping_address=order_data.shipping_address,
        items=order_data.items,
        fulfillment=order_data.fulfillment,
        customer=order_data.customer,
    )

    # Return as JSON
    order_json = json.loads(shopify_order.to_json())
    return jsonify(order_json)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Shopify API Mock"}), 200


@app.route("/", methods=["GET"])
def index():
    """Service info endpoint."""
    return jsonify(
        {
            "service": "Shopify API Mock",
            "version": "1.0.0",
            "endpoints": {
                "/health": "Health check",
                "/get_order/": "Generate a random order",
            },
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
