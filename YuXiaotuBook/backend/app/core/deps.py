from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.response import http_error
from app.core.security import decode_token
from app.models import User

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    if not creds:
        return None
    payload = decode_token(creds.credentials)
    if not payload:
        return None
    user = await User.get_or_none(id=payload.get("sub"), status=1)
    return user


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise http_error(401, "请先登录")
    return user


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise http_error(403, "无管理员权限")
    return user
