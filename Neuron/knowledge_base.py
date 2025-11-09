"""
Knowledge Base for the Synder CRM Application

This module contains comprehensive information about the application,
its features, functionality, and how to explain them to users.
"""

# App Overview
APP_OVERVIEW = {
    "title": "Synder CRM System",
    "description": "A comprehensive Customer Relationship Management system for retail businesses",
    "main_features": [
        "Customer management",
        "Product management", 
        "Order processing",
        "Inventory tracking",
        "Invoice generation",
        "Customer interaction tracking",
        "Sales analytics",
        "AI-powered chatbot"
    ],
    "target_users": [
        "Retail business owners",
        "Customer service representatives",
        "Sales managers",
        "Inventory managers"
    ]
}

# Database Schema
DATABASE_SCHEMA = {
    "customers": {
        "description": "Stores customer information",
        "columns": [
            "id (Integer, Primary Key) - Unique customer identifier",
            "name (Text) - Customer's full name",
            "email (Text) - Customer's email address (Unique)",
            "phone (Text) - Customer's phone number",
            "address (Text) - Customer's address",
            "date_joined (Timestamp) - Date when customer was added",
            "loyalty_points (Integer) - Points accumulated by customer",
            "status (Text) - Customer status (active, inactive, etc.)",
            "notes (Text) - Additional notes about the customer"
        ]
    },
    "products": {
        "description": "Stores product information",
        "columns": [
            "id (Integer, Primary Key) - Unique product identifier",
            "name (Text) - Product name",
            "description (Text) - Product description",
            "price (Real) - Product price",
            "stock_quantity (Integer) - Available stock quantity",
            "category (Text) - Product category",
            "photo (Text) - Path to product photo",
            "technical_details (Text) - Technical specifications",
            "shopify_product_id (Integer) - Associated Shopify product ID",
            "woocommerce_product_id (Integer) - Associated WooCommerce product ID",
            "vat_rate (Real) - VAT rate applicable to product",
            "visualization_3d_path (Text) - 3D visualization path"
        ]
    },
    "orders": {
        "description": "Stores order information",
        "columns": [
            "id (Integer, Primary Key) - Unique order identifier",
            "customer_id (Integer) - Foreign key to customers table",
            "order_date (Timestamp) - Date of the order",
            "total_amount (Real) - Total order amount",
            "status (Text) - Order status (pending, completed, cancelled, etc.)",
            "payment_method (Text) - Payment method used",
            "shipping_address (Text) - Shipping address",
            "tracking_number (Text) - Order tracking number"
        ]
    },
    "order_items": {
        "description": "Stores items within each order (linking orders to products)",
        "columns": [
            "id (Integer, Primary Key) - Unique identifier",
            "order_id (Integer) - Foreign key to orders table",
            "product_id (Integer) - Foreign key to products table",
            "quantity (Integer) - Quantity ordered",
            "unit_price (Real) - Price per unit",
            "subtotal (Real) - Subtotal for this item (quantity * unit_price)"
        ]
    },
    "customer_interactions": {
        "description": "Stores interactions with customers",
        "columns": [
            "id (Integer, Primary Key) - Unique interaction identifier",
            "customer_id (Integer) - Foreign key to customers table",
            "interaction_type (Text) - Type of interaction (email, call, etc.)",
            "notes (Text) - Notes about the interaction",
            "interaction_date (Timestamp) - Date of the interaction",
            "created_by (Text) - Person who recorded the interaction"
        ]
    },
    "invoices": {
        "description": "Stores invoice information",
        "columns": [
            "id (Integer, Primary Key) - Unique invoice identifier",
            "order_id (Integer) - Foreign key to orders table",
            "invoice_number (Text) - Invoice number (Unique)",
            "issue_date (Date) - Invoice issue date",
            "supply_date (Date) - Supply/service date",
            "created_at (Timestamp) - Date invoice was created"
        ]
    },
    "product_photos": {
        "description": "Stores multiple photos for each product",
        "columns": [
            "id (Integer, Primary Key) - Unique photo identifier",
            "product_id (Integer) - Foreign key to products table",
            "photo_path (Text) - Path to the photo file",
            "is_main (Integer) - Whether this is the main photo (0 or 1)",
            "display_order (Integer) - Order in which to display photos",
            "created_at (Timestamp) - Date photo was added"
        ]
    }
}

