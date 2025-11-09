import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging
import base64
import httpx
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WooCommerce API Configuration - hardcoded for now (will make more secure in future)
WOOCOMMERCE_URL = "https://neuron-test-2.wasmer.app"
WOOCOMMERCE_CONSUMER_KEY = "ck_beffe47e4cbd860137c6450d9392b9484044f392"
WOOCOMMERCE_CONSUMER_SECRET = "cs_ed407b798bc01d8eacd5c7952e70e4f47e55826c"


class WooCommerceProductSync:
    """
    WooCommerce product synchronization class to handle all product operations
    between the local database and WooCommerce store
    """

    def __init__(self):
        """Initialize the WooCommerce API client"""
        # Using hardcoded values now (will make more secure in future)
        self.store_url = WOOCOMMERCE_URL.rstrip("/")
        self.consumer_key = WOOCOMMERCE_CONSUMER_KEY
        self.consumer_secret = WOOCOMMERCE_CONSUMER_SECRET
        self.auth = (self.consumer_key, self.consumer_secret)

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the WooCommerce API
        """
        url = f"{self.store_url}/wp-json/wc/v3/{endpoint}"

        headers = {"Content-Type": "application/json"}

        # Print debug information to stdout
        print(f"WooCommerce API Request: {method} {url}")
        if data:
            print(f"Request Data: {data}")

        try:
            with httpx.Client(http2=True, timeout=30.0) as client:
                if method.upper() == "GET":
                    response = client.get(url, auth=self.auth, headers=headers)
                elif method.upper() == "POST":
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!", url, self.auth, headers, data)
                    response = client.post(
                        url, auth=self.auth, headers=headers, json=data
                    )
                elif method.upper() == "PUT":
                    response = client.put(
                        url, auth=self.auth, headers=headers, json=data
                    )
                elif method.upper() == "DELETE":
                    response = client.delete(url, auth=self.auth, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                logger.debug(
                    f"WooCommerce API request: {method} {endpoint}, Status: {response.status_code}"
                )
                print(f"WooCommerce API Response: {response.status_code}")

                if response.status_code >= 400:
                    logger.error(
                        f"WooCommerce API error: {response.status_code} - {response.text}"
                    )
                    print(
                        f"WooCommerce API Error: {response.status_code} - {response.text}"
                    )
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text,
                    }

                response_data = response.json() if response.content else None
                print(f"Response Data: {response_data}")

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response_data,
                }
        except:
            logger.error("Request failed")
            print("WooCommerce API Request failed")
            return {"success": False, "error": str("error woocommerce HEREEEEEEE")}

    def create_product(
        self,
        name: str,
        price: float,
        description: str = "",
        short_description: str = "",
        stock_quantity: int = 0,
        category_ids: List[int] = None,
        image_url: Optional[str] = None,
        technical_details: Optional[str] = None,
        woocommerce_product_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new product in WooCommerce
        """
        logger.info(f"Creating product in WooCommerce: {name}")

        # Prepare product data for WooCommerce
        product_data = {
            "name": name,
            "type": "simple",
            "regular_price": str(price),
            "description": description or f"Description for {name}",
            "short_description": short_description or f"Short description for {name}",
        }

        # Add stock information
        # if stock_quantity is not None:
        #     product_data["stock_quantity"] = stock_quantity
        #     product_data["manage_stock"] = True

        # Add categories if provided
        if category_ids:
            categories = []
            for cat_id in category_ids:
                categories.append({"id": cat_id})
            product_data["categories"] = categories

        # Add image if provided
        if image_url:
            product_data["images"] = [
                {
                    "src": image_url
                }
            ]
        else:
            # Add default placeholder image if available
            placeholder_img = os.getenv("DEFAULT_PRODUCT_IMAGE_URL")
            if placeholder_img:
                product_data["images"] = [{"src": placeholder_img}]

        # Add technical details as custom fields if provided
        # if technical_details:
        #     product_data["meta_data"] = [
        #         {
        #             "key": "_technical_details",
        #             "value": technical_details
        #         }
        #     ]

        # If woocommerce_product_id is provided, update existing product instead
        if woocommerce_product_id:
            return self.update_product(
                woocommerce_product_id,
                name,
                price,
                description,
                short_description,
                stock_quantity,
                category_ids,
                image_url,
                technical_details,
            )

        # Make API call to create product
        result = self._make_request("POST", "products", product_data)

        if result["success"]:
            product = result["data"]
            logger.info(f"Successfully created product in WooCommerce: {product['id']}")
            return {
                "success": True,
                "woocommerce_product_id": product["id"],
                "name": product["name"],
                "message": f"Product '{name}' successfully created in WooCommerce with ID {product['id']}",
            }
        else:
            logger.error(f"Failed to create product in WooCommerce: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "message": f"Failed to create product '{name}' in WooCommerce",
            }

    def update_product(
        self,
        woocommerce_product_id: int,
        name: str,
        price: float,
        description: str = "",
        short_description: str = "",
        stock_quantity: int = 0,
        category_ids: List[int] = None,
        image_url: Optional[str] = None,
        technical_details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing product in WooCommerce
        """
        logger.info(f"Updating product in WooCommerce: {woocommerce_product_id}")

        # Prepare update data
        update_data = {
            "name": name,
            "regular_price": str(price),
            "description": description or f"Description for {name}",
            "short_description": short_description or f"Short description for {name}",
        }

        # Add stock information
        if stock_quantity is not None:
            update_data["stock_quantity"] = stock_quantity
            update_data["manage_stock"] = True

        # Add categories if provided
        if category_ids:
            categories = []
            for cat_id in category_ids:
                categories.append({"id": cat_id})
            update_data["categories"] = categories

        # Add image if provided
        if image_url:
            update_data["images"] = [{"src": image_url}]

        # Add technical details as custom fields if provided
        if technical_details:
            update_data["meta_data"] = [
                {"key": "_technical_details", "value": technical_details}
            ]

        result = self._make_request(
            "PUT", f"products/{woocommerce_product_id}", update_data
        )

        if result["success"]:
            product = result["data"]
            logger.info(
                f"Successfully updated product in WooCommerce: {woocommerce_product_id}"
            )
            return {
                "success": True,
                "woocommerce_product_id": product["id"],
                "name": product["name"],
                "message": f"Product '{name}' successfully updated in WooCommerce",
            }
        else:
            logger.error(f"Failed to update product in WooCommerce: {result['error']}")
            return {
                "success": False,
                "woocommerce_product_id": woocommerce_product_id,
                "error": result["error"],
                "message": f"Failed to update product with ID {woocommerce_product_id} in WooCommerce",
            }

    def delete_product(self, woocommerce_product_id: int) -> Dict[str, Any]:
        """
        Delete a product from WooCommerce
        """
        logger.info(f"Deleting product from WooCommerce: {woocommerce_product_id}")

        result = self._make_request(
            "DELETE", f"products/{woocommerce_product_id}?force=true"
        )

        if result["success"]:
            logger.info(
                f"Successfully deleted product from WooCommerce: {woocommerce_product_id}"
            )
            return {
                "success": True,
                "woocommerce_product_id": woocommerce_product_id,
                "message": f"Product with ID {woocommerce_product_id} successfully deleted from WooCommerce",
            }
        else:
            logger.error(
                f"Failed to delete product from WooCommerce: {result['error']}"
            )
            return {
                "success": False,
                "woocommerce_product_id": woocommerce_product_id,
                "error": result["error"],
                "message": f"Failed to delete product with ID {woocommerce_product_id} from WooCommerce",
            }

    def sync_product_to_woocommerce(
        self,
        product_id: int,
        name: str,
        price: float,
        description: str = "",
        short_description: str = "",
        stock_quantity: int = 0,
        category_ids: List[int] = None,
        image_url: Optional[str] = None,
        technical_details: Optional[str] = None,
        woocommerce_product_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Synchronize a local product to WooCommerce (create or update)
        """
        if woocommerce_product_id:
            # Update existing product
            return self.update_product(
                woocommerce_product_id,
                name,
                price,
                description,
                short_description,
                stock_quantity,
                category_ids,
                image_url,
                technical_details,
            )
        else:
            # Create new product
            return self.create_product(
                name,
                price,
                description,
                short_description,
                stock_quantity,
                category_ids,
                image_url,
                technical_details,
            )

    def get_product(self, woocommerce_product_id: int) -> Dict[str, Any]:
        """
        Get a product from WooCommerce by its ID
        """
        logger.info(f"Fetching product from WooCommerce: {woocommerce_product_id}")

        result = self._make_request("GET", f"products/{woocommerce_product_id}")

        if result["success"]:
            return {"success": True, "data": result["data"]}
        else:
            logger.error(f"Failed to get product from WooCommerce: {result['error']}")
            return {"success": False, "error": result["error"]}

    def get_all_products(self) -> Dict[str, Any]:
        """
        Get all products from WooCommerce
        """
        logger.info("Fetching all products from WooCommerce")

        result = self._make_request("GET", "products")

        if result["success"]:
            return {"success": True, "data": result["data"]}
        else:
            logger.error(f"Failed to get products from WooCommerce: {result['error']}")
            return {"success": False, "error": result["error"]}

    def upload_image_to_imgur(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image to Imgur and return the URL
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            return {"success": False, "error": f"Image file does not exist: {image_path}"}

        # Read the image file and encode as base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Imgur API endpoint
        url = "https://api.imgur.com/3/image"

        # Get Imgur client ID from environment variables
        imgur_client_id = os.getenv("IMGUR_CLIENT_ID", "5a5b3e6064d2ab6")  # Default client ID for testing

        # Headers for Imgur API
        headers = {
            "Authorization": f"Client-ID {imgur_client_id}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Data for the request
        data = {
            "image": image_data,
            "type": "base64"
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)

            print(f"Imgur Upload Response: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    image_url = response_data["data"]["link"]
                    print(f"Imgur upload response data: {image_url}")
                    return {
                        "success": True,
                        "url": image_url
                    }
                else:
                    logger.error(f"Imgur upload failed: {response_data}")
                    print(f"Imgur upload failed: {response_data}")
                    return {
                        "success": False,
                        "error": f"Upload failed: {response_data.get('data', {}).get('error', 'Unknown error')}"
                    }
            elif response.status_code == 403:
                # This often happens with the default client ID due to rate limiting
                logger.warning("Imgur upload failed due to rate limiting or unauthorized client ID. This is expected with default client ID.")
                return {
                    "success": False,
                    "error": "Imgur upload failed - likely due to rate limiting or unauthorized client ID"
                }
            else:
                logger.error(f"Imgur upload failed: {response.status_code} - {response.text}")
                print(f"Imgur upload failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Upload failed: {response.text}",
                    "status_code": response.status_code
                }
        except requests.exceptions.Timeout:
            logger.error("Imgur upload timed out")
            return {
                "success": False,
                "error": "Imgur upload timed out"
            }
        except Exception as e:
            logger.error(f"Error uploading image to Imgur: {str(e)}")
            print(f"Error uploading image to Imgur: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def upload_image_to_woocommerce(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image to WordPress media library (WooCommerce uses WordPress) and return the URL
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            return {"success": False, "error": f"Image file does not exist: {image_path}"}

        # Read the image file
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Get the file's content type based on extension
        ext = os.path.splitext(image_path)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        content_type = content_types.get(ext, 'application/octet-stream')

        # Prepare the request to upload media to WordPress (the proper WooCommerce media endpoint)
        url = f"{self.store_url}/wp-json/wp/v2/media"

        # Headers for media upload
        headers = {
            "Content-Disposition": f"attachment; filename={os.path.basename(image_path)}",
            "Content-Type": content_type,
            "Authorization": f"Basic {base64.b64encode(f'{self.consumer_key}:{self.consumer_secret}'.encode()).decode()}"
        }

        try:
            with httpx.Client(http2=True, timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=headers,
                    content=image_data
                )

                print(f"WooCommerce Media Upload Response: {response.status_code}")

                if response.status_code in [200, 201]:
                    response_data = response.json()
                    print(f"Media upload response data: {response_data}")
                    return {
                        "success": True,
                        "url": response_data.get("source_url"),
                        "id": response_data.get("id")
                    }
                else:
                    logger.error(f"WooCommerce media upload failed: {response.status_code} - {response.text}")
                    print(f"WooCommerce media upload failed: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Upload failed: {response.text}",
                        "status_code": response.status_code
                    }
        except Exception as e:
            logger.error(f"Error uploading media to WooCommerce: {str(e)}")
            print(f"Error uploading media to WooCommerce: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def sync_local_product_to_woocommerce(
        self,
        local_product: Dict[str, Any],
        woocommerce_product_id: Optional[int] = None,
        upload_folder_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synchronize a local product to WooCommerce with mapping from local schema to WooCommerce
        """
        try:
            # Map local product fields to WooCommerce fields
            name = local_product.get("name", "")
            price = float(local_product.get("price", 0.0))
            description = local_product.get("description", "")
            short_description = local_product.get(
                "short_description", ""
            ) or local_product.get("description", "")
            stock_quantity = local_product.get("stock_quantity", 0)
            technical_details = local_product.get("technical_details")

            # Handle categories - try to map local category to WooCommerce category IDs
            category_ids = []
            local_category = local_product.get("category")
            if local_category:
                # This would require a mapping function or lookup table
                # For now, we'll skip category mapping and let the caller specify category IDs
                pass

            # Handle image - upload local image to external image hosting if needed
            image_url = None
            photo_path = local_product.get("photo")
            if photo_path:
                # Check if photo_path is a local file path by checking if it has a valid extension
                # and doesn't start with http (indicating it's already a URL)
                if not photo_path.startswith(('http://', 'https://')):
                    # It's likely a local file path, construct the full path
                    if upload_folder_path is None:
                        # Import app to get upload folder as fallback
                        try:
                            from app import app
                            upload_folder_path = app.config['UPLOAD_FOLDER']
                        except ImportError:
                            # Default fallback path
                            upload_folder_path = 'static/uploads/products'

                    full_photo_path = os.path.join(upload_folder_path, photo_path)

                    if os.path.exists(full_photo_path):
                        # Local file exists, try to upload to WooCommerce media library first
                        # upload_result = self.upload_image_to_woocommerce(full_photo_path)
                        if False:
                            # image_url = upload_result["url"]
                            print(f"Successfully uploaded image to WooCommerce: {image_url}")
                        else:
                            # logger.error(f"Failed to upload image to WooCommerce: {upload_result['error']}")
                            # Try to upload to Imgur as primary fallback
                            print("Trying to upload to Imgur as fallback...")
                            imgur_result = self.upload_image_to_imgur(full_photo_path)
                            if imgur_result["success"]:
                                image_url = imgur_result["url"]
                                print(f"Successfully uploaded image to Imgur: {image_url}")
                            else:
                                logger.error(f"Failed to upload image to Imgur: {imgur_result['error']}")
                                print(f"Imgur upload failed, trying to create public URL...")
                                # As a fallback, try to construct a public URL assuming images are served from the web server
                                # This requires that the image files are accessible from the web
                                try:
                                    from app import app
                                    # If the app is running and images are in the static folder, they might be accessible via web URL
                                    base_url = os.getenv("BASE_URL", "https://yourdomain.com")  # This should be configured
                                    if base_url != "https://yourdomain.com":  # Only try if base_url was actually configured
                                        image_url = f"{base_url}/static/uploads/products/{photo_path}"
                                        print(f"Using public URL for image (fallback): {image_url}")
                                    else:
                                        # If no real domain is configured, use static image as fallback
                                        image_url = "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_back.jpg"
                                        logger.warning(f"No domain configured, using static image as fallback.")
                                except:
                                    # If all above fail, use the static URL as last resort
                                    image_url = "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_back.jpg"
                                    logger.warning(f"Could not upload image to any service. Using fallback static image.")
                    else:
                        # If the file doesn't exist locally, assume it's already a URL
                        logger.warning(f"Local photo file does not exist: {full_photo_path}, treating as URL")
                        image_url = photo_path
                else:
                    # It's already a URL
                    image_url = photo_path

            return self.sync_product_to_woocommerce(
                product_id=local_product.get("id", 0),
                name=name,
                price=price,
                description=description,
                short_description=short_description,
                stock_quantity=stock_quantity,
                category_ids=category_ids,
                image_url=image_url,
                technical_details=technical_details,
                woocommerce_product_id=woocommerce_product_id,
            )
        except Exception as e:
            logger.error(f"Error syncing local product to WooCommerce: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error syncing local product to WooCommerce",
            }


# Global instance for the WooCommerce sync
woocommerce_sync = WooCommerceProductSync()


def sync_product_to_woocommerce(
    product_data: Dict[str, Any], woocommerce_product_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Helper function to synchronize a local product to WooCommerce
    """
    try:
        # Create appropriate category_ids from local data if needed
        category_ids = product_data.get("category_ids", [])
        if not category_ids and product_data.get("category"):
            # Simple mapping - in real implementation you might look up category IDs
            # For now, we'll just ignore category if not provided as IDs
            logger.warning(
                "Category name provided but no category IDs. Category not mapped."
            )

        # Get the upload folder path from the app configuration if possible
        upload_folder_path = None
        try:
            from app import app
            upload_folder_path = app.config['UPLOAD_FOLDER']
        except ImportError:
            # Default location where images are stored
            upload_folder_path = 'static/uploads/products'

        return woocommerce_sync.sync_local_product_to_woocommerce(
            local_product=product_data,
            woocommerce_product_id=woocommerce_product_id,
            upload_folder_path=upload_folder_path
        )
    except Exception as e:
        logger.error(f"Error syncing product to WooCommerce: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error syncing product to WooCommerce",
        }


def delete_product_from_woocommerce(woocommerce_product_id: int) -> Dict[str, Any]:
    """
    Helper function to delete a product from WooCommerce
    """
    try:
        return woocommerce_sync.delete_product(woocommerce_product_id)
    except Exception as e:
        logger.error(f"Error deleting product from WooCommerce: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error deleting product from WooCommerce",
        }


def get_woocommerce_product(woocommerce_product_id: int) -> Dict[str, Any]:
    """
    Helper function to get a product from WooCommerce
    """
    try:
        return woocommerce_sync.get_product(woocommerce_product_id)
    except Exception as e:
        logger.error(f"Error getting product from WooCommerce: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error getting product from WooCommerce",
        }


def sync_all_products_to_woocommerce(
    local_products: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Helper function to sync all local products to WooCommerce
    """
    try:
        results = []
        for product in local_products:
            result = sync_product_to_woocommerce(product)
            results.append(result)

        successful_syncs = sum(1 for r in results if r.get("success"))
        failed_syncs = len(results) - successful_syncs

        return {
            "success": True,
            "total_products": len(local_products),
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error syncing all products to WooCommerce: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error syncing all products to WooCommerce",
        }
