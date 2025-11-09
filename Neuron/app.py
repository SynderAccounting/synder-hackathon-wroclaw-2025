import contextlib
import json
import os
import pickle
import smtplib
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import requests
from flask import (Flask, jsonify, make_response, redirect, render_template,
                   render_template_string, request, url_for)
from sklearn.preprocessing import LabelEncoder
from weasyprint import HTML
from werkzeug.utils import secure_filename

# Import knowledge base
from knowledge_base import get_knowledge_base
# Import Shopify integration
from shopify_integration import (delete_product_from_shopify,
                                 sync_product_to_shopify)
# Import WooCommerce integration
from woocommerce_integration import (delete_product_from_woocommerce,
                                     sync_product_to_woocommerce)

WOOCOMMERCE_ENABLED = True

# Try to import weasyprint, but make it optional for tracking functionality
try:
    from weasyprint import HTML
except ImportError:
    HTML = None
    print("Warning: weasyprint not installed. Invoice PDF generation will be disabled.")

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = 'retail_crms.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/products'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Supplier/Company configuration for invoices
app.config['SUPPLIER_NAME'] = 'Your Company Name'
app.config['SUPPLIER_ADDRESS'] = 'ul. Example Street 123\n00-000 Warsaw, Poland'
app.config['SUPPLIER_NIP'] = '1234567890'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create visualizations folder if it doesn't exist
os.makedirs('static/visualizations', exist_ok=True)

# ==================== MOONSHOT API (KIMI2) CONFIGURATION ====================
# Initialize Moonshot API client for AI-powered chatbot
moonshot_available = False
moonshot_client = None

try:
    from openai import OpenAI

    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
    if MOONSHOT_API_KEY:
        try:
            moonshot_client = OpenAI(api_key=MOONSHOT_API_KEY, base_url="https://api.moonshot.ai/v1")
            moonshot_available = True
            print("Moonshot API (Kimi2) initialized successfully")
        except TypeError as e:
            if "proxies" in str(e):
                # Handle the proxies issue by creating a custom client
                import httpx
                http_client = httpx.Client(
                    timeout=60.0,
                    follow_redirects=True,
                )
                moonshot_client = OpenAI(
                    api_key=MOONSHOT_API_KEY,
                    base_url="https://api.moonshot.ai/v1",
                    http_client=http_client
                )
                moonshot_available = True
                print("Moonshot API (Kimi2) initialized successfully with custom client")
            else:
                raise e
    else:
        print("Warning: MOONSHOT_API_KEY not found in environment variables. AI chatbot will use fallback pattern matching.")
except Exception as e:
    print(f"Warning: Could not initialize Moonshot API: {str(e)}. AI chatbot will use fallback pattern matching.")
    moonshot_available = False

# ==================== VAT RATES DATA ====================
# Polish VAT rates based on regulations
VAT_RATES = {
    'standard': {'rate': 0.23, 'label': 'Standard rate (23%)'},
    'reduced_8': {'rate': 0.08, 'label': 'Reduced rate (8%) - certain food products, newspapers, healthcare products, etc.'},
    'reduced_5': {'rate': 0.05, 'label': 'Reduced rate (5%) - basic foods, children products, books, etc.'},
    'reduced_0': {'rate': 0.0, 'label': 'Reduced rate (0%) - exports, intra-EU supplies, etc.'},
    'parking': {'rate': 0.04, 'label': 'Parking rate (4%) - taxi operation services'}
}

# ==================== ML MODEL CONFIGURATION ====================
MODELS_PATH = 'models'
loaded_models = {}
historical_data = None

# Price prediction model
loaded_price_model = None
loaded_feature_cols = None
loaded_label_encoders = None

def load_historical_data():
    """Load historical Rossmann data for feature generation"""
    global historical_data
    try:
        train = pd.read_csv('rossmann_data/train.csv', parse_dates=['Date'])
        store = pd.read_csv('rossmann_data/store.csv')
        historical_data = train.merge(store, on='Store', how='left')

        # Preprocessing
        historical_data['CompetitionDistance'].fillna(historical_data['CompetitionDistance'].median(), inplace=True)
        historical_data = historical_data.sort_values(['Store', 'Date']).reset_index(drop=True)

        print(f"[OK] Loaded historical data: {len(historical_data):,} records")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load historical data: {e}")
        return False

def load_ml_models():
    """Load all trained ML models at startup"""
    global loaded_models

    model_files = [
        'Sales_day_model.pkl',
        'Sales_week_model.pkl',
        'Sales_month_model.pkl',
        'Customers_day_model.pkl',
        'Customers_week_model.pkl',
        'Customers_month_model.pkl'
    ]

    for model_file in model_files:
        model_path = os.path.join(MODELS_PATH, model_file)
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model_key = model_file.replace('_model.pkl', '')
                    loaded_models[model_key] = pickle.load(f)
                print(f"[OK] Loaded model: {model_key}")
            except Exception as e:
                print(f"[ERROR] Failed to load {model_file}: {e}")
        else:
            print(f"[ERROR] Model file not found: {model_path}")

    return len(loaded_models) > 0

def load_price_model():
    """Load pretrained price prediction model at startup"""
    global loaded_price_model, loaded_feature_cols, loaded_label_encoders

    try:
        loaded_price_model = joblib.load("product_model/retail_price_xgboost_model.pkl")
        loaded_feature_cols = joblib.load("product_model/model_feature_columns.pkl")
        loaded_label_encoders = joblib.load("product_model/categorical_label_encoders.pkl")
        print("Loaded price prediction model, feature columns, and label encoders")
        return True
    except Exception as e:
        print(f"Failed to load price prediction model: {e}")
        # Set default values to avoid errors
        loaded_price_model = None
        loaded_feature_cols = None
        loaded_label_encoders = None
        return False

# Load historical data and models at startup
load_historical_data()

if os.path.exists(MODELS_PATH):
    models_loaded = load_ml_models()
    if models_loaded:
        print(f"Successfully loaded {len(loaded_models)} prediction models")
    else:
        print("Warning: No models could be loaded")
else:
    print(f"Warning: Models directory '{MODELS_PATH}' not found")

# Load price prediction model
price_model_loaded = load_price_model()
if not price_model_loaded:
    print("Warning: Price prediction model could not be loaded")

def get_store_historical_features(store_id, target='Sales', context_window=30):
    """Get deterministic historical features for a store based on actual data"""
    if historical_data is None:
        return None

    # Get data for this store
    store_data = historical_data[historical_data['Store'] == store_id].copy()

    if len(store_data) == 0:
        return None

    # Get the most recent records (last context_window days)
    store_data = store_data.sort_values('Date', ascending=False).head(context_window)

    # Calculate aggregate statistics from historical data
    features = {}

    # Use actual historical values for lag features
    target_values = store_data[target].values

    # Lag features (using actual historical values)
    if len(target_values) > 0:
        features[f'{target}_lag_1'] = target_values[0] if len(target_values) > 0 else 0
        features[f'{target}_lag_7'] = target_values[6] if len(target_values) > 6 else target_values[-1]
        features[f'{target}_lag_14'] = target_values[13] if len(target_values) > 13 else target_values[-1]

    # Rolling statistics (calculated from actual data)
    features[f'{target}_rolling_mean_7'] = np.mean(target_values[:7]) if len(target_values) > 0 else 0
    features[f'{target}_rolling_mean_14'] = np.mean(target_values[:14]) if len(target_values) > 0 else 0

    return features

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def suggest_vat_rate(product_name, product_description, category):
    """
    Suggest appropriate VAT rate based on product information
    Priority: 0% > 5% > 8% > standard
    """
    # Convert inputs to lowercase for matching
    name_lower = (product_name or '').lower()
    desc_lower = (product_description or '').lower()
    cat_lower = (category or '').lower()

    # Combine all text for comprehensive matching
    full_text = f"{name_lower} {desc_lower} {cat_lower}"

    # Check for products that qualify for 0% VAT rate first (highest priority)
    zero_rate_keywords = [
        'export', 'exported', 'exportation', 'intra-eu', 'intra european', 'tax free',
        'tourist', 'free zone', 'customs warehouse', 'international transport',
        'vessel', 'ship', 'air transport', 'aircraft', 'air carrier',
        'nato', 'diplomatic', 'international organization'
    ]

    if any(keyword in full_text for keyword in zero_rate_keywords):
        return VAT_RATES['reduced_0']['rate']

    # Check for products that qualify for 8% VAT rate (newspapers, healthcare, etc.) - before 5% to handle priority
    eight_percent_keywords = [
        'sugar', 'spice', 'processed food', 'preserved food', 'newspaper', 'periodical', 'e-publication',
        'animal', 'plant', 'seed', 'fertilizer', 'feeding stuff', 'veterinary', 'pharmaceutical',
        'medical device', 'disinfectant', 'healthcare', 'blind', 'culture', 'sport', 'recreation',
        'theater', 'theatre', 'circus', 'amusement', 'museum', 'zoo', 'cinema', 'sporting',
        'library', 'water supply', 'street cleaning', 'refuse', 'waste', 'funeral', 'transport',
        'passenger', 'hotel', 'accommodation', 'food serving', 'beverage', 'canteen', 'cafeteria',
        'hairdressing', 'footwear repair', 'leather repair', 'clothing repair', 'clothing alteration', 'bicycle repair',
        'taxi', 'parking'
    ]

    # Check specifically for newspaper/periodical that should get 8% (not 5%)
    # This handles cases where both 5% and 8% keywords are present
    newspaper_words = ['newspaper', 'periodical', 'e-publication']
    if any(word in full_text for word in newspaper_words):
        # Check if it's not a regional/local periodical (which gets 5%)
        if any(word in full_text for word in ['regional', 'local']):
            # Regional/local periodicals get 5% VAT
            return VAT_RATES['reduced_5']['rate']
        else:
            # Regular newspapers/periodicals get 8% VAT
            return VAT_RATES['reduced_8']['rate']

    # Check for taxi/transport services that get parking rate (4%)
    if 'taxi' in full_text or 'transport' in full_text.lower():
        for keyword in ['taxi', 'operation', 'service']:
            if keyword in full_text:
                return VAT_RATES['parking']['rate']

    # If we reach here, check for 8% keywords that aren't newspaper-related
    if any(keyword in full_text for keyword in eight_percent_keywords if keyword not in ['newspaper', 'periodical', 'e-publication']):
        return VAT_RATES['reduced_8']['rate']

    # Check for products that qualify for 5% VAT rate (basic foods, children products, books)
    five_percent_keywords = [
        'bread', 'meat', 'fish', 'fruit', 'vegetable', 'dairy', 'egg', 'juice', 'soup', 'broth',
        'homogenised', 'dietetic', 'food for infants', 'toddler', 'baby', 'child', 'children',
        'pacifier', 'nappy', 'diaper', 'car seat', 'sanitary', 'tampon', 'pad',
        'book', 'e-book', 'publication'  # Removed 'newspaper', 'regional', 'local', 'periodical'
    ]

    if any(keyword in full_text for keyword in five_percent_keywords):
        return VAT_RATES['reduced_5']['rate']

    # For specific categories that might qualify for reduced rates
    if 'food' in cat_lower or 'grocery' in cat_lower or 'restaurant' in cat_lower:
        return VAT_RATES['reduced_5']['rate']
    elif 'book' in cat_lower or 'education' in cat_lower:
        # Special handling for books vs newspapers
        if 'newspaper' in full_text or 'periodical' in full_text:
            # Newspapers and periodicals in book category still get 8% if not regional/local
            if any(word in full_text for word in ['regional', 'local']):
                return VAT_RATES['reduced_5']['rate']
            else:
                return VAT_RATES['reduced_8']['rate']
        else:
            return VAT_RATES['reduced_5']['rate']
    elif 'health' in cat_lower or 'medical' in cat_lower:
        return VAT_RATES['reduced_8']['rate']
    elif 'transport' in cat_lower or 'hotel' in cat_lower:
        return VAT_RATES['reduced_8']['rate']
    elif 'taxi' in cat_lower or 'transportation' in cat_lower:
        return VAT_RATES['parking']['rate']

    # Default to standard VAT rate if no specific category is matched
    return VAT_RATES['standard']['rate']


def remove_background(input_path, output_path):
    """Remove background from image using rembg library"""
    try:
        import io

        from PIL import Image
        from rembg import remove

        # Open the input image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        # Remove background
        output_data = remove(input_data)

        # Save the output to the specified path
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)

        return True
    except Exception as e:
        print(f"Error removing background: {str(e)}")
        return False


from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class InvoiceItem:
    """Represents a single line item in the invoice."""
    item: str  # Product description
    quantity: int
    unit_price_net: float  # Net price per unit in PLN
    gross_total: float  # Total for this item including VAT
    vat_rate: float  # VAT rate (e.g., 0.23 for 23%)
    net_total: float  # Calculated subtotal before VAT
    vat_amount: float  # VAT on this item
    discount: float = 0.0  # Discount percentage or amount

@dataclass
class Invoice:
    """Represents a full Polish VAT-compliant invoice."""
    invoice_number: str  # Unique identifier, e.g., "FA/2025/001"
    issue_date: date  # Invoice creation date
    supply_date: date  # Date of product delivery/sale
    supplier_name: str  # Your business name
    supplier_address: str  # Your full address
    supplier_nip: str  # Your NIP (VAT ID)
    customer_name: str  # Customer's name
    customer_address: str  # Customer's full address
    items: List[InvoiceItem]  # List of invoice items
    overall_net_total: float  # Sum of all net totals
    overall_vat_amount: float  # Sum of all VAT amounts
    overall_gross_total: float  # Total amount due
    currency: str = "PLN"  # Default to PLN for Polish invoices
    customer_nip: Optional[str] = None  # Customer's NIP (optional for B2C)
    payment_due_date: Optional[date] = None  # Due date for payment

# Thread-local storage for database connections
_local = threading.local()