# Routes and Functionality
ROUTES_INFO = {
    "dashboard": {
        "path": "/",
        "description": "Main dashboard showing statistics and recent activity",
        "data_displayed": [
            "Total customers count",
            "Active customers count", 
            "Total products count",
            "Total orders count",
            "Pending orders count",
            "Total revenue",
            "Recent orders",
            "Low stock products"
        ]
    },
    "customers": {
        "path": "/customers",
        "description": "View all customers",
        "functionality": [
            "Display list of all customers",
            "Sort by date joined (descending)"
        ]
    },
    "add_customer": {
        "path": "/customers/add",
        "methods": ["GET", "POST"],
        "description": "Add a new customer",
        "fields": [
            "name (required)",
            "email (required, unique)",
            "phone (optional)",
            "address (optional)",
            "notes (optional)"
        ]
    },
    "customer_detail": {
        "path": "/customers/<int:customer_id>",
        "description": "View detailed information about a specific customer",
        "data_displayed": [
            "Customer information",
            "Customer's orders",
            "Customer interactions"
        ]
    },
    "edit_customer": {
        "path": "/customers/<int:customer_id>/edit",
        "methods": ["GET", "POST"],
        "description": "Edit customer information",
        "editable_fields": [
            "name",
            "email", 
            "phone",
            "address", 
            "status",
            "notes"
        ]
    },
    "add_interaction": {
        "path": "/customers/<int:customer_id>/interaction",
        "methods": ["POST"],
        "description": "Add an interaction record for a customer",
        "fields": [
            "interaction_type",
            "notes",
            "created_by"
        ]
    },
    "products": {
        "path": "/products",
        "description": "View all products",
        "functionality": [
            "Display list of all products",
            "Sort by creation date (descending)"
        ]
    },
    "add_product": {
        "path": "/products/add",
        "methods": ["GET", "POST"],
        "description": "Add a new product",
        "fields": [
            "name (required)",
            "description (optional)",
            "price (required)",
            "stock_quantity (required)",
            "category (optional)",
            "technical_details (optional)",
            "photos (multiple, optional)"
        ],
        "features": [
            "Background removal for uploaded images",
            "3D visualization support",
            "Shopify integration",
            "WooCommerce integration"
        ]
    },
    "orders": {
        "path": "/orders",
        "description": "View all orders",
        "functionality": [
            "Display list of all orders",
            "Sort by date (descending)",
            "Filter by status",
            "View customer name"
        ]
    },
    "add_order": {
        "path": "/orders/add",
        "methods": ["GET", "POST"],
        "description": "Add a new order",
        "functionality": [
            "Select customer",
            "Select products",
            "Set quantities",
            "Choose payment method",
            "Add shipping address",
            "Calculate total automatically"
        ]
    },
    "generate_invoice": {
        "path": "/orders/<int:order_id>/generate_invoice",
        "methods": ["POST"],
        "description": "Generate a Polish VAT-compliant invoice for an order"
    },
    "chatbot_api": {
        "path": "/api/chatbot_query",
        "methods": ["POST"],
        "description": "AI-powered chatbot API that can answer questions about the data",
        "functionality": [
            "Understands natural language questions",
            "Can answer about customers, products, orders, inventory",
            "Provides statistical information",
            "Handles complex queries with multiple conditions"
        ]
    }
}

# Chatbot Capabilities
CHATBOT_CAPABILITIES = {
    "customer_queries": [
        "How many customers are there?",
        "Show me active customers",
        "Show me inactive customers",
        "List all customers",
        "Show me customers with specific status",
        "Find customer by name"
    ],
    "product_queries": [
        "How many products are there?",
        "Show me expensive products",
        "Show me cheap products",
        "Show me low stock products",
        "List products by category",
        "Show products under/over a specific price"
    ],
    "order_queries": [
        "How many orders are there?",
        "What is the total revenue?",
        "Show me pending orders",
        "Show me cancelled orders",
        "Show me recent orders",
        "Show orders with tracking numbers"
    ],
    "inventory_queries": [
        "How many items are in total inventory?",
        "Show me low stock items",
        "Show stock under a specific threshold"
    ],
    "statistical_queries": [
        "Average product price",
        "Average order amount",
        "Highest priced product",
        "Best customer by spending",
        "Show me sales trends"
    ],
    "advanced_queries": [
        "Show me expensive products in electronics category",
        "Orders between specific dates",
        "Products priced between two values",
        "Customers from last month"
    ]
}

