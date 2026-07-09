"""清空用户操作记录：收藏、浏览记录、读书喜好、订单、会员记录。"""
from __future__ import annotations

import asyncio
import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from tortoise import Tortoise

from app.db.database import TORTOISE_ORM
from app.models import MemberOrder, Order, OrderItem, UserBookCollect, UserMember, UserPreference


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)

    fav = await UserBookCollect.filter(collect_type=1).delete()
    hist = await UserBookCollect.filter(collect_type=2).delete()
    pref = await UserPreference.all().delete()
    orders = await Order.all().values_list("id", flat=True)
    items = await OrderItem.filter(order_id__in=list(orders)).delete() if orders else 0
    order_count = await Order.all().delete()
    member_orders = await MemberOrder.all().delete()
    members = await UserMember.all().delete()

    print("已清空用户操作记录：")
    print(f"  收藏：{fav} 条")
    print(f"  浏览记录：{hist} 条")
    print(f"  读书喜好：{pref} 条")
    print(f"  图书订单：{order_count} 笔（明细 {items} 条）")
    print(f"  会员订单：{member_orders} 笔")
    print(f"  会员状态：{members} 条")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
