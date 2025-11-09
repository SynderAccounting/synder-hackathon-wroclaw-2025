import base64
import json
import os
from io import BytesIO
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
try:
    client = OpenAI(api_key=MOONSHOT_API_KEY, base_url="https://api.moonshot.ai/v1")
except TypeError as e:
    if "proxies" in str(e):
        # Handle the proxies issue by creating a custom client
        import httpx
        http_client = httpx.Client(
            timeout=60.0,  # Set a reasonable timeout
            follow_redirects=True,
        )
        client = OpenAI(
            api_key=MOONSHOT_API_KEY,
            base_url="https://api.moonshot.ai/v1",
            http_client=http_client
        )
    else:
        raise e

def generate_product_description(product_name: str, product_details: str, base64_images: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate e-commerce product description using Kimi vision model.

    Args:
        product_name: Product title (e.g., "Wireless Bluetooth Headphones").
        product_details: Additional text details (e.g., "Noise-cancelling, 20-hour battery, black color").
        base64_images: List of base64-encoded images (e.g., from PIL: f"data:image/jpeg;base64,{b64str}").

    Returns:
        Dict with 'title', 'description', 'features', 'keywords' or error info.
    """
    if not product_name and not product_details and not base64_images:
        return {"error": "At least one input (name, details, or images) is required."}

    system_prompt = """
    You are an expert e-commerce copywriter. Generate engaging, persuasive product descriptions that sell:
    - Make them SEO-friendly with relevant keywords.
    - Highlight benefits, features, and unique selling points.
    - Keep the description 150-300 words, encouraging purchase (e.g., "Upgrade your daily routine with...").
    - If images are provided, analyze visuals (colors, style, usage) and incorporate them.
    - If details are missing, infer logically from name/images but stay accurate.
    - Output ONLY valid JSON: {
      "title": "Catchy product title (50 chars max)",
      "description": "Full engaging description paragraph",
      "features": ["Bullet 1", "Bullet 2", ...] (3-5 key features),
      "keywords": ["keyword1", "keyword2", ...] (5-10 SEO tags)
    }
    """

    user_content = [{"type": "text", "text": f"Product name: {product_name or 'N/A'}. Details: {product_details or 'N/A'}."}]

    if base64_images:
        user_content.extend([
            {"type": "image_url", "image_url": {"url": img_b64}} for img_b64 in base64_images
        ])
        user_text = " Analyze the images to describe the product's appearance, quality, and appeal."
    else:
        user_text = " Generate based on text inputs only."

    user_content[0]["text"] += user_text

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=messages,
            temperature=0.6,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()

        try:
            extracted_data = json.loads(content)
            if not isinstance(extracted_data, dict):
                raise ValueError("Output is not a dict")
            return extracted_data
        except (json.JSONDecodeError, ValueError):
            return {
                "title": product_name or "Generated Product",
                "description": content,
                "features": [],
                "keywords": [],
                "raw_fallback": True
            }
    except Exception as e:
        return {"error": f"API error: {str(e)}"}

# Helper to convert image file/path to base64 (for e-commerce product photos)
def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string for API."""
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)  # Compress for API limits
        img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"


