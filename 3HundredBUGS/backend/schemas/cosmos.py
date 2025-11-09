from pydantic import BaseModel


class SupplierProductSchema(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    product_id: str
    product_name: str
    lead_time_days: int
    min_order_qty: int
    unit_cost: float
    currency: str
    current_stock: int
    reorder_point: int


class PostgresSQLQuerySchema(BaseModel):
    query: str
