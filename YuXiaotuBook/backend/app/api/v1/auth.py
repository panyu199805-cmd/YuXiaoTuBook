from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.response import fail, success
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.requests import LoginRequest, RegisterRequest, validate_username
from app.services.member_service import get_member_profile

router = APIRouter()


@router.post("/register", tags=["用户-认证"], summary="用户注册")
async def register(body: RegisterRequest):
    if not validate_username(body.username):
        return fail("用户名须为4-20位字母数字下划线", 400)
    exists = await User.filter(username=body.username).exists()
    if exists:
        return fail("用户名已存在", 40003)
    user = await User.create(
        username=body.username,
        password_hash=hash_password(body.password),
        nickname=body.nickname or body.username,
        province=(body.province or "").strip() or None,
        city=(body.city or "").strip() or None,
        role="user",
    )
    token = create_access_token(user.id, user.role)
    return success(
        {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "role": user.role,
            },
        },
        "注册成功",
    )


@router.post("/login", tags=["Admin-认证"], summary="登录（管理员/用户）")
async def login(body: LoginRequest):
    user = await User.get_or_none(username=body.username, status=1)
    if not user or not verify_password(body.password, user.password_hash):
        return fail("用户名或密码错误", 401)
    token = create_access_token(user.id, user.role)
    return success(
        {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "role": user.role,
            },
        },
        "登录成功",
    )


@router.get("/me", tags=["Admin-认证"], summary="当前用户信息")
async def me(user: User = Depends(get_current_user)):
    profile = await get_member_profile(user.id)
    return success(
        {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "role": user.role,
            "is_vip": profile.get("is_vip", False),
            "vip_expire_time": profile.get("expire_time"),
        }
    )
