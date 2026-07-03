"""v1.5 用户个人中心：orders 物流字段 + user_preference 表（开发环境手动执行）"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM

ALTERS = [
    "ALTER TABLE orders ADD COLUMN ship_company VARCHAR(50) NULL",
    "ALTER TABLE orders ADD COLUMN ship_tracking_no VARCHAR(64) NULL",
    "ALTER TABLE orders ADD COLUMN shipped_at DATETIME(6) NULL",
    "ALTER TABLE orders ADD COLUMN completed_at DATETIME(6) NULL",
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
    await Tortoise.generate_schemas(safe=True)
    print("Schema sync done.")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