# Common Features and Concepts
COMMON_FEATURES = {
    "payment_methods": [
        "cash",
        "credit_card", 
        "debit_card",
        "mobile_payment",
        "bank_transfer"
    ],
    "order_statuses": [
        "pending",      # Default status when order is created
        "processing",   # Order is being processed
        "shipped",      # Order has been shipped
        "delivered",    # Order has been delivered
        "completed",    # Order is completed
        "cancelled",    # Order was cancelled
        "refunded"      # Order was refunded
    ],
    "customer_statuses": [
        "active",       # Regular customer
        "inactive",     # Inactive customer
        "blacklisted",  # Customer on blacklist
        "prospect"      # Potential customer
    ],
    "integrations": [
        {
            "name": "Shopify",
            "description": "Sync products to Shopify store",
            "features": ["Sync products", "Update inventory", "Sync product details"]
        },
        {
            "name": "WooCommerce", 
            "description": "Sync products to WooCommerce store",
            "features": ["Sync products", "Update inventory", "Sync product details"]
        }
    ]
}

# Troubleshooting Information
TROUBLESHOOTING = {
    "common_issues": [
        {
            "issue": "Customer email already exists",
            "solution": "Check if the customer already exists before adding"
        },
        {
            "issue": "Database locked error", 
            "solution": "The system has retry logic built-in to handle this automatically"
        },
        {
            "issue": "Image upload failed",
            "solution": "Check if the file is in allowed formats (png, jpg, jpeg, gif, webp)"
        }
    ]
}

# API Endpoints
API_ENDPOINTS = {
    "chatbot_query": {
        "path": "/api/chatbot_query",
        "method": "POST",
        "request_format": {"question": "your question here"},
        "response_format": {"result": "answer to the question"},
        "description": "Natural language query interface to the database"
    }
}

