"""Mock data storage and generators"""
from faker import Faker
from datetime import datetime, timedelta
from typing import List, Dict
import random
import uuid
from app.core.security import get_password_hash

fake = Faker()

# Mock database storage
class MockDB:
    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.transactions: List[dict] = []
        self.connectors: List[dict] = []
        self.ingestion_jobs: List[dict] = []
        self._initialize_data()

    def _initialize_data(self):
        """Initialize mock data"""
        # Create default users
        self.users = {
            "admin": {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": get_password_hash("admin123"),
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            "analyst": {
                "id": str(uuid.uuid4()),
                "username": "analyst",
                "email": "analyst@example.com",
                "hashed_password": get_password_hash("analyst123"),
                "full_name": "Analyst User",
                "role": "analyst",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            "viewer": {
                "id": str(uuid.uuid4()),
                "username": "viewer",
                "email": "viewer@example.com",
                "hashed_password": get_password_hash("viewer123"),
                "full_name": "Viewer User",
                "role": "viewer",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        }

        # Generate mock transactions
        platforms = ["Shopify", "Amazon", "eBay", "WooCommerce", "Magento"]
        statuses = ["completed", "pending", "failed", "refunded"]

        for i in range(200):  # Generate 200 transactions
            platform = random.choice(platforms)
            status = random.choice(statuses)
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 90))

            num_items = random.randint(1, 5)
            items = []
            total_amount = 0

            for j in range(num_items):
                price = round(random.uniform(10, 500), 2)
                quantity = random.randint(1, 3)
                item_total = round(price * quantity, 2)
                total_amount += item_total

                items.append({
                    "id": str(uuid.uuid4()),
                    "sku": f"SKU-{fake.bothify(text='????-####')}",
                    "name": fake.catch_phrase(),
                    "quantity": quantity,
                    "price": price,
                    "total": item_total,
                })

            self.transactions.append({
                "id": str(uuid.uuid4()),
                "order_id": f"ORD-{fake.bothify(text='########')}",
                "platform": platform,
                "customer_email": fake.email(),
                "customer_name": fake.name(),
                "amount": round(total_amount, 2),
                "currency": "USD",
                "status": status,
                "items": items,
                "created_at": created_at,
                "updated_at": created_at,
                "metadata": {
                    "ip_address": fake.ipv4(),
                    "user_agent": fake.user_agent(),
                },
            })

        # Generate mock connectors
        connector_configs = [
            {"name": "Shopify Store", "platform": "Shopify", "status": "active"},
            {"name": "Amazon Seller Central", "platform": "Amazon", "status": "active"},
            {"name": "eBay Store", "platform": "eBay", "status": "inactive"},
            {"name": "WooCommerce", "platform": "WooCommerce", "status": "active"},
            {"name": "Magento", "platform": "Magento", "status": "error"},
        ]

        for config in connector_configs:
            connector_id = str(uuid.uuid4())
            self.connectors.append({
                "id": connector_id,
                "name": config["name"],
                "platform": config["platform"],
                "description": f"Integration with {config['platform']} platform",
                "status": config["status"],
                "last_sync": datetime.utcnow() - timedelta(hours=random.randint(1, 48)) if config["status"] == "active" else None,
                "config": {
                    "api_key": "mock_api_key_" + str(uuid.uuid4()),
                    "store_url": f"https://{config['platform'].lower()}.example.com",
                },
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow(),
            })

        # Generate mock ingestion jobs
        job_statuses = ["completed", "running", "pending", "failed"]
        for i in range(15):
            connector = random.choice(self.connectors)
            status = random.choice(job_statuses)
            started_at = datetime.utcnow() - timedelta(hours=random.randint(1, 72))

            self.ingestion_jobs.append({
                "id": str(uuid.uuid4()),
                "connector_id": connector["id"],
                "connector_name": connector["name"],
                "status": status,
                "records_processed": random.randint(100, 5000) if status != "pending" else 0,
                "records_failed": random.randint(0, 50) if status == "completed" else 0,
                "started_at": started_at if status != "pending" else None,
                "completed_at": started_at + timedelta(minutes=random.randint(5, 60)) if status == "completed" else None,
                "error_message": "Connection timeout" if status == "failed" else None,
            })

# Global mock database instance
mock_db = MockDB()
