import os
import base64
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shopify API Configuration
SHOP_URL = os.getenv("SHOPIFY_STORE_URL")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-07"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

class ShopifyProductSync:
    """
    Shopify product synchronization class to handle all product operations
    between the local database and Shopify store
    """

    def __init__(self):
        """Initialize the Shopify API client"""
        if not SHOP_URL or not ACCESS_TOKEN:
            raise ValueError("Missing Shopify configuration. Please set SHOP_URL and ACCESS_TOKEN in your .env file.")

        self.shop_url = SHOP_URL
        self.access_token = ACCESS_TOKEN
        self.api_version = API_VERSION
        self.headers = HEADERS

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Shopify API
        """
        url = f"{self.shop_url}/admin/api/{self.api_version}/{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(f"Shopify API request: {method} {endpoint}, Status: {response.status_code}")

            if response.status_code >= 400:
                logger.error(f"Shopify API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.content else None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_product(self, name: str, price: float, description: str = "",
                      stock_quantity: int = 0, category: str = "Default",
                      photo_path: Optional[str] = None,
                      technical_details: Optional[str] = None,
                      shopify_product_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new product in Shopify
        """
        logger.info(f"Creating product in Shopify: {name}")

        # Prepare product data for Shopify
        shopify_product_data = {
            "product": {
                "title": name,
                "body_html": description or f"Description for {name}",
                "vendor": os.getenv("SHOPIFY_VENDOR", "Default Vendor"),
                "product_type": category or "Default",
                "variants": [
                    {
                        "price": str(price),
                        "sku": f"SKU-{name.replace(' ', '-').lower()}-{hash(name) % 10000}",
                        "inventory_quantity": stock_quantity
                    }
                ]
            }
        }

        # Add photo if available
        if photo_path:
            try:
                from app import app  # Import app to get upload folder
                photo_full_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_path)

                if os.path.exists(photo_full_path):
                    with open(photo_full_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")
                    shopify_product_data["product"]["images"] = [{"attachment": encoded}]
                else:
                    logger.warning(f"Product photo not found: {photo_full_path}")
            except Exception as e:
                logger.error(f"Error processing product photo: {str(e)}")

        # Add technical details as custom fields if provided
        metafields = []
        if technical_details:
            metafields.append({
                "namespace": "custom",
                "key": "technical_details",
                "value": technical_details,
                "type": "single_line_text_field"
            })

        if metafields:
            shopify_product_data["product"]["metafields"] = metafields

        # If shopify_product_id is provided, update existing product instead
        if shopify_product_id:
            return self._update_product(shopify_product_id, name, price, description,
                                      stock_quantity, category, photo_path, technical_details)

        # Make API call to create product
        result = self._make_request("POST", "products.json", shopify_product_data)

        if result["success"]:
            product = result["data"]["product"]
            logger.info(f"Successfully created product in Shopify: {product['id']}")
            return {
                "success": True,
                "shopify_product_id": product["id"],
                "name": product["title"],
                "message": f"Product '{name}' successfully created in Shopify with ID {product['id']}"
            }
        else:
            logger.error(f"Failed to create product in Shopify: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "message": f"Failed to create product '{name}' in Shopify"
            }

    def _update_product(self, shopify_product_id: int, name: str, price: float,
                       description: str = "", stock_quantity: int = 0,
                       category: str = "Default", photo_path: Optional[str] = None,
                       technical_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing product in Shopify
        """
        logger.info(f"Updating product in Shopify: {shopify_product_id}")

        # First get the existing product to update its variant
        get_result = self._make_request("GET", f"products/{shopify_product_id}.json")

        if not get_result["success"]:
            logger.error(f"Failed to get existing product for update: {get_result['error']}")
            return get_result

        existing_product = get_result["data"]["product"]
        existing_variant = existing_product["variants"][0]

        # Prepare update data
        update_data = {
            "product": {
                "id": shopify_product_id,
                "title": name,
                "body_html": description or f"Description for {name}",
                "product_type": category or "Default",
                "variants": [
                    {
                        "id": existing_variant["id"],
                        "price": str(price),
                        "inventory_quantity": stock_quantity
                    }
                ]
            }
        }

        # Add technical details as custom fields if provided
        if technical_details:
            metafields_data = {
                "product": {
                    "id": shopify_product_id,
                    "metafields": [
                        {
                            "namespace": "custom",
                            "key": "technical_details",
                            "value": technical_details,
                            "type": "single_line_text_field"
                        }
                    ]
                }
            }

            # First update the product itself
            result = self._make_request("PUT", f"products/{shopify_product_id}.json", update_data)

            if result["success"]:
                # Then update metafields
                metafields_result = self._make_request("PUT", f"products/{shopify_product_id}.json", metafields_data)
                if metafields_result["success"]:
                    return {
                        "success": True,
                        "shopify_product_id": shopify_product_id,
                        "name": name,
                        "message": f"Product '{name}' successfully updated in Shopify"
                    }
                else:
                    # Return the product update success but log the metafields error
                    logger.warning(f"Product updated but metafields failed: {metafields_result['error']}")
                    return {
                        "success": True,
                        "shopify_product_id": shopify_product_id,
                        "name": name,
                        "message": f"Product '{name}' updated in Shopify but with metafields error"
                    }
            else:
                return result
        else:
            result = self._make_request("PUT", f"products/{shopify_product_id}.json", update_data)

            if result["success"]:
                return {
                    "success": True,
                    "shopify_product_id": shopify_product_id,
                    "name": name,
                    "message": f"Product '{name}' successfully updated in Shopify"
                }
            else:
                return result

    def update_product(self, shopify_product_id: int, name: str, price: float,
                      description: str = "", stock_quantity: int = 0,
                      category: str = "Default", photo_path: Optional[str] = None,
                      technical_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing product in Shopify
        """
        return self._update_product(shopify_product_id, name, price, description,
                                  stock_quantity, category, photo_path, technical_details)

    def delete_product(self, shopify_product_id: int) -> Dict[str, Any]:
        """
        Delete a product from Shopify
        """
        logger.info(f"Deleting product from Shopify: {shopify_product_id}")

        result = self._make_request("DELETE", f"products/{shopify_product_id}.json")

        if result["success"]:
            logger.info(f"Successfully deleted product from Shopify: {shopify_product_id}")
            return {
                "success": True,
                "shopify_product_id": shopify_product_id,
                "message": f"Product with ID {shopify_product_id} successfully deleted from Shopify"
            }
        else:
            logger.error(f"Failed to delete product from Shopify: {result['error']}")
            return {
                "success": False,
                "shopify_product_id": shopify_product_id,
                "error": result["error"],
                "message": f"Failed to delete product with ID {shopify_product_id} from Shopify"
            }

    def sync_product_to_shopify(self, product_id: int, name: str, price: float,
                               description: str = "", stock_quantity: int = 0,
                               category: str = "Default", photo_path: Optional[str] = None,
                               technical_details: Optional[str] = None,
                               shopify_product_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Synchronize a local product to Shopify (create or update)
        """
        if shopify_product_id:
            # Update existing product
            return self.update_product(shopify_product_id, name, price, description,
                                     stock_quantity, category, photo_path, technical_details)
        else:
            # Create new product
            return self.create_product(name, price, description, stock_quantity,
                                     category, photo_path, technical_details)

    def get_product(self, shopify_product_id: int) -> Dict[str, Any]:
        """
        Get a product from Shopify by its ID
        """
        logger.info(f"Fetching product from Shopify: {shopify_product_id}")

        result = self._make_request("GET", f"products/{shopify_product_id}.json")

        if result["success"]:
            return {
                "success": True,
                "data": result["data"]["product"]
            }
        else:
            logger.error(f"Failed to get product from Shopify: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }

    def get_all_products(self) -> Dict[str, Any]:
        """
        Get all products from Shopify
        """
        logger.info("Fetching all products from Shopify")

        result = self._make_request("GET", "products.json")

        if result["success"]:
            return {
                "success": True,
                "data": result["data"]["products"]
            }
        else:
            logger.error(f"Failed to get products from Shopify: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }


# Global instance for the shopify sync
shopify_sync = ShopifyProductSync()


def sync_product_to_shopify(product_data: Dict[str, Any], shopify_product_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Helper function to synchronize a local product to Shopify
    """
    try:
        # Extract 3D visualization path if available
        # Note: Adding to product_data for potential use in future enhancements
        # Currently passing to sync function as a parameter

        sync_result = shopify_sync.sync_product_to_shopify(
            product_id=product_data.get('id', 0),
            name=product_data.get('name', ''),
            price=product_data.get('price', 0.0),
            description=product_data.get('description', ''),
            stock_quantity=product_data.get('stock_quantity', 0),
            category=product_data.get('category', 'Default'),
            photo_path=product_data.get('photo'),
            technical_details=product_data.get('technical_details'),
            shopify_product_id=shopify_product_id
        )

        return sync_result
    except Exception as e:
        logger.error(f"Error syncing product to Shopify: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error syncing product to Shopify"
        }


def delete_product_from_shopify(shopify_product_id: int) -> Dict[str, Any]:
    """
    Helper function to delete a product from Shopify
    """
    try:
        return shopify_sync.delete_product(shopify_product_id)
    except Exception as e:
        logger.error(f"Error deleting product from Shopify: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error deleting product from Shopify"
        }
