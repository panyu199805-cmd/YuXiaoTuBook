"""生成每本书独立的 SVG 封面，并可选更新数据库。"""
from __future__ import annotations

import asyncio
import html
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from book_covers import BOOK_COVER_SPECS, TITLE_TO_COVER

OUTPUT_DIR = os.path.join(BACKEND_DIR, "static", "placeholders", "books")
FRONTEND_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "frontend", "public", "placeholders", "books"
)


def _split_title(title: str) -> list[str]:
    if len(title) <= 4:
        return [title]
    mid = len(title) // 2
    return [title[:mid], title[mid:]]


def render_svg(spec: dict) -> str:
    title = str(spec["title"])
    author = str(spec["author"])
    colors = spec["colors"]
    accent = str(spec["accent"])
    lines = _split_title(title)
    title_y = 250 if len(lines) == 1 else 230
    title_lines = "".join(
        f'<tspan x="200" dy="{36 if i else 0}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{colors[0]}"/>
      <stop offset="100%" stop-color="{colors[1]}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="560" fill="url(#bg)"/>
  <rect x="28" y="36" width="344" height="488" rx="10" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)"/>
  <circle cx="320" cy="92" r="42" fill="{accent}" opacity="0.22"/>
  <rect x="52" y="72" width="72" height="8" rx="4" fill="{accent}" opacity="0.85"/>
  <rect x="52" y="92" width="48" height="6" rx="3" fill="{accent}" opacity="0.55"/>
  <text x="200" y="{title_y}" fill="#ffffff" font-size="34" font-family="Microsoft YaHei, PingFang SC, sans-serif" font-weight="700" text-anchor="middle">{title_lines}</text>
  <line x1="80" y1="360" x2="320" y2="360" stroke="{accent}" stroke-width="2" opacity="0.45"/>
  <text x="200" y="410" fill="{accent}" font-size="20" font-family="Microsoft YaHei, PingFang SC, sans-serif" text-anchor="middle">{html.escape(author)}</text>
  <text x="200" y="470" fill="rgba(255,255,255,0.72)" font-size="14" font-family="Microsoft YaHei, PingFang SC, sans-serif" text-anchor="middle">宇小兔 · 每日读书</text>
</svg>
"""


def write_covers() -> None:
    for spec in BOOK_COVER_SPECS:
        content = render_svg(spec)
        filename = f"{spec['slug']}.svg"
        for target in (OUTPUT_DIR, FRONTEND_OUTPUT_DIR):
            os.makedirs(target, exist_ok=True)
            with open(os.path.join(target, filename), "w", encoding="utf-8") as f:
                f.write(content)
    print(f"已生成 {len(BOOK_COVER_SPECS)} 张封面 -> {OUTPUT_DIR}")


async def update_database() -> None:
    from tortoise import Tortoise

    from app.db.database import TORTOISE_ORM
    from app.models import Book, BookVideo

    await Tortoise.init(config=TORTOISE_ORM)

    book_count = 0
    for book in await Book.all():
        cover = TITLE_TO_COVER.get(book.title)
        if not cover:
            continue
        if book.cover != cover:
            book.cover = cover
            await book.save()
            book_count += 1

    video_count = 0
    for video in await BookVideo.all():
        book = await Book.get_or_none(id=video.book_id)
        if not book:
            continue
        cover = TITLE_TO_COVER.get(book.title)
        if not cover or video.video_cover == cover:
            continue
        video.video_cover = cover
        await video.save()
        video_count += 1

    print(f"已更新书籍封面 {book_count} 条，视频封面 {video_count} 条。")
    await Tortoise.close_connections()


async def main() -> None:
    write_covers()
    await update_database()


if __name__ == "__main__":
    asyncio.run(main())
