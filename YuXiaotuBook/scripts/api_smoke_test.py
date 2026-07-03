"""Customer-YuXiaotuBook 管理后台 + 业务域接口冒烟测试

交易域（/orders、/member）由 Java trade-service :8081 提供。
"""
from __future__ import annotations

import json
import os
import sys
import uuid

try:
    import httpx
except ImportError:
    print("FAIL: pip install httpx")
    sys.exit(1)

BASE = os.getenv("PYTHON_BASE", "http://127.0.0.1:8000")
TRADE_BASE = os.getenv("TRADE_BASE", "http://127.0.0.1:8081")
PROXY_BASE = "http://localhost:5188"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123456"

passed = 0
failed = 0
results: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        results.append((name, True, detail or "OK"))
    else:
        failed += 1
        results.append((name, False, detail or "FAILED"))


def _is_trade_path(path: str) -> bool:
    return path.startswith("/api/v1/orders") or path.startswith("/api/v1/member")


def api(client: httpx.Client, method: str, path: str, **kwargs):
    base = TRADE_BASE if _is_trade_path(path) else BASE
    r = client.request(method, f"{base}{path}", **kwargs)
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:200]}
    return r.status_code, body


def main() -> int:
    suffix = uuid.uuid4().hex[:6]
    test_slug = f"api_test_{suffix}"
    test_book_title = f"API测试书_{suffix}"
    created_cat_id = None
    created_book_id = None

    with httpx.Client(timeout=30.0) as client:
        # --- 系统 ---
        code, body = api(client, "GET", "/api/health")
        ok("GET /api/health (Python)", code == 200 and body.get("code") == 200, f"code={body.get('code')}")

        r = client.get(f"{TRADE_BASE}/api/health")
        try:
            trade_health = r.json()
        except Exception:
            trade_health = {}
        ok(
            "GET /api/health (Java trade)",
            r.status_code == 200 and trade_health.get("code") == 200,
            f"status={r.status_code}",
        )

        # --- 认证 ---
        code, body = api(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"username": ADMIN_USER, "password": "wrong_password"},
        )
        ok("POST /auth/login 错误密码", body.get("code") == 401, f"code={body.get('code')}")

        code, body = api(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"username": ADMIN_USER, "password": ADMIN_PASS},
        )
        token = body.get("data", {}).get("token")
        role = body.get("data", {}).get("user", {}).get("role")
        ok("POST /auth/login 管理员", code == 200 and token and role == "admin", f"role={role}")

        code, body = api(client, "GET", "/api/v1/admin/books")
        ok("Admin 无 token 拒绝", code == 401, f"status={code}")

        headers = {"Authorization": f"Bearer {token}"}
        code, body = api(client, "GET", "/api/v1/auth/me", headers=headers)
        ok("GET /auth/me", code == 200 and body.get("data", {}).get("role") == "admin")

        # --- Admin 列表 ---
        for path in [
            "/api/v1/admin/books",
            "/api/v1/admin/videos",
            "/api/v1/admin/categories",
            "/api/v1/admin/orders",
            "/api/v1/admin/site-config",
        ]:
            code, body = api(client, "GET", path, headers=headers)
            data = body.get("data")
            if isinstance(data, dict) and "list" in data:
                item_hint = f"items={len(data.get('list') or [])}"
            elif isinstance(data, list):
                item_hint = f"items={len(data)}"
            else:
                item_hint = "obj"
            ok(f"GET {path}", code == 200 and body.get("code") == 200, item_hint)

        # --- 分类 CRUD ---
        code, body = api(
            client,
            "POST",
            "/api/v1/admin/categories",
            headers=headers,
            json={"name": f"测试分类_{suffix}", "slug": test_slug, "sort_order": 99},
        )
        created_cat_id = body.get("data", {}).get("id")
        ok("POST /admin/categories", code == 200 and created_cat_id, f"id={created_cat_id}")

        # --- 书籍 CRUD ---
        cats_code, cats_body = api(client, "GET", "/api/v1/admin/categories", headers=headers)
        cat_id = (cats_body.get("data") or [{}])[0].get("id", 1)
        code, body = api(
            client,
            "POST",
            "/api/v1/admin/books",
            headers=headers,
            json={
                "title": test_book_title,
                "author": "测试作者",
                "cover": "/placeholders/books/bei-tao-yan-de-yong-qi.svg",
                "category_id": cat_id,
                "price": 19.9,
                "stock": 10,
                "summary": "冒烟测试书籍",
                "status": "published",
            },
        )
        created_book_id = body.get("data", {}).get("id")
        ok("POST /admin/books", code == 200 and created_book_id, f"id={created_book_id}")

        if created_book_id:
            code, body = api(
                client,
                "PUT",
                f"/api/v1/admin/books/{created_book_id}",
                headers=headers,
                json={"stock": 20, "highlight": "测试金句"},
            )
            ok("PUT /admin/books/{id}", code == 200 and body.get("data", {}).get("stock") == 20)

        # --- 视频绑定 ---
        if created_book_id:
            code, body = api(
                client,
                "POST",
                "/api/v1/admin/videos",
                headers=headers,
                json={
                    "book_id": created_book_id,
                    "video_cover": "/placeholders/books/bei-tao-yan-de-yong-qi.svg",
                    "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "video_duration": 120,
                    "video_intro": "冒烟测试视频",
                    "status": 1,
                },
            )
            ok("POST /admin/videos", code == 200 and body.get("data", {}).get("id"), str(body.get("data")))

        # --- 氛围配置 ---
        code, body = api(
            client,
            "PUT",
            "/api/v1/admin/site-config",
            headers=headers,
            json={
                "bg_type": "image",
                "bg_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "daily_sentence": f"冒烟测试金句_{suffix}",
                "featured_book_id": created_book_id,
                "music_enabled": False,
                "bg_enabled": True,
            },
        )
        ok("PUT /admin/site-config", code == 200 and body.get("code") == 200)

        code, body = api(client, "GET", "/api/v1/admin/site-config", headers=headers)
        sentence = (body.get("data") or {}).get("daily_sentence", "")
        ok("GET /admin/site-config 回读", sentence == f"冒烟测试金句_{suffix}", f"sentence={sentence[:30]}")

        # --- 清理 ---
        if created_book_id:
            code, body = api(client, "DELETE", f"/api/v1/admin/books/{created_book_id}", headers=headers)
            ok("DELETE /admin/books/{id}", code == 200 and body.get("code") == 200)

        if created_cat_id:
            code, body = api(client, "DELETE", f"/api/v1/admin/categories/{created_cat_id}", headers=headers)
            ok("DELETE /admin/categories/{id}", code == 200 and body.get("code") == 200)

        # --- 前台公开接口 ---
        for path in ["/api/v1/home/hot-books", "/api/v1/categories", "/api/v1/site/config"]:
            code, body = api(client, "GET", path)
            ok(f"GET {path}", code == 200 and body.get("code") == 200)

        # --- 二期：每日读书 ---
        code, body = api(client, "GET", "/api/v1/daily/today")
        ok("GET /daily/today", code == 200 and body.get("code") == 200)

        code, body = api(client, "GET", "/api/v1/daily/list", params={"page": 1, "page_size": 5})
        daily_list = (body.get("data") or {}).get("list") or []
        ok("GET /daily/list", code == 200 and isinstance(daily_list, list), f"count={len(daily_list)}")

        if daily_list:
            daily_id = daily_list[0]["id"]
            code, body = api(client, "POST", f"/api/v1/daily/{daily_id}/like")
            ok("POST /daily/{id}/like", code == 200 and "like_count" in (body.get("data") or {}))

        # --- 二期：会员套餐 ---
        code, body = api(client, "GET", "/api/v1/member/packages")
        packages = body.get("data") or []
        ok("GET /member/packages", code == 200 and isinstance(packages, list) and len(packages) > 0)

        # --- 二期：play-auth 游客试看 ---
        books_code, books_body = api(client, "GET", "/api/v1/books", params={"page": 1, "page_size": 20})
        video_book_id = None
        for b in (books_body.get("data") or {}).get("list") or []:
            if b.get("has_video"):
                video_book_id = b["id"]
                break
        if video_book_id:
            code, body = api(client, "GET", f"/api/v1/books/{video_book_id}/play-auth")
            data = body.get("data") or {}
            ok(
                "GET play-auth 游客",
                code == 200 and data.get("full_access") is False and data.get("max_duration") == 180,
                f"full_access={data.get('full_access')} max={data.get('max_duration')}",
            )
            code, body = api(client, "GET", f"/api/v1/books/{video_book_id}/play-auth", headers=headers)
            data = body.get("data") or {}
            ok(
                "GET play-auth 登录用户",
                code == 200 and data.get("full_access") is True,
                f"full_access={data.get('full_access')}",
            )
        else:
            ok("GET play-auth 游客", False, "无带视频书籍")
            ok("GET play-auth 登录用户", False, "无带视频书籍")

        # --- 二期：模拟开通会员 ---
        if packages:
            pkg_id = packages[0]["id"]
            code, body = api(
                client,
                "POST",
                "/api/v1/member/subscribe",
                headers=headers,
                json={"package_id": pkg_id},
            )
            order_id = (body.get("data") or {}).get("id")
            ok("POST /member/subscribe", code == 200 and order_id, f"order_id={order_id}")
            if order_id:
                code, body = api(
                    client,
                    "POST",
                    f"/api/v1/member/orders/{order_id}/mock-pay",
                    headers=headers,
                )
                ok(
                    "POST /member/orders/{id}/mock-pay",
                    code == 200 and body.get("code") == 200,
                    f"code={body.get('code')} msg={body.get('msg')}",
                )
                code, body = api(client, "GET", "/api/v1/member/status", headers=headers)
                ok(
                    "GET /member/status",
                    code == 200 and body.get("data", {}).get("is_vip") is True,
                    f"is_vip={body.get('data', {}).get('is_vip')}",
                )
                code, body = api(client, "GET", "/api/v1/auth/me", headers=headers)
                ok(
                    "GET /auth/me is_vip",
                    code == 200 and body.get("data", {}).get("is_vip") is True,
                    f"is_vip={body.get('data', {}).get('is_vip')}",
                )

        # --- 二期：浏览记录 ---
        if video_book_id:
            api(client, "GET", f"/api/v1/books/{video_book_id}", headers=headers)
            code, body = api(client, "GET", "/api/v1/history", headers=headers)
            history = body.get("data") or []
            ok(
                "GET /history",
                code == 200 and any(h.get("id") == video_book_id for h in history),
                f"count={len(history)}",
            )
        else:
            ok("GET /history", False, "无带视频书籍")

        # --- 二期：Admin daily/member CRUD ---
        books_code, books_body = api(client, "GET", "/api/v1/admin/books", headers=headers)
        seed_book_id = ((books_body.get("data") or [{}])[0]).get("id")
        created_daily_id = None
        created_pkg_id = None
        if seed_book_id:
            code, body = api(
                client,
                "POST",
                "/api/v1/admin/daily",
                headers=headers,
                json={
                    "book_id": seed_book_id,
                    "daily_sentence": f"冒烟测试金句_{suffix}",
                    "daily_intro": "冒烟测试简介",
                    "publish_date": "2099-01-01",
                    "is_top": False,
                    "status": 1,
                },
            )
            created_daily_id = (body.get("data") or {}).get("id")
            ok("POST /admin/daily", code == 200 and created_daily_id, f"id={created_daily_id}")

        code, body = api(client, "GET", "/api/v1/admin/daily", headers=headers)
        ok("GET /admin/daily", code == 200 and body.get("code") == 200)

        code, body = api(
            client,
            "POST",
            "/api/v1/admin/member/packages",
            headers=headers,
            json={
                "package_name": f"测试套餐_{suffix}",
                "price": 9.9,
                "valid_day": 7,
                "rights": json.dumps(["测试权益"]),
                "status": 1,
            },
        )
        created_pkg_id = (body.get("data") or {}).get("id")
        ok("POST /admin/member/packages", code == 200 and created_pkg_id, f"id={created_pkg_id}")

        code, body = api(client, "GET", "/api/v1/admin/member/packages", headers=headers)
        ok("GET /admin/member/packages", code == 200 and body.get("code") == 200)

        if created_daily_id:
            code, body = api(
                client, "DELETE", f"/api/v1/admin/daily/{created_daily_id}", headers=headers
            )
            ok("DELETE /admin/daily/{id}", code == 200 and body.get("code") == 200)
        if created_pkg_id:
            code, body = api(
                client, "DELETE", f"/api/v1/admin/member/packages/{created_pkg_id}", headers=headers
            )
            ok("DELETE /admin/member/packages/{id}", code == 200 and body.get("code") == 200)

        for path in [
            "/api/v1/admin/daily",
            "/api/v1/admin/member/packages",
        ]:
            code, body = api(client, "GET", path, headers=headers)
            ok(f"GET {path} 列表", code == 200 and body.get("code") == 200)

        # --- v1.5：用户个人中心 ---
        code, body = api(client, "GET", "/api/v1/user/preferences", headers=headers)
        ok("GET /user/preferences", code == 200 and body.get("code") == 200)

        cats_code, cats_body = api(client, "GET", "/api/v1/categories")
        cat_ids = [c["id"] for c in (cats_body.get("data") or [])[:2]]
        code, body = api(
            client,
            "PUT",
            "/api/v1/user/preferences",
            headers=headers,
            json={
                "category_ids": cat_ids,
                "scene_tags": ["commute", "before_sleep"],
                "bio": "冒烟测试喜好",
            },
        )
        ok("PUT /user/preferences", code == 200 and body.get("code") == 200)

        code, body = api(client, "GET", "/api/v1/user/orders/shipping", headers=headers)
        ship_list = body.get("data") or []
        ok("GET /user/orders/shipping", code == 200 and isinstance(ship_list, list))

        paid_order = next((o for o in ship_list if o.get("status") == "paid"), None)
        if not paid_order:
            admin_orders_code, admin_orders_body = api(
                client, "GET", "/api/v1/admin/orders", headers=headers
            )
            admin_data = admin_orders_body.get("data") or {}
            admin_list = admin_data.get("list") if isinstance(admin_data, dict) else admin_data
            paid_order = next(
                (o for o in (admin_list or []) if o.get("status") == "paid"),
                None,
            )
        if paid_order:
            code, body = api(
                client,
                "PUT",
                f"/api/v1/admin/orders/{paid_order['id']}/ship",
                headers=headers,
                json={"ship_company": "顺丰速运", "ship_tracking_no": f"SF{suffix}"},
            )
            ship_data = body.get("data") or {}
            ok(
                "PUT /admin/orders/{id}/ship",
                code == 200 and ship_data.get("status") == "shipped",
                f"status={ship_data.get('status')}",
            )
            ok(
                "GET shipping 运输中",
                ship_data.get("ship_tracking_no") == f"SF{suffix}",
                f"tracking={ship_data.get('ship_tracking_no')}",
            )
        else:
            ok("PUT /admin/orders/{id}/ship", False, "无 paid 订单可测发货")
            ok("GET shipping 运输中", False, "无 paid 订单")

        # --- Admin 用户管理 ---
        code, body = api(client, "GET", "/api/v1/admin/users/tree", headers=headers)
        tree = (body.get("data") or {}).get("tree") or []
        ok("GET /admin/users/tree", code == 200 and isinstance(tree, list), f"provinces={len(tree)}")
        demo_user_id = None
        for prov in tree:
            for city in prov.get("children") or []:
                for u in city.get("children") or []:
                    if u.get("type") == "user":
                        demo_user_id = u.get("user_id")
                        break
                if demo_user_id:
                    break
            if demo_user_id:
                break
        if demo_user_id:
            code, body = api(client, "GET", f"/api/v1/admin/users/{demo_user_id}", headers=headers)
            ok(
                "GET /admin/users/{id}",
                code == 200 and body.get("data", {}).get("id") == demo_user_id,
                f"orders={len(body.get('data', {}).get('orders') or [])}",
            )
        else:
            ok("GET /admin/users/{id}", False, "树中无用户节点")

    # --- 前端代理 ---
    try:
        with httpx.Client(timeout=10.0) as proxy_client:
            r = proxy_client.get(f"{PROXY_BASE}/api/health")
            body = r.json()
            ok("前端代理 /api/health", r.status_code == 200 and body.get("code") == 200, PROXY_BASE)
    except Exception as e:
        ok("前端代理 /api/health", False, str(e))

    print("\n=== Customer-YuXiaotuBook API 冒烟测试 ===\n")
    for name, success, detail in results:
        mark = "PASS" if success else "FAIL"
        print(f"[{mark}] {name}  ->  {detail}")
    print(f"\n合计: {passed} 通过, {failed} 失败, 共 {passed + failed} 项")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
