"""Event history business logic."""
from typing import List, Dict
from database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)


def get_recent_events(limit: int = 20) -> List[Dict]:
    """
    Retrieve recent system events (history).

    Args:
        limit: Maximum number of events to retrieve (default: 20).

    Returns:
        List of events ordered by creation date (newest first).

    Raises:
        Exception: If database query fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                e.id,
                e.product_id,
                e.suggestion_id,
                e.event_type,
                e.description,
                e.created_at,
                p.name as product_name,
                p.sku as product_sku
            FROM events e
            LEFT JOIN products p ON e.product_id = p.id
            ORDER BY e.created_at DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()

        events = [dict(row) for row in rows]

    logger.info(f"Retrieved {len(events)} events")
    return events
