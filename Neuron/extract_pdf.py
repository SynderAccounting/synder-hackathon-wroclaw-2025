import base64
import os
from io import BytesIO

from openai import OpenAI
from pdf2image import convert_from_path
from PIL import Image

# Set up the client (using your sample)
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

def pdf_to_base64_images(pdf_path):
    """Convert PDF pages to list of base64-encoded JPEG images."""
    images = convert_from_path(pdf_path, dpi=200)  # Higher DPI for scanned PDFs
    base64_images = []
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        base64_images.append(f"data:image/jpeg;base64,{img_str}")
    return base64_images

def extract_invoice_data(pdf_path):
    """Extract invoice data using Kimi vision model."""
    base64_images = pdf_to_base64_images(pdf_path)
    
    # Prepare messages with images and prompt
    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting structured data from invoice images. Output only valid JSON with keys: invoice_number, date, due_date, total_amount, vendor_name, customer_name, line_items (list of dicts with description, quantity, unit_price, total)."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the invoice details from these images. If multi-page, consider all pages."},
                *[
                    {
                        "type": "image_url",
                        "image_url": {"url": img_base64}
                    }
                    for img_base64 in base64_images
                ]
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model="moonshot-v1-8k-vision-preview",  # Corrected to vision-enabled model
        messages=messages,
        temperature=0.1,  # Low temperature for structured output
        max_tokens=1000
    )
    
    # Parse and return the JSON response
    content = response.choices[0].message.content
    try:
        import json
        extracted_data = json.loads(content)
        return extracted_data
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw": content}

# Example usage
if __name__ == "__main__":
    pdf_file = "./invoice.pdf"  # Replace with your PDF path
    data = extract_invoice_data(pdf_file)
    print(data)

