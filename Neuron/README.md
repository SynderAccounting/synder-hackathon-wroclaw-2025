# One Front (Customer Relationship Management System)

A comprehensive Customer Relationship Management System built with Flask and SQLite, designed specifically for retail businesses. Features full Shopify integration for product synchronization between your local panel and Shopify store.

## Features

### Customer Management
- Add, edit, and view customer profiles
- Track customer contact information (name, email, phone, address)
- Customer status management (active/inactive)
- Loyalty points system
- Customer interaction logging (calls, emails, meetings, support, complaints, feedback)
- Order history tracking per customer
- Custom notes for each customer

### Product Management
- Product inventory tracking
- Product details (name, description, SKU, category)
- Price management
- Stock quantity monitoring
- Low stock alerts on dashboard
- Full Shopify integration - products automatically sync to your Shopify store
- Full WooCommerce integration - products automatically sync to your WooCommerce store
- Two-way synchronization for product updates and deletions across both platforms

### Order Management
- Create new orders with multiple products
- Order status tracking (pending, processing, shipped, delivered, cancelled)
- Payment method recording
- Shipping address management
- Automatic stock reduction on order creation
- Automatic loyalty points addition (1 point per dollar spent)
- Detailed order views with line items

### Dashboard & Analytics
- Total customers and active customers count
- Total products in inventory
- Total orders and pending orders
- Total revenue tracking
- Recent orders overview
- Low stock alerts (products with less than 10 units)

### API Endpoints
- RESTful API for customers (`/api/customers`)
- RESTful API for products (`/api/products`)

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with responsive design

## Database Schema

### Tables

1. **customers**
   - id, name, email, phone, address
   - date_joined, loyalty_points, status, notes

2. **products**
   - id, name, description, price
   - stock_quantity, category, sku, created_at

3. **orders**
   - id, customer_id, order_date, total_amount
   - status, payment_method, shipping_address

4. **order_items**
   - id, order_id, product_id
   - quantity, unit_price, subtotal

5. **customer_interactions**
   - id, customer_id, interaction_type
   - notes, interaction_date, created_by

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
cd D:\coding\repos\Test
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Shopify Integration
Update the `.env` file with your Shopify store credentials:
```env
SHOPIFY_STORE_URL=https://your-store.myshopify.com/
SHOPIFY_ACCESS_TOKEN=your_private_app_access_token
SHOPIFY_VENDOR=Your Store Name
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5001/`

### Step 5: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5001/
```

## Usage Guide

### Adding Customers
1. Navigate to "Customers" in the menu
2. Click "Add New Customer"
3. Fill in customer details (name and email are required)
4. Click "Create Customer"

### Adding Products
1. Navigate to "Products" in the menu
2. Click "Add New Product"
3. Fill in product details (name, price, and stock quantity are required)
4. Click "Create Product"

### Creating Orders
1. Navigate to "Orders" in the menu
2. Click "Create New Order"
3. Select a customer
4. Choose payment method
5. Add products and quantities
6. Click "Add Another Item" to add more products
7. Click "Create Order"

### Logging Customer Interactions
1. Go to a customer's detail page
2. Scroll to "Customer Interactions" section
3. Select interaction type (call, email, meeting, etc.)
4. Add notes
5. Click "Add Interaction"

### Updating Order Status
1. Go to order detail page
2. Scroll to "Update Order Status" section
3. Select new status
4. Click "Update Status"

## Project Structure

```
Synder/
├── app.py                      # Main Flask application
├── shopify_integration.py      # Shopify API integration module
├── retail_crms.db             # SQLite database (auto-created)
├── README.md                  # Project documentation
├── SHOPIFY_INTEGRATION.md     # Shopify integration documentation
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (credentials)
├── .venv/                     # Python virtual environment
├── static/
│   └── style.css             # CSS styling
└── templates/
    ├── base.html             # Base template
    ├── index.html            # Dashboard
    ├── customers.html        # Customer list
    ├── customer_form.html    # Add/Edit customer
    ├── customer_detail.html  # Customer details
    ├── products.html         # Product list
    ├── product_form.html     # Add/Edit product
    ├── orders.html           # Order list
    ├── order_form.html       # Create order
    └── order_detail.html     # Order details
```

## Key Features Explained

### Loyalty Points System
- Customers automatically earn 1 loyalty point for every dollar spent
- Points are added when an order is created
- View points on customer detail page

### Stock Management
- Stock is automatically reduced when orders are created
- Low stock products (< 10 units) are highlighted on dashboard
- Stock quantity is displayed on product list

### Order Statuses
- **Pending**: Order created, awaiting processing
- **Processing**: Order is being prepared
- **Shipped**: Order has been shipped
- **Delivered**: Order successfully delivered
- **Cancelled**: Order cancelled

### Customer Interaction Types
- Phone Call
- Email
- Meeting
- Support
- Complaint
- Feedback

## API Usage

### Get All Customers
```
GET /api/customers
```
Returns JSON array of all customers

### Get All Products
```
GET /api/products
```
Returns JSON array of all products

## Database Notes

- Database file `retail_crms.db` is automatically created on first run
- All tables are created automatically on initialization
- Foreign key relationships ensure data integrity
- Timestamps are automatically recorded for orders and interactions

## Security Considerations

For production use, consider:
- Change the `SECRET_KEY` in app.py
- Add user authentication
- Implement input validation and sanitization
- Use environment variables for configuration
- Add HTTPS support
- Implement proper error handling
- Add database backups

## Future Enhancements

Potential features to add:
- User authentication and role-based access
- Advanced analytics and reporting
- Product categories management
- Discount and promotion system
- Invoice generation
- Email notifications
- Export data to CSV/Excel
- Search and filtering capabilities
- Multi-store support

## Troubleshooting

### Database Issues
If you encounter database errors, delete `retail_crms.db` and restart the application to recreate the database.

### Port Already in Use
If port 5000 is in use, modify the last line in `app.py`:
```python
app.run(debug=True, port=5001)  # Change to different port
```

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check the code comments in `app.py` for detailed documentation of each function.