def get_db():
    """Get database connection with proper configuration"""
    conn = sqlite3.connect(
        app.config['DATABASE'],
        timeout=30.0,
        isolation_level=None
    )
    conn.row_factory = sqlite3.Row

    conn.execute('PRAGMA journal_mode=WAL')

    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                loyalty_points INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                notes TEXT
            )
        ''')

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                category TEXT,
                photo TEXT,
                technical_details TEXT,
                shopify_product_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Product Photos table for multiple images
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                is_main INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                shipping_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        # Order Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Customer Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                interaction_type TEXT NOT NULL,
                notes TEXT,
                interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                invoice_number TEXT UNIQUE NOT NULL,
                issue_date DATE NOT NULL,
                supply_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        conn.commit()
    finally:
        conn.close()

# Initialize database on first run
if not os.path.exists(app.config['DATABASE']):
    init_db()
else:
    # Migrations
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Migration: Add photo column to products if it doesn't exist
        try:
            cursor.execute('SELECT photo FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN photo TEXT')
            conn.commit()
            conn.commit()

        # Migration: Create product_photos table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                is_main INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')

        # Migration: Add nip column to customers if it doesn't exist
        try:
            cursor.execute('SELECT nip FROM customers LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE customers ADD COLUMN nip TEXT')
            conn.commit()

        # Migration: Add vat_rate column to products if it doesn't exist (default 23% for Poland)
        try:
            cursor.execute('SELECT vat_rate FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN vat_rate REAL DEFAULT 0.23')
            conn.commit()

        # Migration: Create invoices table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                invoice_number TEXT UNIQUE NOT NULL,
                issue_date DATE NOT NULL,
                supply_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        # Migration: Add technical_details column to products if it doesn't exist
        try:
            cursor.execute('SELECT technical_details FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN technical_details TEXT')
            conn.commit()

        # Migration: Add shopify_product_id column to products if it doesn't exist
        try:
            cursor.execute('SELECT shopify_product_id FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN shopify_product_id INTEGER')
            conn.commit()

        # Migration: Add woocommerce_product_id column to products if it doesn't exist
        try:
            cursor.execute('SELECT woocommerce_product_id FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN woocommerce_product_id INTEGER')
            conn.commit()

        conn.commit()

    finally:
        conn.close()

    # Additional migrations after the main try block
    # Migration: Add tracking_number column to orders if it doesn't exist
    conn = get_db()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT tracking_number FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE orders ADD COLUMN tracking_number TEXT')
            conn.commit()
    finally:
        conn.close()

<<<<<<< HEAD
    # Additional migrations after the main try block
    # Migration: Add tracking_number column to orders if it doesn't exist
=======
    # Migration: Add churn prediction columns to customers if they don't exist
>>>>>>> churn_2
    conn = get_db()
    try:
        cursor = conn.cursor()
        try:
<<<<<<< HEAD
            cursor.execute('SELECT tracking_number FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE orders ADD COLUMN tracking_number TEXT')
            conn.commit()
    finally:
        conn.close()

    # Migration: Add visualization_3d_path column to products if it doesn't exist
    conn = get_db()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT visualization_3d_path FROM products LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE products ADD COLUMN visualization_3d_path TEXT')
=======
            cursor.execute('SELECT churn_probability FROM customers LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE customers ADD COLUMN churn_probability REAL')
            conn.commit()
        try:
            cursor.execute('SELECT stay_probability FROM customers LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE customers ADD COLUMN stay_probability REAL')
            conn.commit()
        try:
            cursor.execute('SELECT customer_lifetime_value FROM customers LIMIT 1')
        except sqlite3.OperationalError:
            cursor.execute('ALTER TABLE customers ADD COLUMN customer_lifetime_value REAL')
>>>>>>> churn_2
            conn.commit()
    finally:
        conn.close()

<<<<<<< HEAD
=======
    # Check if we have churn predictions for customers and run if needed
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM customers WHERE churn_probability IS NOT NULL')
    predictions_count = cursor.fetchone()[0]
    
    # If we have very few predictions, run the churn prediction process
    if predictions_count < 10:  # If less than 10 customers have predictions
        print("Running initial churn prediction process...")
        run_churn_predictions()
    conn.close()

>>>>>>> churn_2
# ==================== INVOICE DATACLASSES ====================

@dataclass
class InvoiceItem:
    """Represents a single line item in the invoice."""
    item: str  # Product description
    quantity: int
    unit_price_net: float  # Net price per unit in PLN
    discount: float = 0.0  # Discount percentage or amount
    vat_rate: float = 0.23  # VAT rate (e.g., 0.23 for 23%)
    net_total: float = 0.0  # Calculated subtotal before VAT
    vat_amount: float = 0.0  # VAT on this item
    gross_total: float = 0.0  # Total for this item including VAT

@dataclass
class Invoice:
    """Represents a full Polish VAT-compliant invoice."""
    invoice_number: str  # Unique identifier, e.g., "FA/2025/001"
    issue_date: date  # Invoice creation date
    supply_date: date  # Date of product delivery/sale
    supplier_name: str  # Your business name
    supplier_address: str  # Your full address
    supplier_nip: str  # Your NIP (VAT ID)
    customer_name: str  # Customer's name
    customer_address: str  # Customer's full address
    customer_nip: Optional[str] = None  # Customer's NIP (optional for B2C)
    items: list = None  # Will be filled with InvoiceItem objects
    currency: str = "$"  # Default to $ for invoices
    payment_due_date: Optional[date] = None  # Due date for payment
    overall_net_total: float = 0.0  # Sum of all net totals
    overall_vat_amount: float = 0.0  # Sum of all VAT amounts
    overall_gross_total: float = 0.0  # Total amount due

    def __post_init__(self):
        if self.items is None:
            self.items = []

        # Calculate totals if not provided
        if self.overall_net_total == 0.0:
            self.overall_net_total = sum(item.net_total for item in self.items)
        if self.overall_vat_amount == 0.0:
            self.overall_vat_amount = sum(item.vat_amount for item in self.items)
        if self.overall_gross_total == 0.0:
            self.overall_gross_total = sum(item.gross_total for item in self.items)

# ==================== INVOICE HELPER FUNCTIONS ====================

def generate_invoice_number():
    """Generate a unique invoice number in format FA/YYYY/NNN"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        current_year = datetime.now().year
        prefix = f"FA/{current_year}/"

        # Get the last invoice number for this year
        last_invoice = cursor.execute(
            'SELECT invoice_number FROM invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1',
            (f'{prefix}%',)
        ).fetchone()

        if last_invoice:
            last_number = int(last_invoice['invoice_number'].split('/')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}{new_number:03d}"
    finally:
        conn.close()

def calculate_invoice_item(item_name: str, quantity: int, unit_price_gross: float, vat_rate: float = 0.23, discount: float = 0.0) -> InvoiceItem:
    """Calculate invoice item with net/gross prices and VAT"""
    # Convert gross price to net price
    unit_price_net = unit_price_gross / (1 + vat_rate)

    # Calculate totals
    net_total = unit_price_net * quantity * (1 - discount / 100)
    vat_amount = net_total * vat_rate
    gross_total = net_total + vat_amount

    return InvoiceItem(
        item=item_name,
        quantity=quantity,
        unit_price_net=round(unit_price_net, 2),
        discount=discount,
        vat_rate=vat_rate,
        net_total=round(net_total, 2),
        vat_amount=round(vat_amount, 2),
        gross_total=round(gross_total, 2)
    )

def execute_with_retry(cursor, query, params=None, max_retries=3):
    """Execute a database query with retry logic for handling potential locking issues"""
    for attempt in range(max_retries):
        try:
            if params:
                return cursor.execute(query, params)
            else:
                return cursor.execute(query)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Wait progressively longer
                continue
            else:
                raise e

def commit_with_retry(conn, max_retries=3):
    """Commit a database transaction with retry logic for handling potential locking issues"""
    for attempt in range(max_retries):
        try:
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Wait progressively longer
                continue
            else:
                raise e

# Function to run churn predictions
def run_churn_predictions():
    """Run churn predictions on customer data and update database exactly as done in churn_prediction.ipynb"""
    import pandas as pd
    import pickle
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    print("running churn prediction")
    try:
        # Load the trained model
        model = joblib.load("churn_prediction.pkl")
        print("✓ Churn prediction model loaded successfully")
        
        # Load the scaler if it was saved, otherwise create a new one
        try:
            scaler = joblib.load("churn_scaler.pkl")
            print("✓ Scaler loaded successfully")
        except FileNotFoundError:
            print("⚠ Scaler not found, will create new one (predictions may be inaccurate)")
            scaler = StandardScaler()
        
        # Load customer data from the churn folder, exactly as in churn_prediction.ipynb
        customer_info = pd.read_csv('churn/Customer_Info.csv')
        location_data = pd.read_csv('churn/Location_Data.csv')
        online_services = pd.read_csv('churn/Online_Services.csv')
        payment_info = pd.read_csv('churn/Payment_Info.csv')
        service_options = pd.read_csv('churn/Service_Options.csv')
        status_analysis = pd.read_csv('churn/Status_Analysis.csv')

        # Merge all dataframes on customer_id, same as in the notebook
        df = status_analysis.merge(service_options, on='customer_id')
        df = df.merge(online_services, on='customer_id')
        df = df.merge(payment_info, on='customer_id')
        df = df.merge(location_data, on='customer_id')
        df = df.merge(customer_info, on='customer_id')
        
        print(f"✓ Loaded customer data for {len(df)} customers")
        
        # Drop the same columns as in the notebook
        X = df.drop([
            'customer_id', 'churn_label', 'churn_value','churn_category',
            'customer_status','churn_reason','country','zip_code','state',
            'longitude', 'latitude','total_population', 'total_population',
            'churn_score','city','total_charges', 'referred_a_friend',
            'gender','senior_citizen', 'partner', 'number_of_dependents', 
            'under_30','number_of_referrals'
        ], axis=1)
        
        print(f"✓ Processed features: {list(X.columns)}")
        
        # Apply get_dummies as in the notebook
        X = pd.get_dummies(X, drop_first=True)
        
        print(f"✓ Feature matrix shape after get_dummies: {X.shape}")
        
        # Scale the features using StandardScaler, exactly as in the notebook
        X_scaled = scaler.transform(X)
        
        print(f"✓ Scaled feature matrix shape: {X_scaled.shape}")
        
        # Make predictions using the loaded model on SCALED data
        churn_probabilities = model.predict_proba(X_scaled)[:, 1]  # Probability of churning
        stay_probabilities = 1 - churn_probabilities  # Probability of staying
        print()
        
        print(f"Sample predictions:")
        print(f"Customer 0 - Churn probability: {churn_probabilities[0]:.4f}")
        print(f"Customer 1 - Churn probability: {churn_probabilities[1]:.4f}")
        
        # Extract CLTV from the original dataframe
        cltv = df['cltv'].values if 'cltv' in df.columns else np.zeros(len(df))
        
        # Create a dictionary mapping customer_id to predictions
        predictions_dict = {}
        for i, customer_id in enumerate(df['customer_id']):
            predictions_dict[customer_id] = {
                'churn_probability': float(churn_probabilities[i]),
                'stay_probability': float(stay_probabilities[i]),
                'cltv': float(cltv[i]) if len(cltv) > i else 0
            }
        
        # Add customers to the database with their predictions
        conn = get_db()
        cursor = conn.cursor()
        
        # Add new columns if they don't exist
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN churn_probability REAL")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN stay_probability REAL")
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN customer_lifetime_value REAL")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Insert or update customers with predictions
        processed_count = 0
        
        # Create a mapping of customer_id to other data for insertion
        customer_data = {}
        for idx, row in df.iterrows():
            customer_id = row['customer_id']
            customer_data[customer_id] = {
                'name': f"{row['gender']}_{row['customer_id']}",  # Use gender and customer_id as name
                'email': f"{row['customer_id']}@example.com",  # Create an email from customer_id
                'age': row.get('age', 0),
                'location': f"{row['city']}, {row['state']}" if 'city' in row and 'state' in row else f"{row.get('city', 'Unknown')}, {row.get('state', 'Unknown')}",
                'contract': row.get('contract', 'Unknown'),
                'payment_method': row.get('payment_method', 'Unknown'),
                'tenure': row.get('tenure', 0)
            }
        
        for customer_id, pred_data in predictions_dict.items():
            # Check if customer already exists
            cursor.execute("SELECT id FROM customers WHERE email = ?", (customer_data[customer_id]['email'],))
            existing_customer = cursor.fetchone()
            
            if existing_customer:
                # Update existing customer with predictions
                cursor.execute('''
                    UPDATE customers 
                    SET churn_probability = ?, stay_probability = ?, customer_lifetime_value = ?
                    WHERE email = ?
                ''', (
                    pred_data['churn_probability'], 
                    pred_data['stay_probability'], 
                    pred_data['cltv'],
                    customer_data[customer_id]['email']
                ))
            else:
                # Insert new customer with predictions
                cursor.execute('''
                    INSERT INTO customers (name, email, churn_probability, stay_probability, customer_lifetime_value, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    customer_data[customer_id]['name'],
                    customer_data[customer_id]['email'],
                    pred_data['churn_probability'],
                    pred_data['stay_probability'],
                    pred_data['cltv'],
                    customer_data[customer_id]['location']
                ))
            
            processed_count += 1
        
        # Additionally, try to match and update any existing customers in the system
        for customer_id, pred_data in predictions_dict.items():
            cursor.execute('''
                UPDATE customers 
                SET churn_probability = ?, stay_probability = ?, customer_lifetime_value = ?
                WHERE name LIKE ? OR email LIKE ? OR notes LIKE ?
            ''', (
                pred_data['churn_probability'], 
                pred_data['stay_probability'], 
                pred_data['cltv'],
                f'%{customer_id}%', 
                f'%{customer_id}%', 
                f'%{customer_id}%'
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Processed churn predictions for {processed_count} customers and added/updated them in database")
        print(f"✓ Processed {len(predictions_dict)} customer predictions")
        return True
    except Exception as e:
        print(f"✗ Error in churn prediction: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_churn_risk_level(churn_probability):
    """Helper function to determine churn risk level based on probability"""
    if churn_probability > 0.7:
        return "High Risk"
    elif churn_probability > 0.4:
        return "Medium Risk"
    else:
        return "Low Risk"

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Dashboard homepage"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Get statistics
        stats = {}
        stats['total_customers'] = cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
        stats['active_customers'] = cursor.execute('SELECT COUNT(*) FROM customers WHERE status = "active"').fetchone()[0]
        stats['total_products'] = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
        stats['total_orders'] = cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        stats['pending_orders'] = cursor.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"').fetchone()[0]

        revenue_result = cursor.execute('SELECT SUM(total_amount) FROM orders WHERE status != "cancelled"').fetchone()[0]
        stats['total_revenue'] = revenue_result if revenue_result else 0

        # Recent orders
        recent_orders = cursor.execute('''
            SELECT o.id, c.name as customer_name, o.order_date, o.total_amount, o.status
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.order_date DESC
            LIMIT 10
        ''').fetchall()

        # Low stock products
        low_stock = cursor.execute('''
            SELECT id, name, stock_quantity
            FROM products
            WHERE stock_quantity < 10
            ORDER BY stock_quantity ASC
            LIMIT 5
        ''').fetchall()

        return render_template('index.html', stats=stats, recent_orders=recent_orders, low_stock=low_stock)
    finally:
        conn.close()

# ==================== CUSTOMER ROUTES ====================

@app.route('/customers')
def customers():
    """View all customers"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Get search query from request
        search_query = request.args.get('search', '').strip()

        if search_query:
            # Search customers by name, email, or phone
            customers = cursor.execute('''
                SELECT * FROM customers
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY date_joined DESC
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')).fetchall()
        else:
            customers = cursor.execute('SELECT * FROM customers ORDER BY date_joined DESC').fetchall()

        return render_template('customers.html', customers=customers, search_query=search_query)
    finally:
        conn.close()

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    """Add a new customer"""
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (name, email, phone, address, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['name'], data['email'], data.get('phone', ''),
                  data.get('address', ''), data.get('notes', '')))
            conn.commit()
            return redirect(url_for('customers'))
        except sqlite3.IntegrityError:
            return "Error: Email already exists", 400
        finally:
            conn.close()

    return render_template('customer_form.html', customer=None)

@app.route('/customers/<int:customer_id>')
def customer_detail(customer_id):
    """View customer details"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        customer = cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()

        # Get customer orders
        orders = cursor.execute('''
            SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC
        ''', (customer_id,)).fetchall()

        # Get customer interactions
        interactions = cursor.execute('''
            SELECT * FROM customer_interactions
            WHERE customer_id = ?
            ORDER BY interaction_date DESC
        ''', (customer_id,)).fetchall()

        if not customer:
            return "Customer not found", 404

        # Calculate customer value based on churn prediction if available

        stay_prob = customer['stay_probability'] if customer['stay_probability'] is not None else 0
        cltv = customer['customer_lifetime_value'] if customer['customer_lifetime_value'] is not None else 0
        
        # Determine if customer is valuable based on stay probability > 70% or high CLTV
        is_valuable = stay_prob > 0.7 or (cltv > 5000 if cltv else False)

        return render_template('customer_detail.html', 
                              customer=customer, 
                              orders=orders, 
                              interactions=interactions,
                              is_valuable=is_valuable,
                              stay_probability=stay_prob,
                              customer_lifetime_value=cltv)
    finally:
        conn.close()

@app.route('/run_churn_predictions', methods=['GET'])
def run_churn_predictions_route():
    """Route to run churn predictions and update database"""
    success = run_churn_predictions()
    if success:
        return jsonify({'success': True, 'message': 'Churn predictions updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to run churn predictions'})
    



@app.route('/update_customer_churn/<int:customer_id>', methods=['GET'])
def update_customer_churn(customer_id):
    """Update churn prediction for a specific customer if possible"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the customer record
    customer = cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    conn.close()
    
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'})
    
    # Note: In a real implementation, we'd need to map the CRM customer to the 
    # churn dataset customer and apply the prediction. For now, we'll return 
    # information about whether this customer already has predictions
    return jsonify({
        'success': True, 
        'message': 'Customer details retrieved',
        'customer_id': customer['id'],
        'name': customer['name'],
        'has_predictions': customer['stay_probability'] is not None,
        'stay_probability': customer['stay_probability'],
        'churn_probability': customer['churn_probability'],
        'customer_lifetime_value': customer['customer_lifetime_value']
    })


def add_sample_customers_db():
    """Add sample customers with known retention values for demonstration (standalone function)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create sample customers with different retention values
    sample_customers = [
        {
            'name': 'Valued Customer Smith',
            'email': 'valued.smith@example.com',
            'phone': '+1234567890',
            'address': '123 Happy Street, City, Country',
            'churn_probability': 0.1,  # 90% retention
            'stay_probability': 0.9,
            'customer_lifetime_value': 15000.0
        },
        {
            'name': 'Regular Customer Johnson',
            'email': 'regular.johnson@example.com',
            'phone': '+1234567891',
            'address': '456 Regular Avenue, City, Country',
            'churn_probability': 0.5,  # 50% retention
            'stay_probability': 0.5,
            'customer_lifetime_value': 3500.0
        },
        {
            'name': 'At Risk Customer Davis',
            'email': 'atrisk.davis@example.com',
            'phone': '+1234567892',
            'address': '789 Risky Road, City, Country',
            'churn_probability': 0.8,  # 20% retention
            'stay_probability': 0.2,
            'customer_lifetime_value': 800.0
        }
    ]
    
    try:
        for customer in sample_customers:
            # Check if customer already exists
            cursor.execute('SELECT id FROM customers WHERE email = ?', (customer['email'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing customer with churn data
                cursor.execute('''
                    UPDATE customers 
                    SET churn_probability = ?, stay_probability = ?, customer_lifetime_value = ?
                    WHERE email = ?
                ''', (
                    customer['churn_probability'], 
                    customer['stay_probability'], 
                    customer['customer_lifetime_value'],
                    customer['email']
                ))
            else:
                # Insert new customer
                cursor.execute('''
                    INSERT INTO customers (name, email, phone, address, churn_probability, stay_probability, customer_lifetime_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    customer['name'],
                    customer['email'],
                    customer['phone'],
                    customer['address'],
                    customer['churn_probability'],
                    customer['stay_probability'],
                    customer['customer_lifetime_value']
                ))
        
        conn.commit()
        print(f'Successfully added/updated {len(sample_customers)} sample customers')
        return True
    except Exception as e:
        conn.rollback()
        print(f'Error adding sample customers: {str(e)}')
        return False
    finally:
        conn.close()

@app.route('/add_sample_customers', methods=['GET'])
def add_sample_customers():
    """Add sample customers with known retention values for demonstration"""
    from flask import jsonify
    success = add_sample_customers_db()
    if success:
        return jsonify({'success': True, 'message': 'Sample customers added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to add sample customers'})

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    """Edit customer information"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        if request.method == 'POST':
            data = request.form
            cursor.execute('''
                UPDATE customers
                SET name = ?, email = ?, phone = ?, address = ?, status = ?, notes = ?
                WHERE id = ?
            ''', (data['name'], data['email'], data.get('phone', ''),
                  data.get('address', ''), data.get('status', 'active'),
                  data.get('notes', ''), customer_id))
            conn.commit()
            return redirect(url_for('customer_detail', customer_id=customer_id))

        customer = cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()

        if not customer:
            return "Customer not found", 404

        return render_template('customer_form.html', customer=customer)
    finally:
        conn.close()

@app.route('/customers/<int:customer_id>/interaction', methods=['POST'])
def add_interaction(customer_id):
    """Add customer interaction"""
    data = request.form
    conn = get_db()
    try:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO customer_interactions (customer_id, interaction_type, notes, created_by)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, data['interaction_type'], data.get('notes', ''), data.get('created_by', 'Admin')))

        conn.commit()
        return redirect(url_for('customer_detail', customer_id=customer_id))
    finally:
        conn.close()

# ==================== PRODUCT ROUTES ====================

@app.route('/products')
def products():
    """View all products"""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Get search query and filter parameters from request
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_stock = request.args.get('min_stock', type=int)
        max_stock = request.args.get('max_stock', type=int)

        # Build the base query
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        # Add search condition
        if search_query:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])

        # Add category filter
        if category_filter:
            query += " AND category = ?"
            params.append(category_filter)

        # Add price filters
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)

        # Add stock filters
        if min_stock is not None:
            query += " AND stock_quantity >= ?"
            params.append(min_stock)

        if max_stock is not None:
            query += " AND stock_quantity <= ?"
            params.append(max_stock)

        # Get all distinct categories for the filter dropdown
        all_categories = cursor.execute('SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category').fetchall()

        query += " ORDER BY created_at DESC"

        products = cursor.execute(query, params).fetchall()

        return render_template('products.html',
                               products=products,
                               search_query=search_query,
                               category_filter=category_filter,
                               min_price=min_price,
                               max_price=max_price,
                               min_stock=min_stock,
                               max_stock=max_stock,
                               all_categories=all_categories)
    finally:
        conn.close()

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product"""
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        cursor = conn.cursor()

        try:
            # Get VAT rate from form or calculate suggested rate
            vat_rate = data.get('vat_rate', '0.23')  # default to standard rate
            if vat_rate:
                vat_rate = float(vat_rate)
            else:
                # If no VAT rate is provided, suggest one based on product information
                vat_rate = suggest_vat_rate(
                    data.get('name', ''),
                    data.get('description', ''),
                    data.get('category', '')
                )

            # Create product
            cursor.execute('''
                INSERT INTO products (name, description, price, stock_quantity, category, technical_details, vat_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['name'], data.get('description', ''), float(data['price']),
                  int(data['stock_quantity']), data.get('category', ''), data.get('technical_details', ''), vat_rate))

            product_id = cursor.lastrowid

            # Handle multiple photo uploads
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                main_photo_index = int(data.get('main_photo', 0))

                for i, file in enumerate(files):
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        original_photo_filename = f"{timestamp}_{i}_{filename}"
                        original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_photo_filename)

                        # Save the original file first
                        file.save(original_file_path)

                        # Check if we should remove background from this image
                        remove_bg = data.get(f'remove_background_{i}', False)  # Check if background removal is requested for this photo
                        if remove_bg or data.get('remove_background_all', False):  # Check if background removal is requested for all
                            # Create background-removed version
                            bg_removed_filename = f"{timestamp}_{i}_bg_removed.png"
                            bg_removed_path = os.path.join(app.config['UPLOAD_FOLDER'], bg_removed_filename)

                            # Apply background removal
                            success = remove_background(original_file_path, bg_removed_path)

                            if success:
                                # Use the background-removed image instead of the original
                                photo_filename = bg_removed_filename
                                # Optionally remove the original if we only want the background-removed version
                                # os.remove(original_file_path)
                            else:
                                # If background removal fails, continue with the original image
                                photo_filename = original_photo_filename
                        else:
                            # No background removal requested, use original file
                            photo_filename = original_photo_filename

                        # Insert into product_photos
                        is_main = 1 if i == main_photo_index else 0
                        cursor.execute('''
                            INSERT INTO product_photos (product_id, photo_path, is_main, display_order)
                            VALUES (?, ?, ?, ?)
                        ''', (product_id, photo_filename, is_main, i))

                        # Set first photo as main product photo for backward compatibility
                        if i == main_photo_index:
                            cursor.execute('UPDATE products SET photo = ? WHERE id = ?', (photo_filename, product_id))

            conn.commit()

            # Synchronize product to Shopify
            try:
                # Get the 3D visualization path for this product if it exists
                # For new products, this will typically be None initially
                product_record = cursor.execute('SELECT visualization_3d_path FROM products WHERE id = ?', (product_id,)).fetchone()

                product_data = {
                    'id': product_id,
                    'name': data['name'],
                    'description': data.get('description', ''),
                    'price': float(data['price']),
                    'stock_quantity': int(data['stock_quantity']),
                    'category': data.get('category', ''),
                    'technical_details': data.get('technical_details', ''),
                    'photo': cursor.execute('SELECT photo FROM products WHERE id = ?', (product_id,)).fetchone()['photo']
                }

                sync_result = sync_product_to_shopify(product_data)

                if sync_result.get('success'):
                    # Update product with Shopify product ID if successful
                    shopify_product_id = sync_result.get('shopify_product_id')
                    if shopify_product_id:
                        cursor.execute('''
                            UPDATE products
                            SET shopify_product_id = ?
                            WHERE id = ?
                        ''', (shopify_product_id, product_id))
                        conn.commit()
                        print(f"Product synchronized to Shopify: {sync_result.get('message')}")
                else:
                    print(f"Failed to sync product to Shopify: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
            except Exception as shopify_error:
                print(f"Shopify sync error: {str(shopify_error)}")

            # Synchronize product to WooCommerce if enabled
            if WOOCOMMERCE_ENABLED:
                try:
                    # Get the photo filename for the product
                    photo_result = cursor.execute('SELECT photo FROM products WHERE id = ?', (product_id,)).fetchone()
                    photo_filename = photo_result['photo'] if photo_result else None

                    product_data = {
                        'id': product_id,
                        'name': data['name'],
                        'description': data.get('description', ''),
                        'price': float(data['price']),
                        'stock_quantity': int(data['stock_quantity']),
                        'category': data.get('category', ''),
                        'technical_details': data.get('technical_details', ''),
                        'photo': photo_filename
                    }

                    sync_result = sync_product_to_woocommerce(product_data)

                    if sync_result.get('success'):
                        # Update product with WooCommerce product ID if successful
                        woocommerce_product_id = sync_result.get('woocommerce_product_id')
                        if woocommerce_product_id:
                            cursor.execute("""
                                UPDATE products
                                SET woocommerce_product_id = ?
                                WHERE id = ?
                            """, (woocommerce_product_id, product_id))
                            conn.commit()
                            print(f"Product synchronized to WooCommerce: {sync_result.get('message')}")
                    else:
                        print(f"Failed to sync product to WooCommerce: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
                except Exception as woocommerce_error:
                    print(f"WooCommerce sync error: {str(woocommerce_error)}")

            return redirect(url_for('products'))
        except Exception as e:
            conn.rollback()
            return f"Error adding product: {str(e)}", 500
        finally:
            conn.close()

    return render_template('product_form.html', product=None, product_photos=[], vat_rates=VAT_RATES)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit product information"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form

        try:
            # Get VAT rate from form
            vat_rate = data.get('vat_rate', '0.23')  # default to standard rate
            if vat_rate:
                vat_rate = float(vat_rate)
            else:
                # If no VAT rate is provided, suggest one based on product information
                vat_rate = suggest_vat_rate(
                    data.get('name', ''),
                    data.get('description', ''),
                    data.get('category', '')
                )

            # Update product
            cursor.execute('''
                UPDATE products
                SET name = ?, description = ?, price = ?, stock_quantity = ?, category = ?, technical_details = ?, visualization_3d_path = ?, vat_rate = ?
                WHERE id = ?
            ''', (data['name'], data.get('description', ''), float(data['price']),
                  int(data['stock_quantity']), data.get('category', ''), data.get('technical_details', ''), data.get('visualization_3d_path', None), vat_rate, product_id))

            # Handle new photo uploads
            if 'photos' in request.files:
                files = request.files.getlist('photos')
                main_photo_index = int(data.get('main_photo', 0))

                # Get current max display order
                max_order = cursor.execute('SELECT MAX(display_order) FROM product_photos WHERE product_id = ?', (product_id,)).fetchone()[0]
                start_order = (max_order or -1) + 1

                for i, file in enumerate(files):
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        original_photo_filename = f"{timestamp}_{i}_{filename}"
                        original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_photo_filename)

                        # Save the original file first
                        file.save(original_file_path)

                        # Check if we should remove background from this image
                        remove_bg = data.get(f'remove_background_{i}', False)  # Check if background removal is requested for this photo
                        if remove_bg or data.get('remove_background_all', False):  # Check if background removal is requested for all
                            # Create background-removed version
                            bg_removed_filename = f"{timestamp}_{i}_bg_removed.png"
                            bg_removed_path = os.path.join(app.config['UPLOAD_FOLDER'], bg_removed_filename)

                            # Apply background removal
                            success = remove_background(original_file_path, bg_removed_path)

                            if success:
                                # Use the background-removed image instead of the original
                                photo_filename = bg_removed_filename
                                # Optionally remove the original if we only want the background-removed version
                                # os.remove(original_file_path)
                            else:
                                # If background removal fails, continue with the original image
                                photo_filename = original_photo_filename
                        else:
                            # No background removal requested, use original file
                            photo_filename = original_photo_filename

                        # Insert into product_photos
                        is_main = 1 if i == main_photo_index else 0
                        cursor.execute('''
                            INSERT INTO product_photos (product_id, photo_path, is_main, display_order)
                            VALUES (?, ?, ?, ?)
                        ''', (product_id, photo_filename, is_main, start_order + i))

                        # Update main photo in products table
                        if is_main:
                            # Unset other main photos
                            cursor.execute('UPDATE product_photos SET is_main = 0 WHERE product_id = ? AND photo_path != ?', (product_id, photo_filename))
                            cursor.execute('UPDATE products SET photo = ? WHERE id = ?', (photo_filename, product_id))
            conn.commit()

            # Synchronize product changes to Shopify
            try:
                # Get the updated product data
                updated_product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

                if updated_product:
                    shopify_product_id = updated_product['shopify_product_id']

                    if shopify_product_id:  # Only sync if the product was previously synchronized

                        product_data = {
                            'id': product_id,
                            'name': updated_product['name'],
                            'description': updated_product['description'],
                            'price': updated_product['price'],
                            'stock_quantity': updated_product['stock_quantity'],
                            'category': updated_product['category'],
                            'technical_details': updated_product['technical_details'],
                            'photo': updated_product['photo']
                        }

                        sync_result = sync_product_to_shopify(product_data, shopify_product_id=shopify_product_id)

                        if sync_result.get('success'):
                            print(f"Product updated in Shopify: {sync_result.get('message')}")
                        else:
                            print(f"Failed to update product in Shopify: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
                    else:
                        # If no shopify_product_id was found, create it in Shopify
                        # Get 3D visualization path if the column exists

                        product_data = {
                            'id': product_id,
                            'name': updated_product['name'],
                            'description': updated_product['description'],
                            'price': updated_product['price'],
                            'stock_quantity': updated_product['stock_quantity'],
                            'category': updated_product['category'],
                            'technical_details': updated_product['technical_details'],
                            'photo': updated_product['photo']
                        }

                        sync_result = sync_product_to_shopify(product_data)

                        if sync_result.get('success'):
                            shopify_product_id = sync_result.get('shopify_product_id')
                            if shopify_product_id:
                                cursor.execute('''
                                    UPDATE products
                                    SET shopify_product_id = ?
                                    WHERE id = ?
                                ''', (shopify_product_id, product_id))
                                conn.commit()
                                print(f"Product synchronized to Shopify: {sync_result.get('message')}")
                        else:
                            print(f"Failed to sync product to Shopify: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
            except Exception as shopify_error:
                print(f"Shopify sync error: {str(shopify_error)}")

            # Synchronize product changes to WooCommerce if enabled
            if WOOCOMMERCE_ENABLED:
                try:
                    # Get the updated product data
                    updated_product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

                    if updated_product:
                        woocommerce_product_id = updated_product['woocommerce_product_id']

                        if woocommerce_product_id:  # Only sync if the product was previously synchronized
                            product_data = {
                                'id': product_id,
                                'name': updated_product['name'],
                                'description': updated_product['description'],
                                'price': updated_product['price'],
                                'stock_quantity': updated_product['stock_quantity'],
                                'category': updated_product['category'],
                                'technical_details': updated_product['technical_details'],
                                'photo': updated_product['photo']
                            }

                            sync_result = sync_product_to_woocommerce(product_data, woocommerce_product_id=woocommerce_product_id)

                            if sync_result.get('success'):
                                print(f"Product updated in WooCommerce: {sync_result.get('message')}")
                            else:
                                print(f"Failed to update product in WooCommerce: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
                        else:
                            # If no woocommerce_product_id was found, create it in WooCommerce
                            product_data = {
                                'id': product_id,
                                'name': updated_product['name'],
                                'description': updated_product['description'],
                                'price': updated_product['price'],
                                'stock_quantity': updated_product['stock_quantity'],
                                'category': updated_product['category'],
                                'technical_details': updated_product['technical_details'],
                                'photo': updated_product['photo']
                            }

                            sync_result = sync_product_to_woocommerce(product_data)

                            if sync_result.get('success'):
                                woocommerce_product_id = sync_result.get('woocommerce_product_id')
                                if woocommerce_product_id:
                                    cursor.execute("""
                                        UPDATE products
                                        SET woocommerce_product_id = ?
                                        WHERE id = ?
                                    """, (woocommerce_product_id, product_id))
                                    conn.commit()
                                    print(f"Product synchronized to WooCommerce: {sync_result.get('message')}")
                            else:
                                print(f"Failed to sync product to WooCommerce: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
                except Exception as woocommerce_error:
                    print(f"WooCommerce sync error: {str(woocommerce_error)}")

            return redirect(url_for('products'))
        except Exception as e:
            conn.rollback()
            return f"Error editing product: {str(e)}", 500
        finally:
            conn.close()

    try:
        product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        product_photos = cursor.execute('SELECT * FROM product_photos WHERE product_id = ? ORDER BY display_order', (product_id,)).fetchall()
    finally:
        conn.close()

    if not product:
        return "Product not found", 404

    return render_template('product_form.html', product=product, product_photos=product_photos, vat_rates=VAT_RATES)

@app.route('/products/<int:product_id>/photos/<int:photo_id>/delete', methods=['POST'])
def delete_product_photo(product_id, photo_id):
    """Delete a product photo"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Get photo
        photo = cursor.execute('SELECT * FROM product_photos WHERE id = ? AND product_id = ?', (photo_id, product_id)).fetchone()

        if photo:
            # Delete file
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['photo_path'])
            if os.path.exists(photo_path):
                os.remove(photo_path)

            # Delete from database
            cursor.execute('DELETE FROM product_photos WHERE id = ?', (photo_id,))

            # If this was the main photo, set another as main
            if photo['is_main']:
                new_main = cursor.execute('SELECT * FROM product_photos WHERE product_id = ? ORDER BY display_order LIMIT 1', (product_id,)).fetchone()
                if new_main:
                    cursor.execute('UPDATE product_photos SET is_main = 1 WHERE id = ?', (new_main['id'],))
                    cursor.execute('UPDATE products SET photo = ? WHERE id = ?', (new_main['photo_path'], product_id))
                else:
                    cursor.execute('UPDATE products SET photo = NULL WHERE id = ?', (product_id,))

            conn.commit()
        return redirect(url_for('edit_product', product_id=product_id))
    except Exception as e:
        conn.rollback()
        return f"Error deleting photo: {str(e)}", 500
    finally:
        conn.close()

@app.route('/products/<int:product_id>/photos/<int:photo_id>/set_main', methods=['POST'])
def set_main_photo(product_id, photo_id):
    """Set a photo as the main photo"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Get photo
        photo = cursor.execute('SELECT * FROM product_photos WHERE id = ? AND product_id = ?', (photo_id, product_id)).fetchone()

        if photo:
            # Unset all main photos for this product
            cursor.execute('UPDATE product_photos SET is_main = 0 WHERE product_id = ?', (product_id,))

            # Set this photo as main
            cursor.execute('UPDATE product_photos SET is_main = 1 WHERE id = ?', (photo_id,))
            cursor.execute('UPDATE products SET photo = ? WHERE id = ?', (photo['photo_path'], product_id))

            conn.commit()
        return redirect(url_for('edit_product', product_id=product_id))
    except Exception as e:
        conn.rollback()
        return f"Error setting main photo: {str(e)}", 500
    finally:
        conn.close()


@app.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Delete a product and synchronize with Shopify"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Get product from database to check if it's linked to Shopify
        product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

        if not product:
            return "Product not found", 404

        shopify_product_id = product['shopify_product_id']

        # Delete from local database (will cascade to product_photos)
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()

        # If product was linked to Shopify, delete it there too
        if shopify_product_id:
            try:
                sync_result = delete_product_from_shopify(shopify_product_id)
                if sync_result.get('success'):
                    print(f"Product deleted from Shopify: {sync_result.get('message')}")
                else:
                    print(f"Failed to delete product from Shopify: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
            except Exception as shopify_error:
                print(f"Shopify deletion error: {str(shopify_error)}")

            # If product was also linked to WooCommerce, delete it there too
            woocommerce_product_id = product['woocommerce_product_id']
            if WOOCOMMERCE_ENABLED and woocommerce_product_id:
                try:
                    sync_result = delete_product_from_woocommerce(woocommerce_product_id)
                    if sync_result.get('success'):
                        print(f"Product deleted from WooCommerce: {sync_result.get('message')}")
                    else:
                        print(f"Failed to delete product from WooCommerce: {sync_result.get('message', sync_result.get('error', 'Unknown error'))}")
                except Exception as woocommerce_error:
                    print(f"WooCommerce deletion error: {str(woocommerce_error)}")

        return redirect(url_for('products'))
    except Exception as e:
        conn.rollback()
        return f"Error deleting product: {str(e)}", 500
    finally:
        conn.close()

@app.route('/products/<int:product_id>/analyze')
def product_analysis(product_id):
    """Analyze product market data"""
    conn = get_db()
    cursor = conn.cursor()

    # Get product details
    product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    if not product:
        conn.close()
        return "Product not found", 404

    # Get product photos
    product_photos = cursor.execute('SELECT * FROM product_photos WHERE product_id = ? ORDER BY is_main DESC, display_order', (product_id,)).fetchall()

    # Get sales data for this product
    sales_data = cursor.execute('''
        SELECT
            COUNT(DISTINCT oi.order_id) as total_orders,
            SUM(oi.quantity) as total_quantity_sold,
            SUM(oi.subtotal) as total_revenue,
            AVG(oi.quantity) as avg_quantity_per_order
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.product_id = ? AND o.status != 'cancelled'
    ''', (product_id,)).fetchone()

    # Get recent orders for this product
    recent_orders = cursor.execute('''
        SELECT o.id, o.order_date, o.total_amount, c.name as customer_name, oi.quantity, oi.subtotal
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN customers c ON o.customer_id = c.id
        WHERE oi.product_id = ?
        ORDER BY o.order_date DESC
        LIMIT 10
    ''', (product_id,)).fetchall()

    # Get similar products in the same category
    similar_products = cursor.execute('''
        SELECT * FROM products
        WHERE category = ? AND id != ?
        LIMIT 5
    ''', (product['category'], product_id)).fetchall()

    conn.close()

    return render_template('product_analysis.html',
                          product=product,
                          product_photos=product_photos,
                          sales_data=sales_data,
                          recent_orders=recent_orders,
                          similar_products=similar_products)

# ==================== ORDER ROUTES ====================

@app.route('/orders')
def orders():
    """View all orders"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        orders = cursor.execute('''
            SELECT o.*, c.name as customer_name, i.invoice_number
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN invoices i ON o.id = i.order_id
            ORDER BY o.order_date DESC
        ''').fetchall()
        return render_template('orders.html', orders=orders)
    finally:
        conn.close()

@app.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    """Create a new order"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.form
        customer_id = int(data['customer_id'])
        payment_method = data.get('payment_method', 'cash')
        shipping_address = data.get('shipping_address', '')

        # Get order items from form (assuming JSON or multiple fields)
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        if not product_ids:
            conn.close()
            return "Error: No products selected", 400

        # Calculate total
        total_amount = 0
        order_items = []

        for i, product_id in enumerate(product_ids):
            product = cursor.execute('SELECT * FROM products WHERE id = ?', (int(product_id),)).fetchone()
            if product:
                quantity = int(quantities[i])

                # Validate stock availability
                if quantity > product['stock_quantity']:
                    conn.close()
                    return f"Error: Cannot order {quantity} units of '{product['name']}'. Only {product['stock_quantity']} units available in stock.", 400

                unit_price = product['price']
                subtotal = unit_price * quantity
                total_amount += subtotal
                order_items.append((int(product_id), quantity, unit_price, subtotal))

        # Create order
        cursor.execute('''
            INSERT INTO orders (customer_id, total_amount, payment_method, shipping_address)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, total_amount, payment_method, shipping_address))

        order_id = cursor.lastrowid

        # Add order items
        for product_id, quantity, unit_price, subtotal in order_items:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, product_id, quantity, unit_price, subtotal))

            # Update product stock
            cursor.execute('''
                UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?
            ''', (quantity, product_id))

        # Add loyalty points (1 point per dollar spent)
        cursor.execute('''
            UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?
        ''', (int(total_amount), customer_id))

        conn.commit()
        conn.close()
        return redirect(url_for('order_detail', order_id=order_id))

    # GET request
    customers = cursor.execute('SELECT id, name, email FROM customers WHERE status = "active" ORDER BY name').fetchall()
    products = cursor.execute('SELECT id, name, price, stock_quantity FROM products WHERE stock_quantity > 0 ORDER BY name').fetchall()
    conn.close()

    return render_template('order_form.html', customers=customers, products=products)

@app.route('/orders/<int:order_id>')
def order_detail(order_id):
    """View order details"""
    conn = get_db()
    cursor = conn.cursor()

    order = cursor.execute('''
        SELECT o.*, c.name as customer_name, c.email as customer_email, i.invoice_number
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN invoices i ON o.id = i.order_id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()

    if not order:
        conn.close()
        return "Order not found", 404

    # Get order items
    items = cursor.execute('''
        SELECT oi.*, p.name as product_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()

    conn.close()
    return render_template('order_detail.html', order=order, items=items)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """Update order status"""
    status = request.form.get('status')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()

    return redirect(url_for('order_detail', order_id=order_id))


@app.route('/orders/<int:order_id>/add_tracking', methods=['POST'])
def add_tracking_number(order_id):
    """Add tracking number to order"""
    tracking_number = request.form.get('tracking_number', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    # Update the order with the tracking number
    execute_with_retry(cursor, 'UPDATE orders SET tracking_number = ? WHERE id = ?', (tracking_number, order_id))
    commit_with_retry(conn)
    conn.close()

    return redirect(url_for('order_detail', order_id=order_id))


@app.route('/orders/<int:order_id>/generate_invoice', methods=['POST'])
def generate_invoice_for_order(order_id):
    """Generate invoice for an order and return PDF"""
    print(835,order_id)
    conn = get_db()
    cursor = conn.cursor()

    # Check if invoice already exists for this order
    existing_invoice = cursor.execute(
        'SELECT invoice_number FROM invoices WHERE order_id = ?',
        (order_id,)
    ).fetchone()

    print(existing_invoice)

    if existing_invoice:
        conn.close()
        return jsonify({
            'success': False,
            'error': f'Invoice already exists: {existing_invoice["invoice_number"]}'
        }), 400

    order = cursor.execute('''
        SELECT o.*, c.name as customer_name, c.email as customer_email,
               c.address as customer_address, c.nip as customer_nip
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    customer_email = order['customer_email']

    if not order:
        conn.close()
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    # Fetch order items with product details
    order_items = cursor.execute('''
        SELECT oi.*, p.name as product_name, p.vat_rate
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    # print(order_items)

    if not order_items:
        conn.close()
        return jsonify({'success': False, 'error': 'No items found in order'}), 400

    invoice_number = generate_invoice_number()

    invoice_items = []
    for item in order_items:
        # Use the product's VAT rate if available, otherwise default to 23%
        vat_rate = item['vat_rate'] if item['vat_rate'] is not None else 0.23
        invoice_item = calculate_invoice_item(
            item_name=item['product_name'],
            quantity=item['quantity'],
            unit_price_gross=item['unit_price'],
            vat_rate=vat_rate,
            discount=0.0
        )
        invoice_items.append(invoice_item)

    # Calculate totals
    overall_net_total = sum(item.net_total for item in invoice_items)
    overall_vat_amount = sum(item.vat_amount for item in invoice_items)
    overall_gross_total = sum(item.gross_total for item in invoice_items)

    invoice = Invoice(
        invoice_number=invoice_number,
        issue_date=date.today(),
        supply_date=datetime.strptime(order['order_date'].split('.')[0].replace(" ", "T"), '%Y-%m-%dT%H:%M:%S').date() if order['order_date'] else date.today(),
        supplier_name=app.config['SUPPLIER_NAME'],
        supplier_address=app.config['SUPPLIER_ADDRESS'],
        supplier_nip=app.config['SUPPLIER_NIP'],
        customer_name=order['customer_name'],
        customer_address=order['customer_address'] or 'Address not provided',
        customer_nip=order['customer_nip'],
        items=invoice_items,
        overall_net_total=round(overall_net_total, 2),
        overall_vat_amount=round(overall_vat_amount, 2),
        overall_gross_total=round(overall_gross_total, 2)
    )

    pdf_bytes = generate_invoice_pdf_bytes(invoice)

    send_invoice_email(customer_email, invoice, pdf_bytes)

    cursor.execute('''
        INSERT INTO invoices (order_id, invoice_number, issue_date, supply_date)
        VALUES (?, ?, ?, ?)
    ''', (order_id, invoice_number, invoice.issue_date, invoice.supply_date))
    conn.commit()
    conn.close()

    invoice_dict = asdict(invoice)
    # print(invoice_dict)

    return jsonify({
        'success': True,
        'invoice_number': invoice_number,
        'invoice': invoice_dict,
        'pdf_available': True
    })

# ==================== API ROUTES ====================

@app.route('/api/suggest_vat_rate', methods=['POST'])
def api_suggest_vat_rate():
    """API: Suggest VAT rate using Kimi2 AI based on product information"""
    try:
        data = request.json
        product_name = data.get('product_name', '')
        product_description = data.get('product_description', '')
        technical_details = data.get('technical_details', '')
        category = data.get('category', '')
        images = data.get('images', [])

        # First try the built-in rule-based VAT suggestion
        rule_based_rate = suggest_vat_rate(product_name, product_description, category)

        # Get the label for the rule-based rate
        rate_label = None
        for rate_key, rate_info in VAT_RATES.items():
            if rate_info['rate'] == rule_based_rate:
                rate_label = rate_info['label']
                break

        # If we have Moonshot API available, use Kimi2 for better suggestions
        if moonshot_available and moonshot_client:
            try:
                # Create a system prompt to guide the AI
                system_prompt = f"""
                You are an AI assistant specialized in Polish VAT regulations.
                Determine the appropriate VAT rate for the given product based on Polish tax law.

                Polish VAT rates:
                - Standard rate: 23%
                - Reduced rate: 8% - for certain food products (sugar, spices, processed food), newspapers, healthcare products, etc.
                - Reduced rate: 5% - for basic foods (bread, meat, fruits, vegetables), children products, books, etc.
                - Reduced rate: 0% - for exports, intra-EU supplies, etc.
                - Parking rate: 4% - for taxi operation services

                Based on the product information provided, respond with a JSON object containing:
                - "vat_rate": the suggested VAT rate as a decimal (e.g., 0.23, 0.08, 0.05, 0.00, 0.04)
                - "reasoning": explanation for the suggested VAT rate
                - "confidence": confidence level of the suggestion (high, medium, low)

                Provide only the JSON response, nothing else.
                """

                # Combine all product information
                user_prompt = f"""
                Product Name: {product_name}
                Product Description: {product_description}
                Technical Details: {technical_details}
                Category: {category}

                Based on this information, what VAT rate should be applied?
                """

                response = moonshot_client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,  # Lower temperature for more consistent responses
                    max_tokens=300
                )

                # Extract the AI response
                ai_response = response.choices[0].message.content.strip()

                # Try to parse the JSON response from Kimi2
                import json
                import re

                # Look for JSON in the response (sometimes AI might include text around it)
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    ai_result = json.loads(json_str)

                    return jsonify({
                        'vat_rate': ai_result.get('vat_rate', rule_based_rate),
                        'reasoning': ai_result.get('reasoning', f'AI suggested based on product information. Fallback: {rate_label}'),
                        'confidence': ai_result.get('confidence', 'medium'),
                        'method': 'ai_suggestion'
                    })
                else:
                    # If JSON parsing fails, fall back to rule-based system
                    return jsonify({
                        'vat_rate': rule_based_rate,
                        'reasoning': f'AI response was not in expected format. Using rule-based suggestion: {rate_label}',
                        'confidence': 'medium',
                        'method': 'rule_based_fallback'
                    })

            except Exception as ai_error:
                # If Kimi2 fails, fall back to rule-based system
                print(f"Kimi2 VAT suggestion failed: {str(ai_error)}")
                return jsonify({
                    'vat_rate': rule_based_rate,
                    'reasoning': f'Using rule-based suggestion due to AI error: {rate_label}',
                    'confidence': 'medium',
                    'method': 'rule_based_fallback'
                })
        else:
            # If no Kimi2 is available, use the rule-based approach
            return jsonify({
                'vat_rate': rule_based_rate,
                'reasoning': f'Using rule-based suggestion: {rate_label}',
                'confidence': 'medium',
                'method': 'rule_based'
            })

    except Exception as e:
        return jsonify({
            'error': f'Failed to suggest VAT rate: {str(e)}'
        }), 500


@app.route('/api/customers', methods=['GET'])
def api_get_customers():
    """API: Get all customers"""
    conn = get_db()
    cursor = conn.cursor()
    customers = cursor.execute('SELECT * FROM customers').fetchall()
    conn.close()
    
    # Convert to list of dictionaries and add formatted churn risk
    customer_list = []
    for c in customers:
        customer_dict = dict(c)
        # Add formatted churn risk information
        if customer_dict.get('churn_probability') is not None:
            customer_dict['churn_risk_level'] = get_churn_risk_level(customer_dict['churn_probability'])
            customer_dict['churn_probability_percent'] = round(customer_dict['churn_probability'] * 100, 2)
        customer_list.append(customer_dict)
    
    return jsonify(customer_list)

@app.route('/api/products', methods=['GET'])
def api_get_products():
    """API: Get all products"""
    conn = get_db()
    cursor = conn.cursor()
    products = cursor.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

@app.route('/api/invoice_by_order/<int:order_id>')
def api_get_invoice_by_order(order_id):
    """API: Get invoice details by order ID"""
    conn = get_db()
    cursor = conn.cursor()

    # Get invoice details from database
    invoice_record = cursor.execute('''
        SELECT i.*, o.id as order_id, c.name as customer_name, c.email as customer_email,
               c.address as customer_address, c.nip as customer_nip
        FROM invoices i
        JOIN orders o ON i.order_id = o.id
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()

    if not invoice_record:
        conn.close()
        return jsonify({
            'success': False,
            'error': 'Invoice not found'
        }), 404

    # Get invoice items
    order_items = cursor.execute('''
        SELECT oi.*, p.name as product_name, p.vat_rate
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()

    conn.close()

    # Recreate invoice items
    invoice_items = []
    for item in order_items:
        vat_rate = item['vat_rate'] if item['vat_rate'] is not None else 0.23
        invoice_item = calculate_invoice_item(
            item_name=item['product_name'],
            quantity=item['quantity'],
            unit_price_gross=item['unit_price'],
            vat_rate=vat_rate,
            discount=0.0
        )
        invoice_items.append(invoice_item)

    # Calculate totals
    overall_net_total = sum(item.net_total for item in invoice_items)
    overall_vat_amount = sum(item.vat_amount for item in invoice_items)
    overall_gross_total = sum(item.gross_total for item in invoice_items)

    # Create response data
    invoice_data = {
        'success': True,
        'invoice_number': invoice_record['invoice_number'],
        'issue_date': invoice_record['issue_date'],
        'supply_date': invoice_record['supply_date'],
        'supplier_name': app.config['SUPPLIER_NAME'],
        'supplier_address': app.config['SUPPLIER_ADDRESS'],
        'supplier_nip': app.config['SUPPLIER_NIP'],
        'customer_name': invoice_record['customer_name'],
        'customer_address': invoice_record['customer_address'] or 'Address not provided',
        'customer_nip': invoice_record['customer_nip'],
        'items': [asdict(item) for item in invoice_items],
        'overall_net_total': round(overall_net_total, 2),
        'overall_vat_amount': round(overall_vat_amount, 2),
        'overall_gross_total': round(overall_gross_total, 2),
        'currency': "PLN"
    }

    return jsonify(invoice_data)


@app.route('/api/generate_description', methods=['POST'])
def api_generate_description():
    """API: Generate product description using AI"""
    conn = None
    try:
        data = request.json
        product_name = data.get('product_name', '')
        product_details = data.get('product_details', '')
        image_data = data.get('images', [])

        # Get the current product's existing photos if we're editing
        product_id = data.get('product_id')
        if product_id:
            conn = get_db()
            cursor = conn.cursor()
            existing_photos = cursor.execute('''
                SELECT photo_path FROM product_photos WHERE product_id = ? ORDER BY is_main DESC, display_order
            ''', (product_id,)).fetchall()
            conn.close()
            conn = None  # Reset connection variable

            # Convert existing photos to base64
            for photo in existing_photos:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['photo_path'])
                if os.path.exists(photo_path):
                    from generate_description import image_to_base64
                    try:
                        base64_img = image_to_base64(photo_path)
                        if base64_img not in image_data:
                            image_data.append(base64_img)
                    except Exception as e:
                        print(f"Error converting existing photo to base64: {str(e)}")

        # Import generate_description function
        from generate_description import generate_product_description

        # Generate the description
        result = generate_product_description(
            product_name=product_name,
            product_details=product_details,
            base64_images=image_data if image_data else None
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Failed to generate description: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/generate_category', methods=['POST'])
def api_generate_category():
    """API: Generate product category using AI"""
    conn = None
    try:
        data = request.json
        product_name = data.get('product_name', '')
        product_details = data.get('product_details', '')
        image_data = data.get('images', [])

        # Get the current product's existing photos if we're editing
        product_id = data.get('product_id')
        if product_id:
            conn = get_db()
            cursor = conn.cursor()
            existing_photos = cursor.execute('''
                SELECT photo_path FROM product_photos WHERE product_id = ? ORDER BY is_main DESC, display_order
            ''', (product_id,)).fetchall()
            conn.close()
            conn = None  # Reset connection variable

            # Convert existing photos to base64
            for photo in existing_photos:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['photo_path'])
                if os.path.exists(photo_path):
                    from generate_description import image_to_base64
                    try:
                        base64_img = image_to_base64(photo_path)
                        if base64_img not in image_data:
                            image_data.append(base64_img)
                    except Exception as e:
                        print(f"Error converting existing photo to base64: {str(e)}")

        # Import generate_category function
        from generate_description import generate_product_category

        # Generate the category
        result = generate_product_category(
            product_name=product_name,
            product_details=product_details,
            base64_images=image_data if image_data else None
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Failed to generate category: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/generate_price', methods=['POST'])
def api_generate_price():
    """API: Generate product price prediction using AI"""
    conn = None
    try:
        data = request.json
        product_name = data.get('product_name', '')
        product_details = data.get('product_details', '')
        brand = data.get('brand', '')
        image_data = data.get('images', [])

        # Get the current product's existing photos if we're editing
        product_id = data.get('product_id')
        if product_id:
            conn = get_db()
            cursor = conn.cursor()
            existing_photos = cursor.execute('''
                SELECT photo_path FROM product_photos WHERE product_id = ? ORDER BY is_main DESC, display_order
            ''', (product_id,)).fetchall()
            conn.close()
            conn = None  # Reset connection variable

            # Convert existing photos to base64
            for photo in existing_photos:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['photo_path'])
                if os.path.exists(photo_path):
                    from generate_description import image_to_base64
                    try:
                        base64_img = image_to_base64(photo_path)
                        if base64_img not in image_data:
                            image_data.append(base64_img)
                    except Exception as e:
                        print(f"Error converting existing photo to base64: {str(e)}")

        # Import generate_price function
        from generate_description import generate_product_price

        # Generate the price prediction
        result = generate_product_price(
            product_name=product_name,
            product_details=product_details,
            brand=brand,
            base64_images=image_data if image_data else None
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Failed to generate price: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/generate_3d_visualization', methods=['POST'])
def api_generate_3d_visualization():
    """API: Generate product 3D visualization using AI"""
    conn = None
    try:
        data = request.json
        product_name = data.get('product_name', '')
        product_details = data.get('product_details', '')
        image_data = data.get('images', [])

        # Get the current product's existing photos if we're editing
        product_id = data.get('product_id')
        if product_id:
            conn = get_db()
            cursor = conn.cursor()
            existing_photos = cursor.execute('''
                SELECT photo_path FROM product_photos WHERE product_id = ? ORDER BY is_main DESC, display_order
            ''', (product_id,)).fetchall()
            conn.close()
            conn = None  # Reset connection variable

            # Convert existing photos to base64
            for photo in existing_photos:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['photo_path'])
                if os.path.exists(photo_path):
                    from generate_description import image_to_base64
                    try:
                        base64_img = image_to_base64(photo_path)
                        if base64_img not in image_data:
                            image_data.append(base64_img)
                    except Exception as e:
                        print(f"Error converting existing photo to base64: {str(e)}")

        # Import generate_3d_visualization function
        from generate_description import generate_product_3d_visualization

        # Generate the 3D visualization
        result = generate_product_3d_visualization(
            product_name=product_name,
            product_details=product_details,
            base64_images=image_data if image_data else None
        )

        # If a product_id was provided and visualization_path exists, save it to the database
        if product_id and result.get('visualization_path'):
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE products
                    SET visualization_3d_path = ?
                    WHERE id = ?
                ''', (result['visualization_path'], product_id))
                conn.commit()
                conn.close()
                conn = None
            except Exception as db_error:
                print(f"Error saving 3D visualization path to database: {str(db_error)}")
                # Continue with the response even if saving to DB fails

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Failed to generate 3D visualization: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/remove_background', methods=['POST'])
def api_remove_background():
    """API: Remove background from an image using rembg library"""
    try:
        data = request.json
        image_data = data.get('image_data', '')

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Import required modules
        import base64
        import io

        from PIL import Image

        # Decode the base64 image data
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as decode_error:
            return jsonify({'error': f'Failed to decode image data: {str(decode_error)}'}), 400

        # Save the image temporarily
        temp_input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_input.png')
        temp_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_output.png')

        try:
            # Write the input image to temporary file
            with open(temp_input_path, 'wb') as f:
                f.write(image_bytes)

            # Remove background from the image
            success = remove_background(temp_input_path, temp_output_path)

            if not success:
                return jsonify({'error': 'Failed to remove background from image'}), 500

            # Read the processed image and convert back to base64
            with open(temp_output_path, 'rb') as f:
                processed_bytes = f.read()

            processed_base64 = base64.b64encode(processed_bytes).decode('utf-8')

            # Remove temporary files
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)

            return jsonify({
                'success': True,
                'processed_image': f'data:image/png;base64,{processed_base64}'
            })

        except Exception as processing_error:
            # Clean up temporary files if they exist
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)

            return jsonify({'error': f'Error processing image: {str(processing_error)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Failed to remove background: {str(e)}'}), 500


@app.route('/api/chatbot_query', methods=['POST'])
def api_chatbot_query():
    """API: Database query chatbot that can understand natural language questions"""
    try:
        data = request.json
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'error': 'No question provided'})

        conn = get_db()
        cursor = conn.cursor()

        try:
            # Try to process the query with our database logic
            response = process_database_query(question, cursor)

            # If the response is generic / unhelpful, try Kimi2 as fallback
            if "I couldn't understand" in response or "No" in response and ("found" in response or "not" in response):
                conn.close()  # Close the connection before calling Kimi2
                response = fallback_to_kimi2(question)
        except Exception as db_error:
            conn.close()
            # If database query fails, fallback to Kimi2
            response = fallback_to_kimi2(question)

        return jsonify({'result': response})

    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'})


def fallback_to_kimi2(question):
    """Fallback to Kimi2 when database query fails or doesn't return useful data"""
    try:
        # Import the required functions for Kimi2
        from generate_description import MOONSHOT_API_KEY

        # Only use Kimi2 if we have the API key
        if not MOONSHOT_API_KEY:
            return "I couldn't understand your question. The database doesn't contain the requested information, and AI fallback is not available."

        import json

        from generate_description import client

        # Create a system prompt to guide the AI
        system_prompt = """
        You are an intelligent assistant connected to a retail store database.
        The user asked a question about the store's data that couldn't be directly answered by the database.
        Based on the question, provide helpful information about retail operations, general knowledge related to the topic,
        or suggest ways the user could rephrase their question to get database results.
        If the question is about data that should be in the database, explain what specific information they should ask for.
        Keep your response helpful and professional.
        """

        user_message = f"User question: '{question}'\n\nThis question could not be answered with the current database. Provide helpful information or guidance."

        response = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content.strip()
        return f"Database couldn't answer this directly. AI suggests: {ai_response}"

    except Exception as e:
        return f"I couldn't understand your question. The database doesn't contain the requested information. Error with AI fallback: {str(e)}"


def process_database_query(question, cursor):
    """Process natural language questions and convert to SQL queries"""
    question_lower = question.lower()

    # Check if the question is about the app itself, not just database data
    knowledge_result = handle_knowledge_base_query(question_lower)
    if knowledge_result:
        return knowledge_result

    try:
        # Try to parse more complex queries with better NLP capabilities
        result = try_parse_complex_query(question_lower, cursor)
        if result is not None:
            return result
    except Exception:
        pass  # If complex parsing fails, continue to simpler parsing

    # Check for customer-related queries
    if any(word in question_lower for word in ['customer', 'client', 'buyer', 'purchaser']):
        if any(word in question_lower for word in ['count', 'how many', 'total number']):
            result = cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
            return f"There are {result} customers in the database."

        elif any(word in question_lower for word in ['list', 'show', 'display', 'all']):
            # Check for specific limit in the query (e.g., "show me all clients" vs "show me 20 customers")
            import re
            number_match = re.search(r'(\d+)\s*(customers|clients|people)', question_lower)
            limit = 10  # default
            if number_match:
                limit = int(number_match.group(1))
            elif 'all' in question_lower and any(word in ['all customers', 'all clients', 'all people']):
                # If asking for ALL customers, use a larger limit
                limit = 100  # large limit instead of all to prevent performance issues

            # Check for additional filters in the query
            if any(word in question_lower for word in ['active', 'active customers']):
                customers = cursor.execute('SELECT id, name, email, status FROM customers WHERE status = "active" LIMIT ?', (limit,)).fetchall()
                if customers:
                    customer_list = "<br>".join([f"ID: {c['id']}, Name: {c['name']}, Email: {c['email']}, Status: {c['status']}" for c in customers])
                    return f"Here are the active customers (showing {min(len(customers), limit)} of {len(customers)}):<br>{customer_list}"
            elif any(word in question_lower for word in ['inactive', 'cancelled', 'not active']):
                customers = cursor.execute('SELECT id, name, email, status FROM customers WHERE status != "active" LIMIT ?', (limit,)).fetchall()
                if customers:
                    customer_list = "<br>".join([f"ID: {c['id']}, Name: {c['name']}, Email: {c['email']}, Status: {c['status']}" for c in customers])
                    return f"Here are the inactive customers (showing {min(len(customers), limit)} of {len(customers)}):<br>{customer_list}"
            else:
                customers = cursor.execute('SELECT id, name, email FROM customers LIMIT ?', (limit,)).fetchall()
                if customers:
                    customer_list = "<br>".join([f"ID: {c['id']}, Name: {c['name']}, Email: {c['email']}" for c in customers])
                    return f"Here are the customers (showing {min(len(customers), limit)} of {len(customers)}):<br>{customer_list}"
            return "No customers found."

    # Check for product-related queries
    elif any(word in question_lower for word in ['product', 'item', 'goods', 'merchandise']):
        if any(word in question_lower for word in ['count', 'how many', 'total number']):
            result = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
            return f"There are {result} products in the database."

        elif any(word in question_lower for word in ['expensive', 'costly', 'pricy', 'high price']):
            # Check for specific price thresholds
            import re
            price_match = re.search(r'(\d+\.?\d*)', question)
            if price_match:
                price_threshold = float(price_match.group(1))
                products = cursor.execute('SELECT name, price FROM products WHERE price > ? ORDER BY price DESC LIMIT 10', (price_threshold,)).fetchall()
                if products:
                    product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}" for p in products])
                    return f"Products over ${price_threshold}:<br>{product_list}"
                else:
                    return f"No products found over ${price_threshold}."
            else:
                products = cursor.execute('SELECT name, price FROM products ORDER BY price DESC LIMIT 5').fetchall()
                if products:
                    product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}" for p in products])
                    return f"Most expensive products:<br>{product_list}"

        elif any(word in question_lower for word in ['cheap', 'inexpensive', 'low price', 'affordable']):
            # Check for specific price thresholds
            import re
            price_match = re.search(r'(\d+\.?\d*)', question)
            if price_match:
                price_threshold = float(price_match.group(1))
                products = cursor.execute('SELECT name, price FROM products WHERE price < ? ORDER BY price ASC LIMIT 10', (price_threshold,)).fetchall()
                if products:
                    product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}" for p in products])
                    return f"Products under ${price_threshold}:<br>{product_list}"
                else:
                    return f"No products found under ${price_threshold}."
            else:
                products = cursor.execute('SELECT name, price FROM products ORDER BY price ASC LIMIT 5').fetchall()
                if products:
                    product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}" for p in products])
                    return f"Least expensive products:<br>{product_list}"

        elif any(word in question_lower for word in ['low stock', 'out of stock', 'stock low']):
            products = cursor.execute('SELECT name, stock_quantity FROM products WHERE stock_quantity < 5 ORDER BY stock_quantity ASC LIMIT 10').fetchall()
            if products:
                product_list = "<br>".join([f"Product: {p['name']}, Stock: {p['stock_quantity']}" for p in products])
                return f"Products with very low stock:<br>{product_list}"
            else:
                return "No products with low stock found."

        elif any(word in question_lower for word in ['list', 'show', 'display', 'all']):
            # Check for specific limit in the query (e.g., "show me all products" vs "show me 20 products")
            import re
            number_match = re.search(r'(\d+)\s*(products|items)', question_lower)
            limit = 10  # default
            if number_match:
                limit = int(number_match.group(1))
            elif 'all' in question_lower and 'all products' in question_lower:
                # If asking for ALL products, use a larger limit or remove limit entirely
                limit = 100  # large limit instead of all to prevent performance issues

            # Check for category filters
            if 'category' in question_lower or any(category in question_lower for category in ['electronics', 'clothing', 'food', 'books', 'toys']):
                category_match = next((cat for cat in ['electronics', 'clothing', 'food', 'books', 'toys'] if cat in question_lower), None)
                if category_match:
                    products = cursor.execute('SELECT name, price, stock_quantity, category FROM products WHERE category LIKE ? LIMIT ?', (f'%{category_match}%', limit)).fetchall()
                    if products:
                        product_list = "<br>".join([f"Product: {p['name']}, Category: {p['category']}, Price: ${p['price']:.2f}, Stock: {p['stock_quantity']}" for p in products])
                        return f"Products in category '{category_match}':<br>{product_list}"
                    else:
                        return f"No products found in category '{category_match}'."
            else:
                products = cursor.execute('SELECT name, price, stock_quantity FROM products LIMIT ?', (limit,)).fetchall()
                if products:
                    product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}, Stock: {p['stock_quantity']}" for p in products])
                    return f"Here are the products:<br>{product_list}"
            return "No products found."

    # Check for order-related queries
    elif any(word in question_lower for word in ['order', 'sale', 'purchase', 'transaction']):
        if any(word in question_lower for word in ['count', 'how many', 'total number']):
            result = cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
            return f"There are {result} orders in the database."

        elif any(word in question_lower for word in ['total', 'revenue', 'income', 'sales']):
            result = cursor.execute('SELECT SUM(total_amount) FROM orders WHERE status != "cancelled"').fetchone()[0]
            total = result if result else 0
            return f"The total revenue from orders is ${total:.2f}."

        elif any(word in question_lower for word in ['pending', 'waiting', 'not shipped']):
            orders = cursor.execute('SELECT o.id, c.name as customer_name, o.total_amount, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = "pending" LIMIT 10').fetchall()
            if orders:
                order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Date: {o['order_date']}" for o in orders])
                return f"Pending orders:<br>{order_list}"
            else:
                return "No pending orders found."

        elif any(word in question_lower for word in ['cancelled', 'canceled', 'not completed']):
            orders = cursor.execute('SELECT o.id, c.name as customer_name, o.total_amount, o.order_date, o.status FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = "cancelled" LIMIT 10').fetchall()
            if orders:
                order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Date: {o['order_date']}, Status: {o['status']}" for o in orders])
                return f"Cancelled orders:<br>{order_list}"
            else:
                return "No cancelled orders found."

        elif any(word in question_lower for word in ['list', 'show', 'display', 'all']):
            # Check if user specified a number of records to return
            import re
            number_match = re.search(r'(\d+)\s*(last|recent|first|next)', question_lower)
            limit = 10  # default
            if number_match:
                limit = int(number_match.group(1))

            # Check if user asked for orders with tracking numbers
            if 'tracking' in question_lower or 'tracking number' in question_lower:
                orders = cursor.execute('''
                    SELECT o.id, c.name as customer_name, o.total_amount, o.status, o.order_date, o.tracking_number
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE o.tracking_number IS NOT NULL AND o.tracking_number != ""
                    ORDER BY o.order_date DESC
                    LIMIT ?
                ''', (limit,)).fetchall()
                if orders:
                    order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Tracking: {o['tracking_number'] or 'N/A'}, Status: {o['status']}, Date: {o['order_date']}" for o in orders])
                    return f"Orders with tracking numbers:<br>{order_list}"
                else:
                    return "No orders with tracking numbers found."
            else:
                orders = cursor.execute('''
                    SELECT o.id, c.name as customer_name, o.total_amount, o.status, o.order_date
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    ORDER BY o.order_date DESC
                    LIMIT ?
                ''', (limit,)).fetchall()
                if orders:
                    order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Status: {o['status']}, Date: {o['order_date']}" for o in orders])
                    return f"Recent orders:<br>{order_list}"
                else:
                    return "No orders found."

    # Check for inventory/stock queries
    elif any(word in question_lower for word in ['stock', 'inventory', 'quantity', 'available']):
        if any(word in question_lower for word in ['low', 'below', 'less than', 'running out']):
            # Look for quantity threshold
            import re
            qty_match = re.search(r'(\d+)', question)
            threshold = int(qty_match.group(1)) if qty_match else 10
            products = cursor.execute('SELECT name, stock_quantity FROM products WHERE stock_quantity < ? ORDER BY stock_quantity ASC LIMIT 10', (threshold,)).fetchall()
            if products:
                product_list = "<br>".join([f"Product: {p['name']}, Stock: {p['stock_quantity']}" for p in products])
                return f"Products with low stock (below {threshold}):<br>{product_list}"
            else:
                return f"No products with stock below {threshold}."

        elif any(word in question_lower for word in ['count', 'how many', 'total']):
            result = cursor.execute('SELECT SUM(stock_quantity) FROM products').fetchone()[0]
            total = result if result else 0
            return f"The total inventory count is {total} items."

    return "I couldn't understand your question. You can ask about customers, products, orders, or inventory. For example: 'How many customers are there?', 'Show me expensive products', or 'What is the total revenue?'."


def try_parse_complex_query(question, cursor):
    """Try to parse more complex queries with better NLP capabilities"""
    # More sophisticated parsing logic with pattern matching
    import re

    # Pattern for customer queries with multiple conditions
    if 'customer' in question and ('name' in question or 'email' in question):
        # Handle specific customer lookups
        name_match = re.search(r'customer named (\w+)', question)
        if name_match:
            name = name_match.group(1)
            customer = cursor.execute('SELECT id, name, email, date_joined, status FROM customers WHERE name LIKE ?', (f'%{name}%',)).fetchone()
            if customer:
                return f"Customer found:<br>ID: {customer['id']}, Name: {customer['name']}, Email: {customer['email']}, Joined: {customer['date_joined']}, Status: {customer['status']}"
            else:
                return f"No customer found with name containing '{name}'."

    # Pattern for product queries
    if 'product' in question:
        # Look for specific product name
        name_match = re.search(r'product.*(?:named|called|is) (\w+)', question)
        if name_match:
            name = name_match.group(1)
            product = cursor.execute('SELECT name, price, stock_quantity, category, description FROM products WHERE name LIKE ?', (f'%{name}%',)).fetchone()
            if product:
                return f"Product found:<br>Name: {product['name']}, Category: {product['category']}, Price: ${product['price']:.2f}, Stock: {product['stock_quantity']}, Description: {product['description'][:100]}..."
            else:
                return f"No product found with name containing '{name}'."

        # Look for price range queries
        range_match = re.search(r'between (\d+\.?\d*) and (\d+\.?\d*)', question)
        if range_match:
            min_price = float(range_match.group(1))
            max_price = float(range_match.group(2))
            products = cursor.execute('SELECT name, price FROM products WHERE price >= ? AND price <= ? ORDER BY price', (min_price, max_price)).fetchall()
            if products:
                product_list = "<br>".join([f"Product: {p['name']}, Price: ${p['price']:.2f}" for p in products])
                return f"Products between ${min_price} and ${max_price}:<br>{product_list}"
            else:
                return f"No products found between ${min_price} and ${max_price}."

    # Pattern for order queries with date ranges
    if 'order' in question:
        if 'last' in question or 'recent' in question:
            # Handle "recent orders" or "last month" type queries
            if 'month' in question:
                # Look up recent orders
                orders = cursor.execute('''
                    SELECT o.id, c.name as customer_name, o.total_amount, o.order_date, o.status
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE o.order_date > date("now", "-1 month")
                    ORDER BY o.order_date DESC
                    LIMIT 10
                ''').fetchall()
                if orders:
                    order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Date: {o['order_date']}, Status: {o['status']}" for o in orders])
                    return f"Recent orders from last month:<br>{order_list}"
                else:
                    return "No recent orders found from last month."

        # Handle "orders in descending order" - this could mean by date, amount or ID
        elif 'descending' in question and 'order' in question:
            # Determine what to sort by
            sort_by = 'order_date'  # default
            if any(word in question for word in ['amount', 'price', 'total']):
                sort_by = 'total_amount'
            elif any(word in question for word in ['id', 'number']):
                sort_by = 'id'

            import re
            number_match = re.search(r'(\d+)', question)
            limit = 10  # default
            if number_match and 'last' not in question and 'recent' not in question and 'first' not in question:
                limit = int(number_match.group(1))

            query = f'''
                SELECT o.id, c.name as customer_name, o.total_amount, o.order_date, o.status
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.{sort_by} DESC
                LIMIT ?
            '''
            orders = cursor.execute(query, (limit,)).fetchall()
            if orders:
                order_list = "<br>".join([f"Order ID: {o['id']}, Customer: {o['customer_name']}, Amount: ${o['total_amount']:.2f}, Date: {o['order_date']}, Status: {o['status']}" for o in orders])
                return f"Orders sorted in descending order by {sort_by.replace('_', ' ')}:<br>{order_list}"
            else:
                return "No orders found."

    # Pattern for statistical queries
    if any(word in question for word in ['average', 'avg', 'mean']):
        if 'price' in question and 'product' in question:
            avg_price = cursor.execute('SELECT AVG(price) FROM products').fetchone()[0]
            return f"The average product price is ${avg_price:.2f}." if avg_price else "No products to calculate average price."
        elif 'amount' in question and 'order' in question:
            avg_amount = cursor.execute('SELECT AVG(total_amount) FROM orders').fetchone()[0]
            return f"The average order amount is ${avg_amount:.2f}." if avg_amount else "No orders to calculate average amount."

    # Pattern for min/max queries
    if any(word in question for word in ['highest', 'top', 'maximum', 'max']):
        if 'price' in question and 'product' in question:
            max_product = cursor.execute('SELECT name, price FROM products ORDER BY price DESC LIMIT 1').fetchone()
            if max_product:
                return f"The most expensive product is '{max_product['name']}' at ${max_product['price']:.2f}."

    if any(word in question for word in ['lowest', 'bottom', 'minimum', 'min']):
        if 'price' in question and 'product' in question:
            min_product = cursor.execute('SELECT name, price FROM products WHERE price > 0 ORDER BY price ASC LIMIT 1').fetchone()
            if min_product:
                return f"The least expensive product is '{min_product['name']}' at ${min_product['price']:.2f}."

    # More complex customer queries
    if 'best customer' in question or 'top customer' in question:
        # Find customer with most orders
        best_customer = cursor.execute('''
            SELECT c.name, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
            LIMIT 1
        ''').fetchone()

        if best_customer:
            return f"The best customer is '{best_customer['name']}' with {best_customer['order_count']} orders, total spent: ${best_customer['total_spent']:.2f}."

    return None  # Return None if this function couldn't handle the query


INVOICE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">

<head>
    <meta charset="UTF-8">
    <title>VAT Invoice {{ invoice.invoice_number }}</title>
    <style>
        @page {
            margin: 2cm;
        }
        @media print {
            body {
                font-size: 11pt;
                color: black;
                background: white;
            }
            .no-print {
                display: none !important;
            }
        }

        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
            margin: 0;
            padding: 20px;
        }

        .invoice-container {
            max-width: 21cm;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }

        .invoice-header {
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }

        .invoice-header h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
            font-size: 24px;
            text-align: center;
        }

        .invoice-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .invoice-info div {
            flex: 1;
        }

        .invoice-parties {
            display: flex;
            gap: 40px;
            margin-bottom: 30px;
        }

        .party {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }

        .party h3 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }

        .invoice-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 13px;
        }

        .invoice-table th {
            background-color: #34495e;
            color: white;
            padding: 10px;
            text-align: left;
            border: 1px solid #333;
        }

        .invoice-table td {
            padding: 8px 10px;
            border: 1px solid #ddd;
            vertical-align: top;
        }

        .invoice-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        .invoice-totals {
            margin-top: 20px;
            text-align: right;
        }

        .totals-table {
            width: 300px;
            float: right;
            border-collapse: collapse;
            border: 1px solid #333;
        }

        .totals-table th, .totals-table td {
            padding: 10px;
            text-align: right;
            border: 1px solid #ddd;
        }

        .totals-table th {
            background-color: #34495e;
            color: white;
        }

        .total-row {
            background-color: #f8f9fa !important;
            font-weight: bold;
        }

        .total-row td {
            font-weight: bold !important;
            color: #000 !important;
        }

        .total-amount {
            font-size: 18px !important;
            font-weight: bold !important;
            color: #000 !important;
            display: inline !important;
        }

        .no-print {
            margin-top: 20px;
            text-align: center;
        }

        .no-print button {
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .no-print button:hover {
            background-color: #2980b9;
        }

        .clear {
            clear: both;
        }
    </style>
</head>

<body>
    <div class="invoice-container">
        <div class="invoice-header">
            <h1>VAT Invoice</h1>
            <div class="invoice-info">
                <div>
                    <p><strong>Invoice No:</strong> {{ invoice.invoice_number }}</p>
                    <p><strong>Issue Date:</strong> {{ invoice.issue_date.strftime('%Y-%m-%d') }}</p>
                    <p><strong>Supply Date:</strong> {{ invoice.supply_date.strftime('%Y-%m-%d') }}</p>
                    {% if invoice.payment_due_date %}
                    <p><strong>Payment Due Date:</strong> {{ invoice.payment_due_date.strftime('%Y-%m-%d') }}</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="invoice-parties">
            <div class="party">
                <h3>Seller:</h3>
                <p><strong>{{ invoice.supplier_name }}</strong><br>
                {{ invoice.supplier_address }}<br>
                NIP: {{ invoice.supplier_nip }}</p>
            </div>
            <div class="party">
                <h3>Buyer:</h3>
                <p><strong>{{ invoice.customer_name }}</strong><br>
                {{ invoice.customer_address }}{% if invoice.customer_nip %}<br>
                NIP: {{ invoice.customer_nip }}{% endif %}</p>
            </div>
        </div>

        <div>
            <h3>Invoice Items:</h3>
            <table class="invoice-table">
                <thead>
                    <tr>
                        <th>No.</th>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit Price (Net)</th>
                        <th>Discount</th>
                        <th>VAT (%)</th>
                        <th>Net Value</th>
                        <th>VAT</th>
                        <th>Gross Value</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in invoice.items %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ item.item }}</td>
                        <td align="right">{{ item.quantity }}</td>
                        <td align="right">{{ "%.2f"|format(item.unit_price_net) }}</td>
                        <td align="right">{{ "%.2f"|format(item.discount) }}%</td>
                        <td align="right">{{ "%.2f"|format(item.vat_rate * 100) }}%</td>
                        <td align="right">{{ "%.2f"|format(item.net_total) }}</td>
                        <td align="right">{{ "%.2f"|format(item.vat_amount) }}</td>
                        <td align="right">{{ "%.2f"|format(item.gross_total) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="clear"></div>

        <div class="invoice-totals">
            <table class="totals-table">
                <tr>
                    <th colspan="2">Summary</th>
                </tr>
                <tr>
                    <td>Net Total:</td>
                    <td align="right">{{ invoice.overall_net_total|round(2) }} {{ invoice.currency }}</td>
                </tr>
                <tr>
                    <td>VAT Total:</td>
                    <td align="right">{{ invoice.overall_vat_amount|round(2) }} {{ invoice.currency }}</td>
                </tr>
                <tr class="total-row">
                    <td><strong>Amount Due:</strong></td>
                    <td align="right"><strong>{{ invoice.overall_gross_total|round(2) }} {{ invoice.currency }}</strong></td>
                </tr>
            </table>
        </div>

        <div class="no-print">
            <button onclick="window.print()">Print Invoice</button>
        </div>
    </div>
</body>

</html>
"""

@app.route('/generate_invoice', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print(f"Received webhook data: {data}")
        process_data(data)
        return jsonify({"message": "Webhook received!"}), 200
    else:
        return jsonify({"message": "Only POST requests are accepted!"}), 400

def process_data(data):
    pass

def generate_invoice_pdf_bytes(invoice):
    """Generate PDF bytes for an invoice."""
    if HTML is None:
        # If weasyprint is not available, return a simple error
        print("Cannot generate PDF: weasyprint not installed")
        return b"PDF generation not available - install weasyprint package"

    rendered_html = render_template_string(INVOICE_TEMPLATE, invoice=invoice)
    # print(rendered_html)
    html = HTML(string=rendered_html)
    pdf_bytes = html.write_pdf()

    return pdf_bytes

def send_invoice_email(customer_email, invoice, pdf_bytes):
    """Send invoice as email attachment."""
    # Email configuration loaded from .env file
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.poczta.onet.pl')
    smtp_port = int(os.environ.get('SMTP_PORT', 465))
    sender_email = os.environ.get('SENDER_EMAIL', 'onefront@op.pl')
    sender_password = os.environ.get('SENDER_PASSWORD')

    if not sender_password:
        raise ValueError("SENDER_PASSWORD not set in .env file")

    print(customer_email)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = f"Invoice {invoice.invoice_number}"

    # Email body
    body = f"""
    Dear Customer,\n
    Please find attached invoice no. {invoice.invoice_number} for the amount of {invoice.overall_gross_total} {invoice.currency}.\n
    Invoice Details:\n
    Seller: {invoice.supplier_name}\n
    Buyer: {invoice.customer_name}\n
    Payment Due Date: {invoice.payment_due_date}\n
    \nThank you for your business!\n
    Team {invoice.supplier_name}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
    )
    msg.attach(part)
    # print(msg)

    try:
        print("1131")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        print("1137")
        server.login(sender_email, sender_password)

        print("1140")
        text = msg.as_string()
        print(text)
        server.sendmail(sender_email, customer_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@app.route('/invoice/<int:invoice_id>')
def show_invoice(invoice_id):
    """Display invoice by ID from database"""
    conn = get_db()
    cursor = conn.cursor()

    # Get invoice details from database
    invoice_record = cursor.execute('''
        SELECT i.*, o.id as order_id, c.name as customer_name, c.email as customer_email,
               c.address as customer_address, c.nip as customer_nip
        FROM invoices i
        JOIN orders o ON i.order_id = o.id
        JOIN customers c ON o.customer_id = c.id
        WHERE i.id = ?
    ''', (invoice_id,)).fetchone()

    if not invoice_record:
        conn.close()
        return "Invoice not found", 404

    # Get invoice items
    order_items = cursor.execute('''
        SELECT oi.*, p.name as product_name, p.vat_rate
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (invoice_record['order_id'],)).fetchall()

    conn.close()

    # Recreate invoice items
    invoice_items = []
    for item in order_items:
        vat_rate = item['vat_rate'] if item['vat_rate'] is not None else 0.23
        invoice_item = calculate_invoice_item(
            item_name=item['product_name'],
            quantity=item['quantity'],
            unit_price_gross=item['unit_price'],
            vat_rate=vat_rate,
            discount=0.0
        )
        invoice_items.append(invoice_item)

    # Calculate totals
    overall_net_total = sum(item.net_total for item in invoice_items)
    overall_vat_amount = sum(item.vat_amount for item in invoice_items)
    overall_gross_total = sum(item.gross_total for item in invoice_items)

    # Parse dates from strings if needed
    from datetime import datetime as dt
    issue_date = invoice_record['issue_date']
    if isinstance(issue_date, str):
        issue_date = dt.strptime(issue_date, '%Y-%m-%d').date()

    supply_date = invoice_record['supply_date']
    if isinstance(supply_date, str):
        supply_date = dt.strptime(supply_date, '%Y-%m-%d').date()

    # Create invoice object
    invoice = Invoice(
        invoice_number=invoice_record['invoice_number'],
        issue_date=issue_date,
        supply_date=supply_date,
        supplier_name=app.config['SUPPLIER_NAME'],
        supplier_address=app.config['SUPPLIER_ADDRESS'],
        supplier_nip=app.config['SUPPLIER_NIP'],
        customer_name=invoice_record['customer_name'],
        customer_address=invoice_record['customer_address'] or 'Address not provided',
        customer_nip=invoice_record['customer_nip'],
        items=invoice_items,
        overall_net_total=round(overall_net_total, 2),
        overall_vat_amount=round(overall_vat_amount, 2),
        overall_gross_total=round(overall_gross_total, 2)
    )

    format_type = request.args.get('format', 'html')
    if format_type == 'pdf':
        # Generate PDF
        pdf_bytes = generate_invoice_pdf_bytes(invoice)
        # Return as downloadable PDF
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
        return response
    else:
        # Default to HTML
        return render_template_string(INVOICE_TEMPLATE, invoice=invoice)

@app.route('/orders/<int:order_id>/invoice/download')
def download_invoice_by_order(order_id):
    """Download invoice PDF by order ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Get invoice details from database
        invoice_record = cursor.execute('''
            SELECT i.*, o.id as order_id, c.name as customer_name, c.email as customer_email,
                   c.address as customer_address, c.nip as customer_nip
            FROM invoices i
            JOIN orders o ON i.order_id = o.id
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        ''', (order_id,)).fetchone()

        if not invoice_record:
            conn.close()
            return "Invoice not found for this order", 404

        # Get invoice items
        order_items = cursor.execute('''
            SELECT oi.*, p.name as product_name, p.vat_rate
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (invoice_record['order_id'],)).fetchall()

        conn.close()

        # Recreate invoice items
        invoice_items = []
        for item in order_items:
            vat_rate = item['vat_rate'] if item['vat_rate'] is not None else 0.23
            invoice_item = calculate_invoice_item(
                item_name=item['product_name'],
                quantity=item['quantity'],
                unit_price_gross=item['unit_price'],
                vat_rate=vat_rate,
                discount=0.0
            )
            invoice_items.append(invoice_item)

        # Calculate totals
        overall_net_total = sum(item.net_total for item in invoice_items)
        overall_vat_amount = sum(item.vat_amount for item in invoice_items)
        overall_gross_total = sum(item.gross_total for item in invoice_items)

        print(f"DEBUG: Calculated totals - Net: {overall_net_total}, VAT: {overall_vat_amount}, Gross: {overall_gross_total}")
        print(f"DEBUG: Number of items: {len(invoice_items)}")
        for idx, item in enumerate(invoice_items):
            print(f"DEBUG: Item {idx}: {item.item}, qty={item.quantity}, gross_total={item.gross_total}")

        # Parse dates from strings if needed
        from datetime import datetime as dt
        issue_date = invoice_record['issue_date']
        if isinstance(issue_date, str):
            issue_date = dt.strptime(issue_date, '%Y-%m-%d').date()

        supply_date = invoice_record['supply_date']
        if isinstance(supply_date, str):
            supply_date = dt.strptime(supply_date, '%Y-%m-%d').date()

        # Create invoice object
        invoice = Invoice(
            invoice_number=invoice_record['invoice_number'],
            issue_date=issue_date,
            supply_date=supply_date,
            supplier_name=app.config['SUPPLIER_NAME'],
            supplier_address=app.config['SUPPLIER_ADDRESS'],
            supplier_nip=app.config['SUPPLIER_NIP'],
            customer_name=invoice_record['customer_name'],
            customer_address=invoice_record['customer_address'] or 'Address not provided',
            customer_nip=invoice_record['customer_nip'],
            items=invoice_items,
            overall_net_total=round(overall_net_total, 2),
            overall_vat_amount=round(overall_vat_amount, 2),
            overall_gross_total=round(overall_gross_total, 2)
        )

        # Generate PDF
        print(f"Generating PDF for invoice {invoice.invoice_number}")
        print(f"DEBUG: Invoice object values:")
        print(f"  - overall_net_total: {invoice.overall_net_total}")
        print(f"  - overall_vat_amount: {invoice.overall_vat_amount}")
        print(f"  - overall_gross_total: {invoice.overall_gross_total}")
        print(f"  - currency: {invoice.currency}")
        pdf_bytes = generate_invoice_pdf_bytes(invoice)
        print(f"PDF generated, size: {len(pdf_bytes)} bytes")

        # Return as downloadable PDF
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
        return response
    except Exception as e:
        print(f"Error generating invoice PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error generating invoice PDF: {str(e)}", 500

# Update the generate_invoice_for_order function to handle PDF generation and email
# ==================== TRACKING ROUTES ====================

@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    """Tracking page for package tracking"""
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number', '').strip()

        if not tracking_number:
            return render_template('tracking.html', error="Please enter a tracking number")

        # First create tracking in TrackingMore
        create_response = create_tracking(tracking_number)

        if not create_response.get('success'):
            return render_template('tracking.html', error=create_response.get('message', 'Failed to create tracking'))

        # Then get tracking information
        tracking_info = get_tracking_info(tracking_number)

        if not tracking_info.get('success'):
            return render_template('tracking.html', error=tracking_info.get('message', 'Failed to get tracking information'))

        tracking_data = tracking_info.get('data', {})
        return render_template('tracking.html', tracking_data=tracking_data, tracking_number=tracking_number)

    # If there's a tracking number in the URL, still render the template with it for the JavaScript to handle
    tracking_number = request.args.get('tracking_number', '').strip()
    return render_template('tracking.html', tracking_number=tracking_number)

def create_tracking(tracking_number, courier_code='inpost-paczkomaty'):
    """Create tracking entry in TrackingMore API"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Tracking-Api-Key': 'prdcbr1w-i59q-d872-0uvm-9u7856drn04n'
    }

    data = {
        'tracking_number': tracking_number,
        'courier_code': courier_code
    }

    try:
        response = requests.post(
            'https://api.trackingmore.com/v4/trackings/create',
            headers=headers,
            json=data
        )

        result = response.json()
        # The API returns status in meta.code, not root code
        meta_code = result.get('meta', {}).get('code')

        if meta_code == 200 or meta_code == 4101:  # 4101 means already exists, which is fine
            return {'success': True, 'data': result}
        elif response.status_code == 200:
            return {'success': True, 'data': result}
        else:
            message = result.get('meta', {}).get('message', f'API request failed with status {response.status_code}')
            return {'success': False, 'message': message}
    except Exception as e:
        return {'success': False, 'message': f'Error creating tracking: {str(e)}'}

def get_tracking_info(tracking_number):
    """Get tracking information from TrackingMore API"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Tracking-Api-Key': 'prdcbr1w-i59q-d872-0uvm-9u7856drn04n'
    }

    url = f'https://api.trackingmore.com/v4/trackings/get?tracking_numbers={tracking_number}'

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            meta_code = result.get('meta', {}).get('code')

            if meta_code == 200:
                # The tracking data is in the 'data' array
                trackings = result.get('data', [])
                if trackings:
                    tracking_data = trackings[0]  # Get first tracking object
                    return {'success': True, 'data': tracking_data}
                else:
                    return {'success': False, 'message': 'No tracking data found'}
            else:
                message = result.get('meta', {}).get('message', 'Error getting tracking information')
                return {'success': False, 'message': message}
        else:
            return {'success': False, 'message': f'API request failed with status {response.status_code}'}
    except Exception as e:
        return {'success': False, 'message': f'Error getting tracking information: {str(e)}'}

@app.route('/api/track', methods=['POST'])
def api_track():
    """API endpoint for tracking packages via AJAX"""
    tracking_number = request.json.get('tracking_number', '').strip()

    if not tracking_number:
        return jsonify({'success': False, 'message': 'Please enter a tracking number'})

    # First create tracking in TrackingMore
    create_response = create_tracking(tracking_number)

    if not create_response.get('success'):
        return jsonify({'success': False, 'message': create_response.get('message', 'Failed to create tracking')})

    # Then get tracking information
    tracking_info = get_tracking_info(tracking_number)

    if not tracking_info.get('success'):
        return jsonify({'success': False, 'message': tracking_info.get('message', 'Failed to get tracking information')})

    tracking_data = tracking_info.get('data', {})
    return jsonify({'success': True, 'data': tracking_data, 'tracking_number': tracking_number})

@app.route('/orders/<int:order_id>/generate_and_send_invoice', methods=['POST'])
def generate_and_send_invoice_for_order(order_id):
    """Generate invoice for order and send it to customer via email."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if invoice already exists for this order
    existing_invoice = cursor.execute(
        'SELECT invoice_number FROM invoices WHERE order_id = ?',
        (order_id,)
    ).fetchone()

    if existing_invoice:
        conn.close()
        return jsonify({
            'success': False,
            'error': f'Invoice already exists: {existing_invoice["invoice_number"]}'
        }), 400

    order = cursor.execute('''
        SELECT o.*, c.name as customer_name, c.email as customer_email,
               c.address as customer_address, c.nip as customer_nip
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()

    if not order:
        conn.close()
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    # Fetch order items with product details
    order_items = cursor.execute('''
        SELECT oi.*, p.name as product_name, p.vat_rate
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()

    if not order_items:
        conn.close()
        return jsonify({'success': False, 'error': 'No items found in order'}), 400

    invoice_number = generate_invoice_number()

    invoice_items = []
    for item in order_items:
        # Use the product's VAT rate if available, otherwise default to 23%
        vat_rate = item['vat_rate'] if item['vat_rate'] is not None else 0.23
        invoice_item = calculate_invoice_item(
            item_name=item['product_name'],
            quantity=item['quantity'],
            unit_price_gross=item['unit_price'],
            vat_rate=vat_rate,
            discount=0.0
        )
        invoice_items.append(invoice_item)

    # Calculate totals
    overall_net_total = sum(item.net_total for item in invoice_items)
    overall_vat_amount = sum(item.vat_amount for item in invoice_items)
    overall_gross_total = sum(item.gross_total for item in invoice_items)

    invoice = Invoice(
        invoice_number=invoice_number,
        issue_date=date.today(),
        supply_date=datetime.strptime(order['order_date'].split('.')[0].replace(" ", "T"), '%Y-%m-%dT%H:%M:%S').date() if order['order_date'] else date.today(),
        supplier_name=app.config['SUPPLIER_NAME'],
        supplier_address=app.config['SUPPLIER_ADDRESS'],
        supplier_nip=app.config['SUPPLIER_NIP'],
        customer_name=order['customer_name'],
        customer_address=order['customer_address'] or 'Address not provided',
        customer_nip=order['customer_nip'],
        items=invoice_items,
        overall_net_total=round(overall_net_total, 2),
        overall_vat_amount=round(overall_vat_amount, 2),
        overall_gross_total=round(overall_gross_total, 2)
    )

    pdf_bytes = generate_invoice_pdf_bytes(invoice)

    # Save invoice to database
    cursor.execute('''
        INSERT INTO invoices (order_id, invoice_number, issue_date, supply_date)
        VALUES (?, ?, ?, ?)
    ''', (order_id, invoice_number, invoice.issue_date, invoice.supply_date))
    conn.commit()

    email_sent = False
    if order['customer_email']:
        email_sent = send_invoice_email(order['customer_email'], invoice, pdf_bytes)

    conn.close()

    # Convert invoice to dict for JSON response
    invoice_dict = asdict(invoice)

    return jsonify({
        'success': True,
        'invoice_number': invoice_number,
        'invoice': invoice_dict,
        'email_sent': email_sent,
        'pdf_generated': True
    })


@app.route('/documentation')
def documentation():
    """Documentation page for the One Front system"""
    return render_template('documentation.html')

# ==================== PREDICTION ROUTES ====================

@app.route('/predictions')
def predictions():
    """Predictions dashboard page"""
    return render_template('predictions.html')



@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API: Make predictions using trained models"""
    try:
        data = request.json
        store_id = data.get('store_id', 1)
        target = data.get('target', 'Sales')  # Sales or Customers
        horizon = data.get('horizon', 'day')  # day, week, month

        model_key = f"{target}_{horizon}"

        if model_key not in loaded_models:
            return jsonify({
                'success': False,
                'error': f'Model {model_key} not loaded'
            }), 400

        model_data = loaded_models[model_key]
        model = model_data['model']
        scaler = model_data['scaler']
        features = model_data['features']

        # Create dummy features based on the feature list
        # In a real scenario, you would fetch actual historical data
        feature_values = {}

        # Base features with default values
        feature_values['Store'] = store_id
        feature_values['DayOfWeek'] = datetime.now().weekday()
        feature_values['Open'] = 1
        feature_values['Promo'] = 0
        feature_values['SchoolHoliday'] = 0
        feature_values['StoreType_enc'] = 1
        feature_values['Assortment_enc'] = 1
        feature_values['CompetitionDistance'] = 1000
        feature_values['Promo2'] = 0
        feature_values['Year'] = datetime.now().year
        feature_values['Month'] = datetime.now().month
        feature_values['Day'] = datetime.now().day
        feature_values['DayOfWeek_num'] = datetime.now().weekday()
        feature_values['WeekOfYear'] = datetime.now().isocalendar()[1]
        feature_values['Quarter'] = (datetime.now().month - 1) // 3 + 1

        # Get historical features from actual data
        context_window = model_data.get('context_window', 30)
        hist_features = get_store_historical_features(store_id, target, context_window)

        # Fill in features from historical data or use deterministic defaults
        if hist_features:
            for key, value in hist_features.items():
                if key not in feature_values:
                    feature_values[key] = value

        # For remaining features, use deterministic defaults based on store_id
        # This ensures predictions are consistent for the same store
        base_value = 5000 if target == 'Sales' else 500
        # Use store_id as seed for deterministic "random" values
        deterministic_factor = (store_id % 100) / 100.0  # 0.00 to 0.99

        for feature in features:
            if feature not in feature_values:
                if 'lag' in feature:
                    feature_values[feature] = base_value * (0.9 + deterministic_factor * 0.2)
                elif 'rolling_mean' in feature:
                    feature_values[feature] = base_value * (0.95 + deterministic_factor * 0.1)
                elif 'rolling_std' in feature:
                    feature_values[feature] = base_value * 0.1
                elif 'rolling_max' in feature:
                    feature_values[feature] = base_value * 1.2
                elif 'rolling_min' in feature:
                    feature_values[feature] = base_value * 0.8
                elif 'ema' in feature:
                    feature_values[feature] = base_value * (0.95 + deterministic_factor * 0.1)
                else:
                    feature_values[feature] = 0

        # Create feature array in correct order
        X = np.array([[feature_values[f] for f in features]])

        # Scale and predict
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]

        # Get model metrics
        metrics = model_data.get('metrics', {})

        # Calculate confidence interval (simple approach)
        mape = metrics.get('MAPE', 10)
        confidence_lower = prediction * (1 - mape / 100)
        confidence_upper = prediction * (1 + mape / 100)

        return jsonify({
            'success': True,
            'prediction': float(prediction),
            'confidence_interval': {
                'lower': float(confidence_lower),
                'upper': float(confidence_upper)
            },
            'metrics': {
                'MAE': metrics.get('MAE', 0),
                'RMSE': metrics.get('RMSE', 0),
                'R2': metrics.get('R2', 0),
                'MAPE': metrics.get('MAPE', 0)
            },
            'context_window': model_data.get('context_window', 0)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/product_price_prediction', methods=['POST'])
def api_product_price_prediction():
    """API: Predict price changes for products using pre-trained XGBoost model"""
    global loaded_price_model, loaded_feature_cols, loaded_label_encoders

    try:
        # Check if models are loaded
        if loaded_price_model is None or loaded_feature_cols is None or loaded_label_encoders is None:
            return jsonify({
                'success': False,
                'error': 'Price prediction model not loaded'
            }), 500

        data = request.json
        product_id = data.get('product_id')

        # Get the selected product from the database
        conn = get_db()
        cursor = conn.cursor()
        product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()

        if not product:
            return jsonify({
                'success': False,
                'error': f'Product with id {product_id} not found'
            }), 400

        product_name = product[1]  # product name is at index 1
        current_price = float(product[3])  # price is at index 3

        # Load historical data from the retail prices CSV to create predictions
        retail_df = pd.read_csv('products_prices/Retail_Prices_of _Products.csv')

        # Prepare the data structure exactly as in the notebook
        df = retail_df.copy()
        if 'Value' in df.columns:
            df = df.rename(columns={'Value': 'VALUE'})
        df['date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2) + '-01')
        df = df.sort_values(['GEO', 'Product Category', 'Products', 'Essential', 'date']).reset_index(drop=True)
        df = df[['GEO', 'Product Category', 'Products', 'Essential', 'date', 'VALUE']].dropna(subset=['VALUE'])

        # Filter for specific product - match exactly
        product_data = df[df['Products'].str.strip() == product_name.strip()]

        if len(product_data) == 0:
            # Try fuzzy matching if exact match fails
            product_data = df[df['Products'].str.contains(product_name, case=False, na=False)]

        if len(product_data) == 0:
            # If no historical data for this product in the CSV, use current price with minimal variation
            predictions = []
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            current_month_idx = datetime.now().month - 1

            for i in range(5):
                month_name = months[(current_month_idx + i) % 12]
                # Simple trend-based prediction
                predicted_price = current_price * (1.01 ** i)  # 1% growth per month

                predictions.append({
                    'month': month_name,
                    'predictedPrice': round(predicted_price, 2),
                    'confidenceLow': round(predicted_price * 0.95, 2),
                    'confidenceHigh': round(predicted_price * 1.05, 2)
                })

            return jsonify({
                'success': True,
                'product_id': product_id,
                'product_name': product_name,
                'predictions': predictions,
                'note': 'No historical data found - using simple trend prediction'
            })

        # Encode categorical columns using pre-loaded label encoders
        categorical_cols = ['GEO', 'Product Category', 'Products', 'Essential']
        for col in categorical_cols:
            df[col] = df[col].astype(str)
            if col in loaded_label_encoders:
                # Handle unknown categories
                def safe_transform(val, encoder):
                    if val in encoder.classes_:
                        return encoder.transform([val])[0]
                    else:
                        # Return encoding of first class for unknown values
                        return 0

                df[col + '_encoded'] = df[col].apply(lambda x: safe_transform(x, loaded_label_encoders[col]))
            else:
                # If encoder not available, create a simple numeric encoding
                df[col + '_encoded'] = pd.Categorical(df[col]).codes

        # Group keys and encoded keys
        group_keys = ['GEO', 'Product Category', 'Products', 'Essential']
        encoded_keys = [col + '_encoded' for col in categorical_cols]

        # Feature engineering function (EXACTLY as in notebook)
        def build_advanced_features(group):
            group = group.set_index('date').sort_index()
            full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq='MS')
            group = group.reindex(full_range)

            # Basic lags
            for lag in [1, 2, 3, 4, 6, 12]:
                group[f'lag_{lag}'] = group['VALUE'].shift(lag)

            # Rolling stats
            group['rolling_mean_3'] = group['VALUE'].shift(1).rolling(3, min_periods=1).mean()
            group['rolling_mean_6'] = group['VALUE'].shift(1).rolling(6, min_periods=1).mean()
            group['rolling_std_3'] = group['VALUE'].shift(1).rolling(3, min_periods=1).std()
            group['rolling_cv_3'] = group['rolling_std_3'] / (group['rolling_mean_3'] + 1e-8)

            # Difference features
            group['diff_1'] = group['VALUE'].diff(1)
            group['diff_2'] = group['VALUE'].diff(2)

            # Percentage change features
            group['pct_change_1'] = group['VALUE'].pct_change(1)
            group['pct_change_3'] = group['VALUE'].pct_change(3)

            # Time features
            group['year'] = group.index.year
            group['month'] = group.index.month
            group['quarter'] = group.index.quarter
            group['month_sin'] = np.sin(2 * np.pi * group['month'] / 12)
            group['month_cos'] = np.cos(2 * np.pi * group['month'] / 12)

            # Linear & quadratic time trend
            group['time_idx'] = np.arange(len(group))
            group['time_trend'] = group['time_idx']
            group['time_trend_sq'] = group['time_idx'] ** 2

            return group.reset_index().rename(columns={'index': 'date'})

        # Apply feature engineering to ALL groups (not just product_data)
        feature_dfs = []
        for name, group in df.groupby(group_keys):
            if len(group) < 12:  # need at least 1 year
                continue
            feat_df = build_advanced_features(group)
            # Add encoded columns - get from the first row of the group
            for col in categorical_cols:
                feat_df[col] = group[col].iloc[0]
                feat_df[col + '_encoded'] = group[col + '_encoded'].iloc[0]
            feature_dfs.append(feat_df)

        if not feature_dfs:
            raise ValueError("Not enough data for feature engineering.")

        features_df = pd.concat(feature_dfs, ignore_index=True)

        # Clean data - fill NaN values with 0 for feature columns only
        feature_cols_list = loaded_feature_cols
        modeling_df = features_df.dropna(subset=['VALUE']).copy()

        # Ensure all feature columns exist
        for col in feature_cols_list:
            if col not in modeling_df.columns:
                modeling_df[col] = 0

        modeling_df[feature_cols_list] = modeling_df[feature_cols_list].fillna(0)

        # Get the most recent row for the selected product
        # Match based on the product name
        product_df = modeling_df[modeling_df['Products'] == product_data['Products'].iloc[0]].copy()

        if len(product_df) == 0:
            raise ValueError("No feature data available for this product")

        # Sort by date to get the most recent data
        product_df = product_df.sort_values('date')

        last_row = product_df.iloc[-1:][feature_cols_list].copy()
        last_value = product_df.iloc[-1]['VALUE']

        # Make predictions for next 5 months
        predictions = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Get current date from the last data point
        last_date = pd.to_datetime(product_df.iloc[-1]['date'])

        # Iterative prediction: each prediction updates features for the next
        current_features = last_row.copy()
        current_value = last_value

        for i in range(1, 6):
            # Calculate next month
            next_date = last_date + pd.DateOffset(months=i)
            next_month_idx = next_date.month - 1

            # Update time-based features
            current_features.loc[:, 'year'] = next_date.year
            current_features.loc[:, 'month_sin'] = np.sin(2 * np.pi * next_date.month / 12)
            current_features.loc[:, 'month_cos'] = np.cos(2 * np.pi * next_date.month / 12)
            current_features.loc[:, 'quarter'] = (next_date.month - 1) // 3 + 1
            current_features.loc[:, 'time_trend'] = current_features['time_trend'].values[0] + i
            current_features.loc[:, 'time_trend_sq'] = current_features['time_trend'].values[0] ** 2

            # Make prediction
            pred_value = loaded_price_model.predict(current_features[feature_cols_list])[0]
            pred_value = max(0.01, pred_value)  # Ensure positive

            # Update lag features for next iteration (shift values)
            if i < 5:  # Don't need to update on last iteration
                current_features.loc[:, 'lag_12'] = current_features['lag_6'].values[0] if i >= 6 else current_features['lag_12'].values[0]
                current_features.loc[:, 'lag_6'] = current_features['lag_4'].values[0] if i >= 6 else current_features['lag_6'].values[0]
                current_features.loc[:, 'lag_4'] = current_features['lag_3'].values[0] if i >= 4 else current_features['lag_4'].values[0]
                current_features.loc[:, 'lag_3'] = current_features['lag_2'].values[0] if i >= 3 else current_features['lag_3'].values[0]
                current_features.loc[:, 'lag_2'] = current_features['lag_1'].values[0] if i >= 2 else current_features['lag_2'].values[0]
                current_features.loc[:, 'lag_1'] = current_value

                # Update rolling features
                current_features.loc[:, 'rolling_mean_3'] = (current_value + current_features['lag_1'].values[0] + current_features['lag_2'].values[0]) / 3
                current_features.loc[:, 'rolling_mean_6'] = current_features['rolling_mean_3'].values[0]  # Approximate

                # Update diff and pct_change
                current_features.loc[:, 'diff_1'] = pred_value - current_value
                current_features.loc[:, 'pct_change_1'] = (pred_value - current_value) / (current_value + 1e-8)

                current_value = pred_value

            # Calculate confidence interval (5% based on typical model performance)
            confidence_range = pred_value * 0.05

            predictions.append({
                'month': months[next_month_idx],
                'predictedPrice': round(float(pred_value), 2),
                'confidenceLow': round(float(max(0.01, pred_value - confidence_range)), 2),
                'confidenceHigh': round(float(pred_value + confidence_range), 2)
            })

        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product_name,
            'predictions': predictions
        })

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/batch_predict', methods=['POST'])
def api_batch_predict():
    """API: Make batch predictions for all horizons"""
    try:
        data = request.json
        store_id = data.get('store_id', 1)

        results = {
            'sales': {},
            'customers': {}
        }

        for target in ['Sales', 'Customers']:
            for horizon in ['day', 'week', 'month']:
                model_key = f"{target}_{horizon}"

                if model_key not in loaded_models:
                    continue

                model_data = loaded_models[model_key]
                model = model_data['model']
                scaler = model_data['scaler']
                features = model_data['features']

                # Create features (same as single prediction)
                feature_values = {}
                feature_values['Store'] = store_id
                feature_values['DayOfWeek'] = datetime.now().weekday()
                feature_values['Open'] = 1
                feature_values['Promo'] = 0
                feature_values['SchoolHoliday'] = 0
                feature_values['StoreType_enc'] = 1
                feature_values['Assortment_enc'] = 1
                feature_values['CompetitionDistance'] = 1000
                feature_values['Promo2'] = 0
                feature_values['Year'] = datetime.now().year
                feature_values['Month'] = datetime.now().month
                feature_values['Day'] = datetime.now().day
                feature_values['DayOfWeek_num'] = datetime.now().weekday()
                feature_values['WeekOfYear'] = datetime.now().isocalendar()[1]
                feature_values['Quarter'] = (datetime.now().month - 1) // 3 + 1

                # Get historical features from actual data
                context_window = model_data.get('context_window', 30)
                hist_features = get_store_historical_features(store_id, target, context_window)

                # Fill in features from historical data or use deterministic defaults
                if hist_features:
                    for key, value in hist_features.items():
                        if key not in feature_values:
                            feature_values[key] = value

                # For remaining features, use deterministic defaults
                base_value = 5000 if target == 'Sales' else 500
                deterministic_factor = (store_id % 100) / 100.0

                for feature in features:
                    if feature not in feature_values:
                        if 'lag' in feature:
                            feature_values[feature] = base_value * (0.9 + deterministic_factor * 0.2)
                        elif 'rolling_mean' in feature:
                            feature_values[feature] = base_value * (0.95 + deterministic_factor * 0.1)
                        elif 'rolling_std' in feature:
                            feature_values[feature] = base_value * 0.1
                        elif 'rolling_max' in feature:
                            feature_values[feature] = base_value * 1.2
                        elif 'rolling_min' in feature:
                            feature_values[feature] = base_value * 0.8
                        elif 'ema' in feature:
                            feature_values[feature] = base_value * (0.95 + deterministic_factor * 0.1)
                        else:
                            feature_values[feature] = 0

                X = np.array([[feature_values[f] for f in features]])
                X_scaled = scaler.transform(X)
                prediction = model.predict(X_scaled)[0]

                metrics = model_data.get('metrics', {})
                mape = metrics.get('MAPE', 10)

                target_key = target.lower()
                results[target_key][horizon] = {
                    'value': float(prediction),
                    'confidence_lower': float(prediction * (1 - mape / 100)),
                    'confidence_upper': float(prediction * (1 + mape / 100)),
                    'mape': float(mape)
                }

        return jsonify({
            'success': True,
            'store_id': store_id,
            'timestamp': datetime.now().isoformat(),
            'predictions': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def handle_knowledge_base_query(question_lower):
    """Handle queries about the application itself using comprehensive knowledge base"""
    knowledge_base = get_knowledge_base()

    # Check FAQ first for exact or similar questions
    for category, faqs in knowledge_base.get('faq', {}).items():
        for faq_item in faqs:
            faq_question = faq_item['question'].lower()
            # Check if question is similar to FAQ
            if any(word in question_lower for word in faq_question.split() if len(word) > 3):
                # Additional check to ensure it's a good match
                common_words = set(question_lower.split()) & set(faq_question.split())
                if len(common_words) >= 2:
                    return faq_item['answer']

    # Check for specific feature explanation requests
    feature_keywords = {
        'customer_management': ['customer management', 'managing customers', 'customer feature'],
        'product_management': ['product management', 'managing products', 'product feature', 'inventory'],
        'order_management': ['order management', 'managing orders', 'order processing', 'order feature'],
        'invoice_system': ['invoice', 'invoicing', 'faktura'],
        'chatbot_assistant': ['chatbot', 'bot', 'assistant', 'ai helper'],
        'analytics_dashboard': ['dashboard', 'analytics', 'statistics', 'metrics', 'overview'],
        'interaction_tracking': ['interaction', 'customer interaction', 'communication tracking'],
        'multi_channel_integration': ['integration', 'shopify', 'woocommerce', 'multi-channel', 'sync']
    }

    for feature_key, keywords in feature_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            feature = knowledge_base['feature_explanations'].get(feature_key)
            if feature:
                response = f"{feature['title']}: {feature['description']}<br><br>"
                response += "<strong>Features:</strong><br>" + "<br>".join([f"• {f}" for f in feature['features'][:5]])
                if len(feature['features']) > 5:
                    response += f"<br>...and {len(feature['features']) - 5} more"
                return response

    # Check for "how to" questions
    how_to_keywords = {
        'add_customer': ['add customer', 'create customer', 'new customer'],
        'add_product': ['add product', 'create product', 'new product'],
        'add_order': ['add order', 'create order', 'new order', 'place order'],
        'edit_customer': ['edit customer', 'update customer', 'change customer'],
        'track_interactions': ['add interaction', 'track interaction', 'customer interaction', 'record interaction'],
        'generate_invoice': ['generate invoice', 'create invoice', 'make invoice'],
        'manage_inventory': ['manage inventory', 'track inventory', 'stock management', 'inventory management'],
        'use_integrations': ['use shopify', 'use woocommerce', 'sync products'],
        'understand_dashboard': ['use dashboard', 'understand dashboard', 'dashboard help'],
        'change_order_status': ['change status', 'update order status', 'order status'],
        'search_and_filter': ['search', 'filter', 'find']
    }

    for guide_key, keywords in how_to_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            guide = knowledge_base['how_to_guides'].get(guide_key)
            if guide:
                response = f"<strong>{guide['title']}</strong><br><br>"
                if 'steps' in guide:
                    response += "<strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])])
                if 'tips' in guide and len(guide['tips']) > 0:
                    response += "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])
                if 'description' in guide:
                    response += f"<br><br>{guide['description']}"
                if 'sections' in guide:
                    response += "<br><br><strong>Dashboard Sections:</strong><br>" + "<br>".join([f"• {section}" for section in guide['sections']])
                return response

    # Check for status information
    if 'status' in question_lower:
        if any(word in question_lower for word in ['customer', 'customers', 'client']):
            statuses = knowledge_base['common_features']['customer_statuses']
            return f"<strong>Customer Statuses:</strong><br>" + "<br>".join([f"• <strong>{s}</strong> - {desc}" for s, desc in [
                ('active', 'Regular customer'),
                ('inactive', 'Inactive customer'),
                ('blacklisted', 'Customer on blacklist'),
                ('prospect', 'Potential customer')
            ]])

        if any(word in question_lower for word in ['order', 'orders']):
            return f"<strong>Order Statuses:</strong><br>" + "<br>".join([f"• <strong>{s}</strong> - {desc}" for s, desc in [
                ('pending', 'Just created, awaiting processing'),
                ('processing', 'Being prepared'),
                ('shipped', 'Sent to customer'),
                ('delivered', 'Received by customer'),
                ('completed', 'Finalized'),
                ('cancelled', 'Cancelled order'),
                ('refunded', 'Money returned')
            ]])

    # Check for payment methods
    if any(word in question_lower for word in ['payment', 'pay', 'method']):
        methods = knowledge_base['common_features']['payment_methods']
        return f"<strong>Available Payment Methods:</strong><br>" + "<br>".join([f"• {m.replace('_', ' ').title()}" for m in methods])

    # Check for features list
    if any(word in question_lower for word in ['feature', 'function', 'capability', 'what can']):
        if any(word in question_lower for word in ['app', 'system', 'synder', 'crm', 'this']):
            features = knowledge_base['app_overview']['main_features']
            return f"<strong>Synder CRM Main Features:</strong><br>" + "<br>".join([f"• {f.title()}" for f in features])

    # Check for general app info
    if any(word in question_lower for word in ['what is', 'what does', 'tell me about']) and any(word in question_lower for word in ['app', 'application', 'system', 'synder', 'crm']):
        overview = knowledge_base['app_overview']
        return f"<strong>{overview['title']}</strong><br><br>{overview['description']}<br><br><strong>Main Features:</strong><br>" + "<br>".join([f"• {f.title()}" for f in overview['main_features'][:6]])

    # Check for navigation/where questions
    if any(word in question_lower for word in ['where is', 'where can', 'how to find', 'navigate']):
        if 'dashboard' in question_lower:
            dash_guide = knowledge_base['how_to_guides']['understand_dashboard']
            return f"The <strong>Dashboard</strong> is your main page at '/'. {dash_guide['description']}<br><br><strong>What you'll see:</strong><br>" + "<br>".join([f"• {s}" for s in dash_guide['sections'][:5]])
        elif 'customer' in question_lower:
            return "The <strong>Customers page</strong> is accessible from the navigation menu at '/customers'. Here you can view all customers, add new ones, and manage customer information."
        elif 'product' in question_lower:
            return "The <strong>Products page</strong> is accessible from the navigation menu at '/products'. Here you can view all products, manage inventory, and add new products."
        elif 'order' in question_lower:
            return "The <strong>Orders page</strong> is accessible from the navigation menu at '/orders'. Here you can view all orders, create new orders, and track order status."

    # Check for troubleshooting
    if any(word in question_lower for word in ['problem', 'issue', 'error', 'trouble', 'not working', 'help']):
        issues = knowledge_base['troubleshooting']['common_issues']
        return "<strong>Common Issues & Solutions:</strong><br>" + "<br>".join([f"• <strong>{issue['issue']}</strong>: {issue['solution']}" for issue in issues])

    # If not a knowledge base query, return None
    return None


@app.route('/api/app_chatbot', methods=['POST'])
def app_chatbot():
    """AI-powered chatbot that helps users understand and use the Synder CRM application"""
    try:
        data = request.json
        question_original = data.get('question', '').strip()
        question = question_original.lower()

        if not question:
            return jsonify({'result': 'Please ask a question about the application.'})

        # Get knowledge base
        knowledge_base = get_knowledge_base()

        # Try Kimi2 AI first for intelligent, natural responses
        if moonshot_available:
            kimi_response = generate_kb_response_with_kimi(question_original, knowledge_base)
            if kimi_response:
                return jsonify({'result': kimi_response})

        # Fallback to pattern matching if Kimi2 is unavailable or fails
        # Try knowledge base pattern matching
        knowledge_response = handle_knowledge_base_query(question)
        if knowledge_response:
            return jsonify({'result': knowledge_response})

        # Try common app questions patterns
        response = handle_app_questions(question)

        if response:
            return jsonify({'result': response})
        else:
            # If we can't answer the question, provide a helpful response with examples
            help_message = """<strong>I'm here to help you use Synder CRM!</strong><br><br>
            I can answer questions about:<br>
            • <strong>How to use features</strong> - "How do I add a customer?", "How to create an order?"<br>
            • <strong>Features & capabilities</strong> - "What features does the system have?", "Tell me about product management"<br>
            • <strong>Statuses & settings</strong> - "What are order statuses?", "What payment methods are available?"<br>
            • <strong>Navigation</strong> - "Where is the dashboard?", "How do I find products?"<br>
            • <strong>Troubleshooting</strong> - "I have an error", "Something is not working"<br>
            • <strong>Integrations</strong> - "How do I use Shopify?", "Tell me about WooCommerce sync"<br><br>
            Try asking me anything about how to use the system!"""
            return jsonify({'result': help_message})

    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'})


def handle_app_questions(question_lower):
    """Handle various application-related questions using knowledge base"""
    knowledge_base = get_knowledge_base()

    # Handle "how to" questions by pulling from the comprehensive guides
    if any(word in question_lower for word in ['how', 'add', 'create', 'new']):
        # Customer related
        if any(word in question_lower for word in ['customer', 'client']):
            guide = knowledge_base['how_to_guides']['add_customer']
            if 'edit' in question_lower or 'update' in question_lower or 'change' in question_lower:
                guide = knowledge_base['how_to_guides']['edit_customer']
            return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

        # Product related
        if any(word in question_lower for word in ['product', 'item']):
            guide = knowledge_base['how_to_guides']['add_product']
            return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

        # Order related
        if any(word in question_lower for word in ['order']):
            guide = knowledge_base['how_to_guides']['add_order']
            return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

    # Invoice questions
    if any(word in question_lower for word in ['invoice', 'faktura']):
        guide = knowledge_base['how_to_guides']['generate_invoice']
        return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

    # Integration questions
    if any(word in question_lower for word in ['shopify', 'woocommerce', 'integration', 'sync']):
        feature = knowledge_base['feature_explanations']['multi_channel_integration']
        return f"<strong>{feature['title']}</strong><br><br>{feature['description']}<br><br><strong>Features:</strong><br>" + "<br>".join([f"• {f}" for f in feature['features']])

    # Interaction tracking
    if any(word in question_lower for word in ['interaction', 'contact', 'communicate', 'track']):
        if 'customer' in question_lower:
            guide = knowledge_base['how_to_guides']['track_interactions']
            return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

    # Search and filter questions
    if any(word in question_lower for word in ['find', 'search', 'filter', 'locate']):
        guide = knowledge_base['how_to_guides']['search_and_filter']
        response = f"<strong>{guide['title']}</strong><br><br>"
        if 'customer' in question_lower:
            response += f"<strong>Customers:</strong> {guide['customers']}"
        elif 'product' in question_lower:
            response += f"<strong>Products:</strong> {guide['products']}"
        elif 'order' in question_lower:
            response += f"<strong>Orders:</strong> {guide['orders']}"
        else:
            response += f"<strong>Customers:</strong> {guide['customers']}<br>"
            response += f"<strong>Products:</strong> {guide['products']}<br>"
            response += f"<strong>Orders:</strong> {guide['orders']}"
        response += "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])
        return response

    # Help and support questions
    if any(word in question_lower for word in ['help', 'support', 'tutorial', 'guide', 'getting started']):
        overview = knowledge_base['app_overview']
        return f"<strong>Welcome to {overview['title']}</strong><br><br>{overview['description']}<br><br><strong>Main Features:</strong><br>" + "<br>".join([f"• {f.title()}" for f in overview['main_features']]) + "<br><br>Use the navigation menu to access different sections. Ask me specific questions about features like 'How do I add a product?' or 'What are order statuses?'"

    # Analytics and reporting
    if any(word in question_lower for word in ['report', 'analytics', 'data', 'statistics', 'insights', 'metrics']):
        feature = knowledge_base['feature_explanations']['analytics_dashboard']
        return f"<strong>{feature['title']}</strong><br><br>{feature['description']}<br><br><strong>Metrics Available:</strong><br>" + "<br>".join([f"• {m}" for m in feature['metrics']])

    # Inventory management
    if any(word in question_lower for word in ['inventory', 'stock', 'quantity']):
        guide = knowledge_base['how_to_guides']['manage_inventory']
        return f"<strong>{guide['title']}</strong><br><br><strong>Steps:</strong><br>" + "<br>".join([f"{i+1}. {step}" for i, step in enumerate(guide['steps'])]) + "<br><br><strong>Tips:</strong><br>" + "<br>".join([f"• {tip}" for tip in guide['tips']])

    # Background removal or photo questions
    if any(word in question_lower for word in ['photo', 'image', 'picture', 'background']):
        return "<strong>Product Photos</strong><br><br>You can upload multiple photos for each product when adding or editing products. The system includes an automatic background removal feature to create professional product images.<br><br><strong>To add photos:</strong><br>1. Go to Products page<br>2. Click 'Add Product' or edit an existing product<br>3. Upload your images<br>4. The system can automatically remove backgrounds<br>5. Save your product"

    # VAT or tax questions
    if any(word in question_lower for word in ['vat', 'tax', 'polski', 'polish']):
        feature = knowledge_base['feature_explanations']['invoice_system']
        return f"<strong>{feature['title']}</strong><br><br>{feature['description']}<br><br><strong>Features:</strong><br>" + "<br>".join([f"• {f}" for f in feature['features']])

    return None  # If no pattern matches


def generate_kb_response_with_kimi(question, knowledge_base):
    """Use Kimi2 API to generate intelligent responses using knowledge base as context"""
    try:
        # Check if Moonshot is available
        if not moonshot_available:
            return None

        # Prepare knowledge base context
        kb_context = {
            "app_overview": knowledge_base.get('app_overview', {}),
            "how_to_guides": {k: v for k, v in list(knowledge_base.get('how_to_guides', {}).items())[:5]},  # Limit to prevent token overflow
            "feature_explanations": knowledge_base.get('feature_explanations', {}),
            "common_features": knowledge_base.get('common_features', {}),
            "faq": knowledge_base.get('faq', {})
        }

        system_prompt = """You are a helpful assistant for the Synder CRM system. Your role is to help users understand and use the application.

IMPORTANT INSTRUCTIONS:
1. Use the knowledge base provided to answer questions accurately
2. Provide step-by-step instructions when users ask "how to" do something
3. Format your responses using HTML for better readability:
   - Use <strong> for headings and important terms
   - Use <br> for line breaks
   - Use bullet points with • for lists
4. Be concise but helpful
5. If the question is about a feature, explain what it does and how to use it
6. If you're not sure about something from the knowledge base, say so
7. Always be encouraging and helpful
8. Only answer questions about the Synder CRM application based on the knowledge base
9. Keep responses under 300 words unless providing step-by-step instructions

Available information in knowledge base:
- App overview and main features
- How-to guides for common tasks
- Feature explanations
- Payment methods and order/customer statuses
- FAQ and troubleshooting"""

        user_content = f"User question: {question}\n\nKnowledge Base:\n{json.dumps(kb_context, indent=2)}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = moonshot_client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Kimi2 error: {str(e)}")
        return None


# ==================== CHATBOT ROUTES ====================

# Moonshot API helper functions (using client initialized at top of file)
if moonshot_available:
    def generate_ai_insight(user_message, context_data):
        """Generate AI-powered insights using Moonshot API (Kimi)"""
        try:
            system_prompt = """
            You are an expert business and financial analyst for a CRM system.
            Analyze the customer order data and provide meaningful insights based on the user's query.
            Use the context data to provide accurate, actionable insights.
            Focus on patterns, trends, recommendations, and business intelligence.
            Be concise but informative, and include specific numbers and details when relevant.
            """

            user_content = f"User query: {user_message}\n\nContext data: {json.dumps(context_data, indent=2, default=str)}"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]

            response = moonshot_client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=messages,
                temperature=0.6,
                max_tokens=800
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"

    def get_crm_insights(user_message, cursor):
        """Get CRM-specific data for AI analysis"""
        # Get all orders from the main orders table
        orders_data = cursor.execute('''
            SELECT o.id, o.total_amount, o.status, o.order_date, o.payment_method,
                   c.name as customer_name, c.email, c.phone, c.loyalty_points,
                   COUNT(oi.id) as item_count,
                   GROUP_CONCAT(p.name) as product_names
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE o.total_amount IS NOT NULL
            GROUP BY o.id
            ORDER BY o.order_date DESC
            LIMIT 20
        ''').fetchall()

        # Convert to list of dicts for JSON serialization
        orders_list = [dict(order) for order in orders_data]

        # Get customer insights
        customer_stats = cursor.execute('''
            SELECT
                COUNT(*) as total_customers,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_customers,
                AVG(loyalty_points) as avg_loyalty_points
            FROM customers
        ''').fetchone()

        # Get product insights
        product_stats = cursor.execute('''
            SELECT
                COUNT(*) as total_products,
                AVG(price) as avg_price,
                MIN(stock_quantity) as min_stock,
                MAX(stock_quantity) as max_stock
            FROM products
        ''').fetchone()

        # Get revenue insights by status
        revenue_by_status = cursor.execute('''
            SELECT status, COUNT(*) as count, SUM(total_amount) as total_revenue
            FROM orders
            WHERE status != 'cancelled'
            GROUP BY status
        ''').fetchall()

        return {
            'orders': orders_list,
            'customer_stats': dict(customer_stats) if customer_stats else {},
            'product_stats': dict(product_stats) if product_stats else {},
            'revenue_by_status': [dict(status_row) for status_row in revenue_by_status],
        }

    # Use Moonshot API for enhanced responses
    def get_enhanced_response(user_message, cursor):
        """Get enhanced response using AI insights"""
        if 'analyze' in user_message or 'insight' in user_message or 'recommend' in user_message or 'trend' in user_message or 'pattern' in user_message:
            # Get CRM insights for AI analysis
            crm_insights = get_crm_insights(user_message, cursor)
            return generate_ai_insight(user_message, crm_insights)
        return None  # Return None if not an AI query

# Define fallback function if moonshot is not available
if not moonshot_available:
    def get_enhanced_response(user_message, cursor):
        return None


if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True, host='0.0.0.0', port=5001)
=======
    # Run churn predictions on startup
    print("Running initial churn predictions on startup...")
    run_churn_predictions()
    app.run(debug=True, port=5001)
>>>>>>> churn_2
