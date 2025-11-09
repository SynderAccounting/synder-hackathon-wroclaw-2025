"""Utility helpers for working with Shopify GraphQL responses."""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def parse_graphql_edges(edges: Optional[Iterable[Dict[str, Any]]]) -> List[Any]:
    """Extract nodes from GraphQL `edges` collections."""
    if not edges:
        return []
    return [edge["node"] for edge in edges if edge and "node" in edge]


async def fetch_all_pages(
    fetcher: Callable[..., Awaitable[Dict[str, Any]]],
    *,
    key: str,
    cursor: Optional[str] = None,
    max_pages: int = 10,
    **kwargs: Any,
) -> Tuple[List[Any], Dict[str, Any]]:
    """Iteratively fetch multiple pages using a cursor-based fetcher."""
    all_items: List[Any] = []
    current_cursor = cursor
    last_page_info: Dict[str, Any] = {}

    for _ in range(max_pages):
        page = await fetcher(cursor=current_cursor, **kwargs)
        items = page.get(key, [])
        all_items.extend(items)
        last_page_info = page.get("page_info", {})

        has_next = bool(last_page_info.get("hasNextPage"))
        current_cursor = last_page_info.get("endCursor") if has_next else None
        if not has_next or not current_cursor:
            break

    return all_items, last_page_info
