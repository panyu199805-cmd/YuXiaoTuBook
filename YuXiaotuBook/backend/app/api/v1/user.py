from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.response import fail, success
from app.models import Order, User
from app.schemas.requests import UserPreferenceRequest
from app.services.order_helpers import order_to_dict
from app.services.preference_service import get_user_preferences, save_user_preferences

router = APIRouter(tags=["用户-个人中心"])

SHIPPING_STATUSES = ("paid", "shipped", "completed", "cancelled")


@router.get("/preferences", summary="获取读书喜好")
async def get_preferences(user: User = Depends(get_current_user)):
    return success(await get_user_preferences(user.id))


@router.put("/preferences", summary="保存读书喜好")
async def update_preferences(body: UserPreferenceRequest, user: User = Depends(get_current_user)):
    try:
        data = await save_user_preferences(
            user.id, body.category_ids, body.scene_tags, body.bio
        )
    except ValueError as e:
        return fail(str(e), 400)
    return success(data, "保存成功")


@router.get("/orders/shipping", summary="已购书籍收发货列表")
async def list_shipping_orders(user: User = Depends(get_current_user)):
    orders = await Order.filter(user_id=user.id, status__in=SHIPPING_STATUSES).order_by(
        "-created_at"
    )
    result = [await order_to_dict(o) for o in orders]
    return success(result)
