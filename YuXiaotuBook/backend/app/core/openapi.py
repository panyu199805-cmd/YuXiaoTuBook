from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


OPENAPI_TAGS = [
    {"name": "Admin-认证", "description": "管理员登录与当前用户信息"},
    {"name": "Admin-书籍", "description": "书籍增删改查"},
    {"name": "Admin-视频", "description": "书籍视频绑定与管理"},
    {"name": "Admin-分类", "description": "分类维护"},
    {"name": "Admin-订单", "description": "订单查询与状态变更"},
    {"name": "Admin-氛围配置", "description": "首页氛围与站点配置"},
    {"name": "Admin-上传", "description": "图片上传"},
    {"name": "Admin-每日读书", "description": "每日读书内容管理"},
    {"name": "Admin-会员", "description": "会员套餐与订单"},
    {"name": "Admin-用户", "description": "用户管理与地区分组"},
    {"name": "每日读书", "description": "每日读书专栏"},
    {"name": "会员", "description": "会员相关（C 端开通已迁移至 Java trade-service）"},
    {"name": "用户-个人中心", "description": "读书喜好与收发货"},
    {"name": "用户-认证", "description": "用户注册登录"},
    {"name": "首页", "description": "首页推荐与热门书籍"},
    {"name": "站点", "description": "站点公开配置与分类"},
    {"name": "书籍", "description": "前台书籍浏览"},
    {"name": "收藏", "description": "收藏与浏览记录"},
    {"name": "订单", "description": "用户下单（C 端已迁移至 Java trade-service）"},
    {"name": "系统", "description": "健康检查"},
]


def setup_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "BearerAuth"
        ] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "登录后获取 token，格式：Bearer {token}",
        }

        for path, methods in schema.get("paths", {}).items():
            if path.startswith("/api/v1/admin") or path == "/api/v1/auth/me" or path.startswith("/api/v1/user"):
                for method in methods.values():
                    if isinstance(method, dict):
                        method.setdefault("security", [{"BearerAuth": []}])

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
