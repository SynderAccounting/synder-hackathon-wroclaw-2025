# Database Client

Database client for storing and retrieving mock e-commerce orders from Amazon, Etsy, and Shopify.

## Structure

```
db_client/
├── db/                     # Database utilities
│   ├── connection.py       # Connection management
│   └── orders.py          # Order CRUD operations
├── examples/              # Example scripts
│   └── insert_order_example.py
└── requirements.txt       # Database dependencies
```

## Installation

```bash
cd db_client
pip install -r requirements.txt
```

## Database Schema

The PostgreSQL database uses a normalized schema with the following tables:
- `customers` - Customer information
- `addresses` - Billing and shipping addresses
- `orders` - Main order data with service identifier
- `order_items` - Line items for each order
- `fulfillments` - Tracking and shipment information
- `discounts` - Discount codes and percentages

See `../database/init.sql` for the full schema.

## Usage

### Environment Variables

Set these environment variables to connect to the database:

```bash
export DB_HOST=localhost        # Database host
export DB_PORT=5432            # Database port
export DB_NAME=mockapi         # Database name
export DB_USER=postgres        # Database user
export DB_PASSWORD=postgres    # Database password
```

### Inserting Orders

```python
from db.connection import get_db_connection
from db.orders import insert_order
from models.order import Order

# Create an Order instance (from mock_api)
order = Order(...)

# Insert into database
with get_db_connection() as conn:
    order_id = insert_order(conn, order)
    print(f"Inserted order with ID: {order_id}")
```

### Running the Example Script

The example script populates the database with mock orders:

```bash
# Make sure database is running
docker-compose up -d postgres

# Run the example
cd db_client
python examples/insert_order_example.py
```

## Dependencies

This module depends on:
- `mock_api` - For Order models and data generation
- PostgreSQL database - Configured via docker-compose
