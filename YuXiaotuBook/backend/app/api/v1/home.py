from __future__ import annotations

from fastapi import APIRouter

from app.core.response import success
from app.models import Book, Category, SiteConfig
from app.services.book_service import book_list_item, book_to_dict
from app.services.site_config_helpers import public_site_config_dict

router = APIRouter()
site_router = APIRouter()


@site_router.get("/site/config", tags=["站点"], summary="站点公开配置")
async def site_config():
    cfg = await SiteConfig.all().order_by("-id").first()
    if not cfg:
        return success(None)
    return success(public_site_config_dict(cfg))


@router.get("/featured", tags=["首页"], summary="主推书籍")
async def featured():
    cfg = await SiteConfig.all().order_by("-id").first()
    if not cfg or not cfg.featured_book_id:
        return success(None)
    book = await Book.get_or_none(id=cfg.featured_book_id, status="published")
    if not book:
        return success(None)
    return success(await book_to_dict(book))


@router.get("/hot-books", tags=["首页"], summary="热门书籍")
async def hot_books(page: int = 1, page_size: int = 12):
    offset = (page - 1) * page_size
    qs = Book.filter(status="published").order_by("-view_count", "-id")
    total = await qs.count()
    books = await qs.offset(offset).limit(page_size)
    items = [await book_list_item(b) for b in books]
    return success({"list": items, "total": total, "page": page, "page_size": page_size})


@site_router.get("/categories", tags=["站点"], summary="公开分类列表")
async def categories():
    cats = await Category.all().order_by("sort_order", "id")
    return success([{"id": c.id, "name": c.name, "slug": c.slug} for c in cats])
