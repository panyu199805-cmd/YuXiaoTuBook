"""为《非暴力沟通》写入电子书解读内容。"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))
sys.path.insert(0, os.path.dirname(__file__))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM
from app.models import Book, BookVideo
from ebooks.fei_bao_li_gou_tong import EBOOK_CONTENT


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    book = await Book.get_or_none(title="非暴力沟通")
    if not book:
        print("未找到书籍：非暴力沟通")
        await Tortoise.close_connections()
        return
    video = await BookVideo.get_or_none(book_id=book.id)
    if not video:
        print(f"书籍 {book.id} 暂无视频记录")
        await Tortoise.close_connections()
        return
    video.explain_content = EBOOK_CONTENT
    await video.save()
    print(f"已更新《{book.title}》电子书内容，共 {len(EBOOK_CONTENT)} 字")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
