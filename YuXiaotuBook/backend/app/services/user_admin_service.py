from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.models import Book, MemberOrder, Order, User, UserBookCollect
from app.services.book_service import book_list_item
from app.services.member_service import get_member_profile, member_order_to_dict
from app.services.order_helpers import order_to_dict

UNKNOWN_PROVINCE = "未填写"
UNKNOWN_CITY = "未填写"


def _region(value: Optional[str], default: str) -> str:
    text = (value or "").strip()
    return text or default


async def build_user_region_tree() -> List[Dict[str, Any]]:
    users = await User.filter(role="user").order_by("id")
    province_map: Dict[str, Dict[str, List[User]]] = {}
    for user in users:
        prov = _region(user.province, UNKNOWN_PROVINCE)
        city = _region(user.city, UNKNOWN_CITY)
        province_map.setdefault(prov, {}).setdefault(city, []).append(user)

    tree: List[Dict[str, Any]] = []
    for prov in sorted(province_map.keys()):
        cities = province_map[prov]
        prov_count = sum(len(v) for v in cities.values())
        city_nodes: List[Dict[str, Any]] = []
        for city in sorted(cities.keys()):
            city_users = cities[city]
            user_nodes = [
                {
                    "id": f"user:{u.id}",
                    "label": f"{u.nickname}（{u.username}）",
                    "type": "user",
                    "user_id": u.id,
                    "isLeaf": True,
                }
                for u in city_users
            ]
            city_nodes.append(
                {
                    "id": f"city:{prov}:{city}",
                    "label": f"{city}（{len(city_users)}）",
                    "type": "city",
                    "province": prov,
                    "city": city,
                    "count": len(city_users),
                    "children": user_nodes,
                }
            )
        tree.append(
            {
                "id": f"province:{prov}",
                "label": f"{prov}（{prov_count}）",
                "type": "province",
                "province": prov,
                "count": prov_count,
                "children": city_nodes,
            }
        )
    return tree


async def get_admin_user_detail(user_id: int) -> Dict[str, Any]:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")

    member = await get_member_profile(user.id)
    favorites: List[Dict[str, Any]] = []
    collects = await UserBookCollect.filter(user_id=user.id, collect_type=1).order_by("-created_at")
    for c in collects:
        book = await Book.get_or_none(id=c.book_id)
        if book:
            item = await book_list_item(book)
            item["collected_at"] = c.created_at.isoformat() if c.created_at else None
            favorites.append(item)

    orders = await Order.filter(user_id=user.id).order_by("-created_at")
    order_list = [await order_to_dict(o) for o in orders]

    member_orders = [
        member_order_to_dict(mo)
        for mo in await MemberOrder.filter(user_id=user.id).order_by("-created_at")
    ]

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "province": _region(user.province, UNKNOWN_PROVINCE),
        "city": _region(user.city, UNKNOWN_CITY),
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "member": member,
        "favorites": favorites,
        "orders": order_list,
        "member_orders": member_orders,
        "stats": {
            "favorite_count": len(favorites),
            "book_order_count": len(order_list),
            "member_order_count": len(member_orders),
        },
    }