# Comprehensive How-To Guides
HOW_TO_GUIDES = {
    "add_customer": {
        "title": "How to Add a New Customer",
        "steps": [
            "Navigate to the Customers page using the navigation menu",
            "Click the 'Add Customer' button",
            "Fill in the customer details: Name (required), Email (required and must be unique), Phone (optional), Address (optional)",
            "Add any notes about the customer in the Notes field",
            "Click 'Create Customer' to save",
            "The new customer will appear in your customer list with 'active' status by default"
        ],
        "tips": [
            "Email addresses must be unique - you cannot add two customers with the same email",
            "You can update customer information later by clicking on the customer and selecting 'Edit'",
            "Use the Notes field to record important information about the customer"
        ]
    },
    "add_product": {
        "title": "How to Add a New Product",
        "steps": [
            "Go to the Products page from the navigation menu",
            "Click the 'Add Product' button",
            "Enter the product name (required)",
            "Add a description to help identify the product",
            "Set the price (required)",
            "Enter the stock quantity (required)",
            "Select or enter a category for organization",
            "Upload product photos - you can upload multiple images",
            "The system can automatically remove backgrounds from your product images",
            "Add technical details if applicable",
            "If you use Shopify or WooCommerce, you can sync this product later",
            "Click 'Create Product' to save"
        ],
        "tips": [
            "You can upload multiple photos for each product",
            "The background removal feature helps create professional product images",
            "Stock quantities update automatically when orders are placed",
            "Products with stock below 10 units are highlighted as 'low stock'"
        ]
    },
    "add_order": {
        "title": "How to Create a New Order",
        "steps": [
            "Navigate to the Orders page",
            "Click 'Add Order'",
            "Select the customer from the dropdown menu",
            "Choose products to add to the order",
            "Set the quantity for each product",
            "The total will be calculated automatically",
            "Select a payment method (cash, credit card, debit card, mobile payment, or bank transfer)",
            "Add the shipping address if different from customer's default address",
            "Click 'Create Order'",
            "The order will be created with 'pending' status"
        ],
        "tips": [
            "Make sure the customer exists before creating an order",
            "Check product availability before adding to order",
            "You can change order status later as it progresses",
            "Generate invoices for completed orders"
        ]
    },
    "edit_customer": {
        "title": "How to Edit Customer Information",
        "steps": [
            "Go to the Customers page",
            "Find the customer you want to edit",
            "Click on the customer to view their details",
            "Click the 'Edit' button",
            "Update any fields you need to change (name, email, phone, address, status, notes)",
            "Click 'Save Changes'",
            "The updated information will be reflected immediately"
        ],
        "tips": [
            "You can change customer status to: active, inactive, blacklisted, or prospect",
            "All customer orders and interactions are preserved when you edit customer info"
        ]
    },
    "track_interactions": {
        "title": "How to Track Customer Interactions",
        "steps": [
            "Navigate to the specific customer's detail page",
            "Scroll down to the 'Customer Interactions' section",
            "Click 'Add Interaction'",
            "Select the interaction type (email, call, meeting, support ticket, etc.)",
            "Add detailed notes about what was discussed or what happened",
            "Enter who created this interaction record",
            "Click 'Save Interaction'",
            "The interaction will be added to the customer's history with a timestamp"
        ],
        "tips": [
            "Use interactions to maintain a complete history of customer communications",
            "Detailed notes help team members understand customer history",
            "All interactions are timestamped automatically"
        ]
    },
    "generate_invoice": {
        "title": "How to Generate an Invoice",
        "steps": [
            "Go to the Orders page",
            "Find the order you want to invoice",
            "Click the 'Generate Invoice' button next to the order",
            "The system will create a Polish VAT-compliant invoice",
            "The invoice includes all order details, customer information, and itemized products",
            "You can download the invoice as a PDF",
            "Invoice numbers are automatically generated and unique"
        ],
        "tips": [
            "Invoices follow Polish VAT regulations",
            "Each invoice has a unique invoice number",
            "Invoices include issue date and supply date"
        ]
    },
    "manage_inventory": {
        "title": "How to Manage Inventory",
        "steps": [
            "Go to the Products page to view all inventory",
            "Check the 'Stock Quantity' column to see current levels",
            "Products with stock below 10 units are highlighted in red as 'Low Stock'",
            "To update stock: click on a product, click 'Edit', update the stock quantity, save",
            "Stock automatically decreases when orders are placed",
            "Monitor the dashboard for low stock alerts"
        ],
        "tips": [
            "Set up regular inventory checks to maintain accurate stock levels",
            "The dashboard shows low stock products for quick monitoring",
            "Consider setting reorder points for frequently sold items"
        ]
    },
    "use_integrations": {
        "title": "How to Use Shopify and WooCommerce Integrations",
        "steps": [
            "Products can be synced to Shopify and WooCommerce stores",
            "When adding or editing a product, you can link it to Shopify or WooCommerce",
            "The system stores the external product IDs for synchronization",
            "Updates to products can be pushed to your connected stores",
            "Inventory levels can be synchronized across platforms"
        ],
        "tips": [
            "Keep product information consistent across all platforms",
            "Sync regularly to avoid inventory discrepancies"
        ]
    },
    "understand_dashboard": {
        "title": "How to Use the Dashboard",
        "description": "The dashboard is your main overview page showing key business metrics",
        "sections": [
            "Total Customers - Shows count of all customers in the system",
            "Active Customers - Shows customers with 'active' status",
            "Total Products - Count of all products in inventory",
            "Total Orders - Count of all orders ever placed",
            "Pending Orders - Orders awaiting processing",
            "Total Revenue - Sum of all completed order values",
            "Recent Orders - List of most recent orders",
            "Low Stock Products - Products with less than 10 units in stock"
        ],
        "tips": [
            "Check the dashboard daily for a quick overview of your business",
            "Low stock alerts help you reorder before running out",
            "Monitor pending orders to ensure timely processing"
        ]
    },
    "change_order_status": {
        "title": "How to Change Order Status",
        "steps": [
            "Go to the Orders page",
            "Click on the order you want to update",
            "Click 'Edit Order' or change status directly",
            "Select the new status from the dropdown",
            "Available statuses: pending, processing, shipped, delivered, completed, cancelled, refunded",
            "Click 'Save' to update the order"
        ],
        "tips": [
            "Update status as the order progresses through fulfillment",
            "Customers appreciate knowing their order status",
            "Use 'completed' for successfully delivered orders"
        ]
    },
    "search_and_filter": {
        "title": "How to Search and Filter",
        "customers": "On the Customers page, you can filter by status, sort by date joined, or search by name and email",
        "products": "On the Products page, you can filter by category, sort by price or stock, search by product name",
        "orders": "On the Orders page, you can filter by status, date range, customer, or search by order ID",
        "tips": [
            "Use filters to quickly find what you're looking for",
            "Combine multiple filters for more specific results"
        ]
    }
}

