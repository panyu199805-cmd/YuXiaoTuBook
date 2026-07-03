"""将 picsum 等不可达外链封面替换为本地 /placeholders/ 路径。"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM
from app.models import Book, BookVideo

SCRIPTS_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(SCRIPTS_DIR))
from book_covers import cover_path_by_title


def local_cover(book_id: int, title: str = "") -> str:
    return cover_path_by_title(title, fallback_id=book_id)


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)

    book_count = 0
    for book in await Book.all():
        if book.cover.startswith("http"):
            book.cover = local_cover(book.id, book.title)
            await book.save()
            book_count += 1

    video_count = 0
    for video in await BookVideo.all():
        if video.video_cover.startswith("http"):
            video.video_cover = local_cover(video.book_id)
            await video.save()
            video_count += 1

    print(f"已更新书籍封面 {book_count} 条，视频封面 {video_count} 条。")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
