"""Business logic services."""
from .product_service import get_all_products, get_product_details
from .suggestion_service import get_suggestions_for_product, apply_suggestion
from .event_service import get_recent_events
from .connection_service import (
    get_all_connections,
    create_connection,
    delete_connection,
    toggle_connection,
    quick_demo_setup
)
from .sync_service import sync_connection
from .ai_agent_service import (
    generate_suggestions_for_product,
    generate_suggestions_for_all_products
)

__all__ = [
    # Product services
    'get_all_products',
    'get_product_details',
    # Suggestion services
    'get_suggestions_for_product',
    'apply_suggestion',
    # Event services
    'get_recent_events',
    # Connection services
    'get_all_connections',
    'create_connection',
    'delete_connection',
    'toggle_connection',
    'quick_demo_setup',
    # Sync services
    'sync_connection',
    # AI Agent services
    'generate_suggestions_for_product',
    'generate_suggestions_for_all_products',
]
