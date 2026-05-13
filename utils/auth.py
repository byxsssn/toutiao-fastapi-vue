from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from crud.users import get_user_by_token


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="无效 token")

    token = parts[1]
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    return user
