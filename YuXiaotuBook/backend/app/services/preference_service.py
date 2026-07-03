from __future__ import annotations

import json
from typing import Any, Dict, List

from app.models import Category, UserPreference

MAX_CATEGORY_IDS = 8
ALLOWED_SCENE_TAGS = frozenset({"commute", "before_sleep", "weekend", "career"})


def _parse_json_list(raw: str) -> List[Any]:
    try:
        data = json.loads(raw or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


async def get_user_preferences(user_id: int) -> Dict[str, Any]:
    pref = await UserPreference.get_or_none(user_id=user_id)
    if not pref:
        return {"category_ids": [], "scene_tags": [], "bio": ""}
    return {
        "category_ids": _parse_json_list(pref.category_ids),
        "scene_tags": _parse_json_list(pref.scene_tags),
        "bio": pref.bio or "",
    }


async def save_user_preferences(
    user_id: int,
    category_ids: List[int],
    scene_tags: List[str],
    bio: str | None,
) -> Dict[str, Any]:
    if len(category_ids) > MAX_CATEGORY_IDS:
        raise ValueError(f"最多选择 {MAX_CATEGORY_IDS} 个分类")
    if len(set(category_ids)) != len(category_ids):
        raise ValueError("分类不能重复")
    for tag in scene_tags:
        if tag not in ALLOWED_SCENE_TAGS:
            raise ValueError("阅读场景标签无效")
    if bio and len(bio) > 100:
        raise ValueError("简介不能超过100字")

    if category_ids:
        count = await Category.filter(id__in=category_ids).count()
        if count != len(category_ids):
            raise ValueError("存在无效分类")

    payload = {
        "category_ids": json.dumps(category_ids),
        "scene_tags": json.dumps(scene_tags),
        "bio": (bio or "").strip() or None,
    }
    pref = await UserPreference.get_or_none(user_id=user_id)
    if pref:
        for k, v in payload.items():
            setattr(pref, k, v)
        await pref.save()
    else:
        pref = await UserPreference.create(user_id=user_id, **payload)
    return await get_user_preferences(user_id)
