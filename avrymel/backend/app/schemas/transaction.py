from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class TransactionItem(BaseModel):
    id: str
    sku: str
    name: str
    quantity: int
    price: float
    total: float


class Transaction(BaseModel):
    id: str
    order_id: str
    platform: str
    customer_email: str
    customer_name: str
    amount: float
    currency: str
    status: str
    items: List[TransactionItem]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict[str, Any]] = None


class PaginatedTransactions(BaseModel):
    items: List[Transaction]
    total: int
    page: int
    size: int
    pages: int
