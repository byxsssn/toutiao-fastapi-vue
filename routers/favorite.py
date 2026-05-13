from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from crud.favorite import add_favorite, is_favorite, remove_favorite
from schemas.favorite import FavoriteCheck
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter()


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await is_favorite(db, user.id, news_id)
    return success_response(
        message="检查收藏成功",
        data=FavoriteCheck(is_favorite=result),
    )


@router.post("/")
async def create_favorite(
    news_id: int = Query(..., alias="newsId"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await add_favorite(db, user.id, news_id)
    return success_response(
        message="收藏成功",
        data=FavoriteCheck(is_favorite=result),
    )


@router.delete("/")
async def delete_favorite(
    news_id: int = Query(..., alias="newsId"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await remove_favorite(db, user.id, news_id)
    return success_response(
        message="取消收藏成功",
        data=FavoriteCheck(is_favorite=result),
    )
