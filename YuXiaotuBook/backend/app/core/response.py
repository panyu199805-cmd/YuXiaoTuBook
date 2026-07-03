from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def success(data: Optional[Any] = None, msg: str = "操作成功") -> JSONResponse:
    return JSONResponse(status_code=200, content={"code": 200, "msg": msg, "data": data})


def fail(msg: str, code: int = 400) -> JSONResponse:
    status = code if code in (400, 401, 403, 404, 500) else 400
    return JSONResponse(status_code=status, content={"code": code, "msg": msg, "data": None})


def http_error(code: int, msg: str) -> HTTPException:
    return HTTPException(status_code=code, detail={"code": code, "msg": msg, "data": None})
