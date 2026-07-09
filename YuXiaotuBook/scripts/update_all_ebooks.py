"""为全站书籍写入电子书解读（版式同《非暴力沟通》）。"""
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
from ebooks.catalog import ALL_EBOOK_TITLES, DEFAULT_VIDEO_URL, ebook_content_for


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    updated = 0
    created_video = 0

    for title in ALL_EBOOK_TITLES:
        book = await Book.get_or_none(title=title)
        if not book:
            print(f"跳过（未找到书籍）：{title}")
            continue

        video = await BookVideo.get_or_none(book_id=book.id)
        if not video:
            video = await BookVideo.create(
                book_id=book.id,
                video_cover=book.cover,
                video_url=DEFAULT_VIDEO_URL,
                video_duration=360,
                video_intro="3分钟读懂全书精华",
                status=1,
            )
            created_video += 1
            print(f"已创建视频记录：{title}")

        content = ebook_content_for(title)
        video.explain_content = content
        await video.save()
        updated += 1
        print(f"已更新《{title}》电子书，共 {len(content)} 字")

    print(f"\n完成：更新 {updated} 本，新建视频 {created_video} 条。")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