# Feature Explanations
FEATURE_EXPLANATIONS = {
    "customer_management": {
        "title": "Customer Management",
        "description": "Comprehensive customer relationship management to track all your customers in one place",
        "features": [
            "Store customer contact information (name, email, phone, address)",
            "Track customer status (active, inactive, blacklisted, prospect)",
            "Add unlimited notes about each customer",
            "View complete customer order history",
            "Track all interactions with each customer",
            "Loyalty points system to reward repeat customers",
            "Timestamp when each customer joined"
        ],
        "benefits": [
            "Never lose track of customer information",
            "Complete history of customer relationships",
            "Better customer service with interaction tracking",
            "Identify your best customers by order history"
        ]
    },
    "product_management": {
        "title": "Product Management",
        "description": "Manage your entire product catalog with inventory tracking and multi-channel support",
        "features": [
            "Store detailed product information (name, description, price, category)",
            "Track stock quantities in real-time",
            "Upload multiple photos per product",
            "Automatic background removal for product photos",
            "3D visualization support for products",
            "Technical specifications and details",
            "VAT rate configuration per product",
            "Integration with Shopify and WooCommerce",
            "Low stock alerts (under 10 units)",
            "Category-based organization"
        ],
        "benefits": [
            "Professional product presentations with background removal",
            "Never run out of stock with alerts",
            "Multi-channel selling made easy",
            "Organized catalog for easy browsing"
        ]
    },
    "order_management": {
        "title": "Order Processing",
        "description": "Complete order management from creation to fulfillment",
        "features": [
            "Create orders linked to customers",
            "Add multiple products to each order",
            "Automatic total calculation",
            "Multiple payment method support",
            "Order status tracking (pending → processing → shipped → delivered → completed)",
            "Shipping address management",
            "Tracking number support",
            "Order history and timestamps",
            "Generate Polish VAT-compliant invoices"
        ],
        "benefits": [
            "Streamlined order processing",
            "Complete order history",
            "Professional invoicing",
            "Customer order tracking"
        ]
    },
    "invoice_system": {
        "title": "Invoice Generation",
        "description": "Automated Polish VAT-compliant invoice generation",
        "features": [
            "One-click invoice generation from orders",
            "Automatic invoice numbering",
            "Polish VAT compliance",
            "PDF export capability",
            "Includes all order and customer details",
            "Issue date and supply date tracking",
            "Itemized product listing with VAT"
        ],
        "benefits": [
            "Legal compliance for Polish businesses",
            "Professional invoices",
            "Time-saving automation",
            "Complete audit trail"
        ]
    },
    "chatbot_assistant": {
        "title": "AI Chatbot Assistant",
        "description": "Intelligent assistant to help you use the system and answer questions",
        "capabilities": [
            "Answer questions about how to use features",
            "Explain different parts of the system",
            "Provide step-by-step guidance for tasks",
            "Explain payment methods and statuses",
            "Help with troubleshooting common issues",
            "Guide you through workflows",
            "Available from any page in the system"
        ],
        "example_questions": [
            "How do I add a new customer?",
            "What are the order statuses?",
            "How do I generate an invoice?",
            "Where is the dashboard?",
            "How do I track inventory?",
            "What payment methods are available?",
            "How do I add a product photo?"
        ]
    },
    "analytics_dashboard": {
        "title": "Analytics Dashboard",
        "description": "Real-time business insights and key metrics at a glance",
        "metrics": [
            "Total and active customer counts",
            "Product inventory count",
            "Order statistics",
            "Revenue tracking",
            "Low stock alerts",
            "Recent activity feed",
            "Pending order notifications"
        ],
        "benefits": [
            "Quick business overview",
            "Identify issues quickly",
            "Track growth over time",
            "Make informed decisions"
        ]
    },
    "interaction_tracking": {
        "title": "Customer Interaction Tracking",
        "description": "Record and track all customer communications and touchpoints",
        "features": [
            "Multiple interaction types (email, call, meeting, support, etc.)",
            "Detailed notes for each interaction",
            "Automatic timestamps",
            "Track who recorded the interaction",
            "Complete interaction history per customer",
            "Chronological timeline view"
        ],
        "benefits": [
            "Complete customer communication history",
            "Better team collaboration",
            "Improved customer service",
            "Never forget customer conversations"
        ]
    },
    "multi_channel_integration": {
        "title": "Multi-Channel Integration",
        "description": "Connect with Shopify and WooCommerce for seamless multi-channel selling",
        "features": [
            "Shopify product synchronization",
            "WooCommerce product synchronization",
            "Inventory sync across platforms",
            "Product detail synchronization",
            "Centralized product management"
        ],
        "benefits": [
            "Sell on multiple platforms from one system",
            "Avoid overselling with inventory sync",
            "Update once, sync everywhere",
            "Expand your reach"
        ]
    }
}

