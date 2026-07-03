from __future__ import annotations

from typing import Any, Dict, List

from app.models import Book, UserBookCollect
from app.services.book_service import book_list_item


async def list_user_collected_books(
    user_id: int,
    collect_type: int,
    *,
    published_only: bool = False,
) -> List[Dict[str, Any]]:
    """按收藏类型列出用户书籍（收藏=1，浏览历史=2）。"""
    collects = await UserBookCollect.filter(
        user_id=user_id, collect_type=collect_type
    ).order_by("-created_at")
    items: List[Dict[str, Any]] = []
    for collect in collects:
        if published_only:
            book = await Book.get_or_none(id=collect.book_id, status="published")
        else:
            book = await Book.get_or_none(id=collect.book_id)
        if book:
            items.append(await book_list_item(book))
    return items
