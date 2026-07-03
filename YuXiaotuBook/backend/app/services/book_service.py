from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.models import Book, BookVideo, Category


async def book_to_dict(book: Book, with_video_meta: bool = True) -> Dict[str, Any]:
    category = await Category.get_or_none(id=book.category_id)
    video = await BookVideo.get_or_none(book_id=book.id, status=1)
    data: Dict[str, Any] = {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "cover": book.cover,
        "category": {"id": category.id, "name": category.name} if category else None,
        "price": float(book.price),
        "stock": book.stock,
        "summary": book.summary,
        "highlight": book.highlight,
        "target_audience": book.target_audience,
        "status": book.status,
        "view_count": book.view_count,
        "has_video": video is not None,
    }
    if with_video_meta and video:
        data["video"] = {
            "duration": video.video_duration,
            "cover": video.video_cover,
            "intro": video.video_intro,
        }
    return data


async def book_list_item(book: Book) -> Dict[str, Any]:
    video = await BookVideo.get_or_none(book_id=book.id, status=1)
    category = await Category.get_or_none(id=book.category_id)
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "cover": book.cover,
        "category": {"id": category.id, "name": category.name} if category else None,
        "price": float(book.price),
        "has_video": video is not None,
        "view_count": book.view_count,
    }
