from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from app.models import Book, DailyBook
from app.services.book_service import book_list_item


async def daily_to_dict(daily: DailyBook) -> Dict[str, Any]:
    book = await Book.get_or_none(id=daily.book_id)
    book_item = await book_list_item(book) if book else None
    return {
        "id": daily.id,
        "book_id": daily.book_id,
        "daily_sentence": daily.daily_sentence,
        "daily_intro": daily.daily_intro,
        "publish_date": daily.publish_date.isoformat(),
        "is_top": daily.is_top,
        "like_count": daily.like_count,
        "book": book_item,
    }


async def get_today_daily() -> Optional[Dict[str, Any]]:
    today = date.today()
    daily = await DailyBook.get_or_none(publish_date=today, status=1)
    if not daily:
        daily = (
            await DailyBook.filter(status=1, publish_date__lte=today)
            .order_by("-publish_date")
            .first()
        )
    if not daily:
        return None
    return await daily_to_dict(daily)


async def list_daily_archive(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    qs = DailyBook.filter(status=1).order_by("-publish_date")
    total = await qs.count()
    items = await qs.offset((page - 1) * page_size).limit(page_size)
    return {
        "list": [await daily_to_dict(d) for d in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def like_daily(daily_id: int) -> int:
    daily = await DailyBook.get_or_none(id=daily_id, status=1)
    if not daily:
        raise ValueError("内容不存在")
    daily.like_count += 1
    await daily.save()
    return daily.like_count
