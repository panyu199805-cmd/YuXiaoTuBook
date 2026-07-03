from __future__ import annotations

from starlette.staticfiles import StaticFiles
from starlette.types import Scope


class CachedStaticFiles(StaticFiles):
    """静态资源长缓存，减少视频/图片重复加载。"""

    async def get_response(self, path: str, scope: Scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200 and self._should_cache(path):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    @staticmethod
    def _should_cache(path: str) -> bool:
        lower = path.lower()
        return lower.endswith((".mp4", ".webm", ".jpg", ".jpeg", ".png", ".webp", ".svg"))