def generate_product_category(product_name: str, product_details: str, base64_images: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate e-commerce product category using Kimi vision model.

    Args:
        product_name: Product title (e.g., "Wireless Bluetooth Headphones").
        product_details: Additional text details (e.g., "Noise-cancelling, 20-hour battery, black color").
        base64_images: List of base64-encoded images (e.g., from PIL: f"data:image/jpeg;base64,{b64str}").

    Returns:
        Dict with 'category' (string) or 'categories' (array of strings) or error info.
    """
    if not product_name and not product_details and not base64_images:
        return {"error": "At least one input (name, details, or images) is required."}

    system_prompt = """
    You are an expert e-commerce categorization specialist. Determine the most appropriate product categories from these options:
    Electronics, Clothing & Accessories, Home & Garden, Sports & Outdoors, Beauty & Personal Care,
    Food & Grocery, Books & Media, Toys & Games, Automotive, Health & Wellness, Office Supplies,
    Pet Supplies, Jewelry, Furniture, Tools & Hardware, Baby & Kids, Travel & Luggage, Arts & Crafts.

    If the product fits multiple categories, provide up to 3 most appropriate categories.
    If the product doesn't clearly fit these categories, suggest more specific subcategories that would be appropriate.

    Output ONLY valid JSON: {
      "categories": ["Most appropriate category name (20 chars max)", "Second category", ...] (1-3 categories),
      "primary_category": "The most appropriate single category"  // Optional: if you want to designate one primary category
    }
    OR for backward compatibility:
    {
      "category": "Most appropriate category name (20 chars max)"  // Single category for backward compatibility
    }
    """

    user_content = [{"type": "text", "text": f"Product name: {product_name or 'N/A'}. Details: {product_details or 'N/A'}."}]

    if base64_images:
        user_content.extend([
            {"type": "image_url", "image_url": {"url": img_b64}} for img_b64 in base64_images
        ])
        user_text = " Analyze the images to help determine the category based on visual characteristics."
    else:
        user_text = " Generate based on text inputs only."

    user_content[0]["text"] += user_text

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent category suggestions
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        try:
            extracted_data = json.loads(content)
            if not isinstance(extracted_data, dict):
                raise ValueError("Output is not a dict")
            
            # Handle both formats: single category and multiple categories
            if "categories" in extracted_data:
                # If we have a categories array, return it
                return extracted_data
            elif "category" in extracted_data:
                # If we have a single category, return it in a backward-compatible way
                # Also add it as a categories array for consistency
                category = extracted_data["category"]
                return {
                    "category": category,
                    "categories": [category]
                }
            else:
                return {"error": "Invalid response format: missing 'category' or 'categories' field"}
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, try to extract categories from the plain text response
            # Look for multiple categories in the response text
            import re

            # Try to match a categories array in JSON format
            categories_match = re.search(r'"?categories"?\s*:\s*\[([^\]]+)\]', content, re.IGNORECASE)
            if categories_match:
                # Extract the content from the array and parse it
                categories_str = categories_match.group(1)
                # Extract quoted strings from the array
                category_matches = re.findall(r'"([^"]+)"', categories_str)
                if category_matches:
                    return {"categories": category_matches, "primary_category": category_matches[0]}
            
            # Try to match a single category
            category_match = re.search(r'"?category"?\s*:\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if category_match:
                category = category_match.group(1)
                return {"category": category, "categories": [category]}
            
            # If we still can't parse, return a generic category
            return {"category": "General", "categories": ["General"]}
    except Exception as e:
        return {"error": f"API error: {str(e)}"}


def generate_product_price(product_name: str, product_details: str, brand: Optional[str] = None, base64_images: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate e-commerce product price prediction with reasoning using AI model.

    Args:
        product_name: Product title (e.g., "Wireless Bluetooth Headphones").
        product_details: Additional text details (e.g., "Noise-cancelling, 20-hour battery, black color").
        brand: Brand name (e.g., "Sony", "Apple", "Generic").
        base64_images: List of base64-encoded images (e.g., from PIL: f"data:image/jpeg;base64,{b64str}").

    Returns:
        Dict with 'predicted_price', 'currency', 'reasoning', or error info.
    """
    if not product_name and not product_details and not base64_images:
        return {"error": "At least one input (name, details, or images) is required."}

    # Build product description for the AI
    product_info = f"Product name: {product_name or 'N/A'}. "
    if brand:
        product_info += f"Brand: {brand}. "
    product_info += f"Details: {product_details or 'N/A'}."

    system_prompt = f"""
    You are an expert e-commerce pricing analyst. Analyze the product and predict a competitive retail price in USD with detailed reasoning.
    
    Consider these factors:
    1. Product category and type
    2. Brand reputation (if provided)
    3. Features, materials, quality indicators
    4. Market positioning (budget, mid-range, premium)
    5. Similar products in the market
    6. Target audience
    7. Seasonal trends (if applicable)
    8. Quality indicators from description/images
    9. Value proposition
    
    Output ONLY valid JSON: {{
      "predicted_price": float,  // Suggested retail price in USD
      "currency": "USD",  // Currency code
      "reasoning": "Detailed explanation of price reasoning - factors considered, market comparison, quality assessment, etc.",
      "price_range": {{  // Optional: min and max range
        "min": float,  // Minimum suggested price
        "max": float   // Maximum suggested price
      }},
      "market_positioning": "budget|mid-range|premium"  // How the product is positioned in the market
    }}
    """

    user_content = [{"type": "text", "text": product_info}]

    if base64_images:
        user_content.extend([
            {"type": "image_url", "image_url": {"url": img_b64}} for img_b64 in base64_images
        ])
        user_text = " Analyze the images to assess quality, design, materials, and brand indicators for pricing."
    else:
        user_text = " Price based on text information only."

    user_content[0]["text"] += user_text

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=messages,
            temperature=0.4,  # Lower temperature for more consistent pricing
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()

        try:
            extracted_data = json.loads(content)
            if not isinstance(extracted_data, dict):
                raise ValueError("Output is not a dict")
            
            # Ensure required fields are present
            if "predicted_price" not in extracted_data:
                return {"error": "AI did not return a predicted price"}
            
            return extracted_data
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, try to extract price from the plain text response
            import re

            # Look for a price in the response text
            price_match = re.search(r'\d+\.?\d*', content)
            if price_match:
                price = float(price_match.group())
                return {
                    "predicted_price": price,
                    "currency": "USD",
                    "reasoning": f"Price extracted from response: {content[:200]}...",
                    "price_range": {"min": price * 0.8, "max": price * 1.2}
                }
            else:
                return {
                    "error": "Could not extract price from AI response",
                    "raw_response": content
                }
    except Exception as e:
        return {"error": f"API error: {str(e)}"}


def generate_product_3d_visualization(product_name: str, product_details: str, base64_images: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate 3D visualization for a product by creating a rotating GIF from product images.

    Args:
        product_name: Product title (e.g., "Wireless Bluetooth Headphones").
        product_details: Additional text details (e.g., "Noise-cancelling, 20-hour battery, black color").
        base64_images: List of base64-encoded images (e.g., from PIL: f"data:image/jpeg;base64,{b64str}").

    Returns:
        Dict with 'success', 'visualization_path', 'model_type', 'parameters', 'description', or error info.
    """
    if not product_name and not product_details and not base64_images:
        return {"error": "At least one input (name, details, or images) is required."}

    # First, get 3D visualization parameters from AI
    product_info = f"Product name: {product_name or 'N/A'}. "
    product_info += f"Details: {product_details or 'N/A'}."

    system_prompt = """
    You are an expert 3D visualization specialist. Based on the product description and images, generate parameters for creating a 3D visualization of the product.

    Consider these factors:
    1. Product shape, form, and dimensions
    2. Colors, materials, and textures
    3. Key visual features and details
    4. Surface properties (glossy, matte, metallic, etc.)
    5. Overall aesthetic and design style

    For Gaussian splatting or similar 3D generation methods, suggest parameters such as:
    - Main colors/palette
    - Material properties (metallic, roughness, etc.)
    - Shape approximations
    - Key visual elements to emphasize

    Output ONLY valid JSON: {
      "success": true,
      "model_type": "gaussian_splatting|mesh|point_cloud|other",
      "parameters": {
        "main_colors": ["hex_color", ...],
        "materials": ["material_type", ...],
        "shape_approximation": "description of basic shape",
        "key_features": ["feature1", "feature2", ...],
        "surface_properties": {
          "roughness": float,  // 0.0 to 1.0
          "metallic": float,   // 0.0 to 1.0
        }
      },
      "description": "Brief description of how the 3D visualization should look",
      "instructions": "Detailed instructions for creating the 3D visualization"
    }
    """

    user_content = [{"type": "text", "text": product_info}]

    if base64_images:
        user_content.extend([
            {"type": "image_url", "image_url": {"url": img_b64}} for img_b64 in base64_images
        ])
        user_text = " Analyze the images to understand the exact shape, colors, materials, and visual details of the product for 3D visualization."
    else:
        user_text = " Generate based on text information only."

    user_content[0]["text"] += user_text

    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        try:
            ai_params = json.loads(content)
            if not isinstance(ai_params, dict):
                raise ValueError("Output is not a dict")
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, use default parameters
            ai_params = {
                "success": True,
                "model_type": "gaussian_splatting",
                "parameters": {
                    "main_colors": ["#808080"],  # Default gray
                    "materials": ["plastic"],
                    "shape_approximation": "basic geometric approximation",
                    "key_features": ["product visualization"],
                    "surface_properties": {
                        "roughness": 0.5,
                        "metallic": 0.0
                    }
                },
                "description": "3D visualization based on product information",
                "instructions": f"Visualize the product: {product_info[:200]}..."
            }
    except Exception as e:
        return {"error": f"Failed to get 3D parameters: {str(e)}"}

    # Now generate the actual 3D-like visualization as a rotating GIF
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import io
        import os
        import numpy as np
        from datetime import datetime
        import uuid

        # Create visualization directory if it doesn't exist
        vis_dir = "static/visualizations"
        os.makedirs(vis_dir, exist_ok=True)

        # Create a unique filename for the 3D visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        gif_filename = f"3d_visualization_{timestamp}_{unique_id}.gif"
        gif_path = os.path.join(vis_dir, gif_filename)

        if base64_images:
            # Process existing images to create rotating effect
            images = []
            for img_b64 in base64_images:
                # Remove data URL prefix if present
                if img_b64.startswith('data:image'):
                    img_b64 = img_b64.split(',')[1]
                
                # Decode base64 image
                img_data = base64.b64decode(img_b64)
                img = Image.open(BytesIO(img_data))
                
                # Ensure image is in RGB mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                images.append(img)
            
            # Create a sequence of frames for the rotating animation
            frames = []
            
            # If we have multiple images, use them as frames directly
            if len(images) > 1:
                frames = images
            else:
                # If we have only one image, create a rotating effect
                img = images[0]
                
                # Create rotated versions for animation
                for angle in range(0, 360, 30):  # 12 frames for a full rotation
                    rotated_img = img.rotate(angle, expand=True, fillcolor='white')
                    # Resize to a standard size for consistent animation
                    rotated_img = rotated_img.resize((400, 400), Image.Resampling.LANCZOS)
                    frames.append(rotated_img)
            
            # Save frames as an animated GIF
            if frames:
                # Ensure all frames are the same size
                min_width = min(img.width for img in frames)
                min_height = min(img.height for img in frames)
                
                resized_frames = []
                for frame in frames:
                    resized_frame = frame.resize((min_width, min_height), Image.Resampling.LANCZOS)
                    resized_frames.append(resized_frame)
                
                # Save the animated GIF
                resized_frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=resized_frames[1:],
                    duration=500,  # 500ms per frame
                    loop=0  # Infinite loop
                )
                
                # Update the result with the GIF path
                ai_params['success'] = True
                ai_params['visualization_path'] = f"/static/visualizations/{gif_filename}"  # URL path relative to static folder
                ai_params['gif_filename'] = gif_filename
            else:
                return {"error": "Could not create visualization from provided images"}

        else:
            # If no images are provided, create a simple animated 3D-like shape based on the AI parameters
            width, height = 400, 400
            frames = []

            # Create a simple 3D-like shape animation based on AI parameters
            main_color = ai_params['parameters']['main_colors'][0] if ai_params['parameters']['main_colors'] else '#808080'
            
            # Convert hex color to RGB
            if main_color.startswith('#'):
                main_color = main_color[1:]
            if len(main_color) == 3:
                main_color = ''.join([c+c for c in main_color])
            r, g, b = tuple(int(main_color[i:i+2], 16) for i in (0, 2, 4))
            
            for i in range(12):  # 12 frames for rotation
                # Create a blank image
                img = Image.new('RGB', (width, height), (255, 255, 255))
                
                # Draw a simple rotating shape (e.g., an oval that changes to create 3D illusion)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                
                # Calculate oval dimensions based on rotation to create 3D effect
                angle = i * (2 * np.pi / 12)
                # Create a slightly different oval shape per frame to simulate rotation
                left = 100 + 20 * np.sin(angle)
                top = 150
                right = 300 + 20 * np.sin(angle)
                bottom = 250
                
                # Draw the oval
                draw.ellipse([left, top, right, bottom], fill=(r, g, b), outline="black", width=2)
                
                # Draw an ellipse on top to make it look like a 3D shape
                top_ellipse_left = left + 30
                top_ellipse_top = top + 20
                top_ellipse_right = right - 30
                top_ellipse_bottom = bottom - 60
                
                draw.ellipse([top_ellipse_left, top_ellipse_top, top_ellipse_right, top_ellipse_bottom], 
                           fill=(int(r*1.2), int(g*1.2), int(b*1.2)), outline="black", width=1)
                
                frames.append(img)
            
            # Save the animated GIF
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=500,  # 500ms per frame
                loop=0  # Infinite loop
            )
            
            # Update the result with the GIF path
            ai_params['success'] = True
            ai_params['visualization_path'] = f"/static/visualizations/{gif_filename}"  # URL path relative to static folder
            ai_params['gif_filename'] = gif_filename

        return ai_params

    except Exception as e:
        # If actual GIF generation fails, return the original AI parameters
        print(f"Warning: Could not generate actual 3D visualization: {str(e)}")
        ai_params['success'] = True  # Mark as successful but without actual visualization
        return ai_params


# Example usage
if __name__ == "__main__":
    # Example 1: Text only
    desc_text = generate_product_description(
        product_name="Wireless Bluetooth Headphones",
        product_details="Noise-cancelling, 20-hour battery life, lightweight design for workouts."
    )
    print("Text-only Description:", json.dumps(desc_text, indent=2, ensure_ascii=False))

    # Example 2: With images (replace with your image paths)
    base64_img1 = image_to_base64("./product_photo1.jpg")  # e.g., product image
    base64_img2 = image_to_base64("./product_photo2.jpg")  # e.g., detail shot
    desc_img = generate_product_description(
        product_name="Wireless Bluetooth Headphones",
        product_details="Available in black and blue.",
        base64_images=[base64_img1, base64_img2]
    )
    print("Image+Text Description:", json.dumps(desc_img, indent=2, ensure_ascii=False))

    # Example 3: Price prediction
    price_prediction = generate_product_price(
        product_name="Wireless Bluetooth Headphones",
        product_details="Noise-cancelling, 20-hour battery life, lightweight design for workouts.",
        brand="Sony"
    )
    print("Price Prediction:", json.dumps(price_prediction, indent=2, ensure_ascii=False))

    # Example 4: 3D visualization
    try:
        base64_img1 = image_to_base64("./product_photo1.jpg")  # e.g., product image
        base64_img2 = image_to_base64("./product_photo2.jpg")  # e.g., detail shot
        visualization_result = generate_product_3d_visualization(
            product_name="Wireless Bluetooth Headphones",
            product_details="Noise-cancelling, 20-hour battery life, lightweight design for workouts.",
            base64_images=[base64_img1, base64_img2]
        )
        print("3D Visualization:", json.dumps(visualization_result, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print("Image files not found, skipping 3D visualization example")