# Common Questions and Answers
FAQ = {
    "general": [
        {
            "question": "What is Synder CRM?",
            "answer": "Synder CRM is a comprehensive Customer Relationship Management system designed for retail businesses. It helps you manage customers, products, orders, inventory, and invoices all in one place."
        },
        {
            "question": "Who should use Synder CRM?",
            "answer": "Synder CRM is perfect for retail business owners, customer service representatives, sales managers, and inventory managers who need to manage customer relationships and sales operations."
        },
        {
            "question": "How do I navigate the system?",
            "answer": "Use the navigation menu at the top to access different sections: Dashboard (home), Customers, Products, Orders, and more. The dashboard provides a quick overview of your business."
        }
    ],
    "customers": [
        {
            "question": "What customer information can I store?",
            "answer": "You can store: name, email, phone, address, status (active/inactive/blacklisted/prospect), loyalty points, join date, and custom notes. You can also track all orders and interactions for each customer."
        },
        {
            "question": "Can I have duplicate customer emails?",
            "answer": "No, email addresses must be unique in the system to prevent duplicate customer records."
        },
        {
            "question": "What are customer statuses?",
            "answer": "Active (regular customer), Inactive (not currently active), Blacklisted (blocked customer), Prospect (potential customer not yet converted)."
        }
    ],
    "products": [
        {
            "question": "How many photos can I add per product?",
            "answer": "You can add multiple photos for each product. The system supports uploading several images and can automatically remove backgrounds to create professional product photos."
        },
        {
            "question": "What happens when stock is low?",
            "answer": "Products with stock quantity below 10 units are highlighted as 'low stock' on the dashboard and products page, alerting you to reorder."
        },
        {
            "question": "Can I sell on Shopify and WooCommerce?",
            "answer": "Yes! The system integrates with both Shopify and WooCommerce, allowing you to sync products and inventory across platforms."
        }
    ],
    "orders": [
        {
            "question": "What payment methods are supported?",
            "answer": "The system supports: cash, credit card, debit card, mobile payment, and bank transfer."
        },
        {
            "question": "What are the order statuses?",
            "answer": "Pending (just created), Processing (being prepared), Shipped (sent to customer), Delivered (received by customer), Completed (finalized), Cancelled (cancelled order), Refunded (money returned)."
        },
        {
            "question": "How do I track orders?",
            "answer": "Each order can have a tracking number added. You can also update the order status as it progresses from pending to delivered."
        }
    ],
    "invoices": [
        {
            "question": "Are invoices legally compliant?",
            "answer": "Yes, the system generates Polish VAT-compliant invoices that meet legal requirements for Polish businesses."
        },
        {
            "question": "Can I download invoices?",
            "answer": "Yes, invoices can be downloaded as PDF files for printing or emailing to customers."
        },
        {
            "question": "How are invoice numbers generated?",
            "answer": "Invoice numbers are automatically generated and guaranteed to be unique for each invoice."
        }
    ]
}

def get_knowledge_base():
    """
    Returns the complete knowledge base as a dictionary
    """
    return {
        "app_overview": APP_OVERVIEW,
        "database_schema": DATABASE_SCHEMA,
        "routes_info": ROUTES_INFO,
        "chatbot_capabilities": CHATBOT_CAPABILITIES,
        "common_features": COMMON_FEATURES,
        "troubleshooting": TROUBLESHOOTING,
        "api_endpoints": API_ENDPOINTS,
        "how_to_guides": HOW_TO_GUIDES,
        "feature_explanations": FEATURE_EXPLANATIONS,
        "faq": FAQ
    }