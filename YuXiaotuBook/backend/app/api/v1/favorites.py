from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.response import fail, success
from app.models import Book, User, UserBookCollect
from app.schemas.requests import FavoriteRequest
from app.services.collect_service import list_user_collected_books

router = APIRouter()
history_router = APIRouter()


@router.post("")
async def add_favorite(body: FavoriteRequest, user: User = Depends(get_current_user)):
    book = await Book.get_or_none(id=body.book_id, status="published")
    if not book:
        return fail("书籍不存在", 404)
    exists = await UserBookCollect.filter(
        user_id=user.id, book_id=body.book_id, collect_type=1
    ).exists()
    if not exists:
        await UserBookCollect.create(
            user_id=user.id, book_id=body.book_id, collect_type=1
        )
    return success(None, "收藏成功")


@router.delete("/{book_id}")
async def remove_favorite(book_id: int, user: User = Depends(get_current_user)):
    await UserBookCollect.filter(
        user_id=user.id, book_id=book_id, collect_type=1
    ).delete()
    return success(None, "已取消收藏")


@router.get("")
async def list_favorites(user: User = Depends(get_current_user)):
    items = await list_user_collected_books(user.id, collect_type=1, published_only=True)
    return success(items)


@history_router.get("")
async def list_history(user: User = Depends(get_current_user)):
    items = await list_user_collected_books(user.id, collect_type=2)
    return success(items)
