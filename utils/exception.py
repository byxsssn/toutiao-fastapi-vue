import os
import traceback

from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.response import error_response

load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


def _debug_data(request, exc: Exception, include_traceback: bool = False):
    if not DEBUG_MODE:
        return None

    data = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "path": str(request.url),
    }

    if include_traceback:
        data["error_traceback"] = traceback.format_exc()

    return data


async def http_exception_handler(request, exc: HTTPException):
    return error_response(
        code=exc.status_code,
        message=exc.detail,
        debug=_debug_data(request, exc),
    )


async def integrity_error_handler(request, exc: IntegrityError):
    error_msg = str(getattr(exc, "orig", exc))

    if "username_unique" in error_msg or "Duplicate entry" in error_msg:
        message = "用户名已存在"
    elif "FOREIGN KEY" in error_msg:
        message = "关联数据不存在"
    else:
        message = "数据约束冲突"

    return error_response(
        code=400,
        message=message,
        debug=_debug_data(request, exc),
    )


async def sqlalchemy_error_handler(request, exc: SQLAlchemyError):
    return error_response(
        code=500,
        message="数据库错误",
        debug=_debug_data(request, exc, include_traceback=True),
    )


async def generic_exception_handler(request, exc: Exception):
    return error_response(
        code=500,
        message="服务器错误",
        debug=_debug_data(request, exc, include_traceback=True),
    )
