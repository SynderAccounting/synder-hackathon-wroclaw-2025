from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import math
import csv
import io

from app.schemas.transaction import Transaction, PaginatedTransactions
from app.schemas.user import User
from app.api.auth import get_current_user
from app.models.mock_data import mock_db

router = APIRouter()


@router.get("", response_model=PaginatedTransactions)
async def get_transactions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get paginated transactions with optional filters"""
    # Filter transactions
    filtered_transactions = mock_db.transactions.copy()

    if platform:
        filtered_transactions = [t for t in filtered_transactions if t["platform"].lower() == platform.lower()]

    if status:
        filtered_transactions = [t for t in filtered_transactions if t["status"].lower() == status.lower()]

    if min_amount is not None:
        filtered_transactions = [t for t in filtered_transactions if t["amount"] >= min_amount]

    if max_amount is not None:
        filtered_transactions = [t for t in filtered_transactions if t["amount"] <= max_amount]

    if search:
        search_lower = search.lower()
        filtered_transactions = [
            t for t in filtered_transactions
            if search_lower in t["order_id"].lower()
            or search_lower in t["customer_email"].lower()
            or search_lower in t["customer_name"].lower()
        ]

    # Sort by created_at descending
    filtered_transactions.sort(key=lambda x: x["created_at"], reverse=True)

    # Pagination
    total = len(filtered_transactions)
    pages = math.ceil(total / size) if total > 0 else 1
    start = (page - 1) * size
    end = start + size
    items = filtered_transactions[start:end]

    return PaginatedTransactions(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a single transaction by ID"""
    for transaction in mock_db.transactions:
        if transaction["id"] == transaction_id:
            return transaction
    return None


@router.get("/export", response_class=StreamingResponse)
async def export_transactions(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Export transactions to CSV"""
    # Filter transactions
    filtered_transactions = mock_db.transactions.copy()

    if platform:
        filtered_transactions = [t for t in filtered_transactions if t["platform"].lower() == platform.lower()]

    if status:
        filtered_transactions = [t for t in filtered_transactions if t["status"].lower() == status.lower()]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Order ID", "Platform", "Customer Name", "Customer Email",
        "Amount", "Currency", "Status", "Created At"
    ])

    # Write data
    for t in filtered_transactions:
        writer.writerow([
            t["order_id"],
            t["platform"],
            t["customer_name"],
            t["customer_email"],
            t["amount"],
            t["currency"],
            t["status"],
            t["created_at"].isoformat(),
        ])

    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )
