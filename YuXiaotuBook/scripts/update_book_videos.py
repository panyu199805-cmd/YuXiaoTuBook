"""将所有图书解读视频 URL 更新为宇小兔介绍视频。"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))
sys.path.insert(0, os.path.dirname(__file__))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM
from app.models import BookVideo
from book_video_asset import BOOK_INTRO_VIDEO_INTRO, BOOK_INTRO_VIDEO_URL


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    videos = await BookVideo.all()
    updated = 0
    for video in videos:
        video.video_url = BOOK_INTRO_VIDEO_URL
        video.video_intro = BOOK_INTRO_VIDEO_INTRO
        await video.save()
        updated += 1
    print(f"已更新 {updated} 条图书视频为: {BOOK_INTRO_VIDEO_URL}")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
