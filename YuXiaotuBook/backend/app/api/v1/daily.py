from __future__ import annotations

from fastapi import APIRouter

from app.core.response import fail, success
from app.services.daily_service import get_today_daily, like_daily, list_daily_archive

router = APIRouter(tags=["每日读书"])


@router.get("/today", summary="今日读书")
async def today_daily():
    data = await get_today_daily()
    return success(data)


@router.get("/list", summary="历史归档")
async def daily_list(page: int = 1, page_size: int = 10):
    data = await list_daily_archive(page=page, page_size=page_size)
    return success(data)


@router.post("/{daily_id}/like", summary="点赞")
async def daily_like(daily_id: int):
    try:
        count = await like_daily(daily_id)
    except ValueError as e:
        return fail(str(e), 404)
    return success({"like_count": count})
