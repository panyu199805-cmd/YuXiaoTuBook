"""user 表增加 province / city 字段（开发环境手动执行）"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM

ALTERS = [
    "ALTER TABLE user ADD COLUMN province VARCHAR(50) NULL",
    "ALTER TABLE user ADD COLUMN city VARCHAR(50) NULL",
]


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    for sql in ALTERS:
        try:
            await conn.execute_query(sql)
            print(f"OK: {sql}")
        except Exception as e:
            if "Duplicate column" in str(e) or "1060" in str(e):
                print(f"SKIP (exists): {sql}")
            else:
                raise
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
