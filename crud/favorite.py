from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite


async def get_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
) -> Favorite | None:
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id,
        )
    )
    return result.scalar_one_or_none()


async def is_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    return await get_favorite(db, user_id, news_id) is not None


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    if await is_favorite(db, user_id, news_id):
        return True

    db.add(Favorite(user_id=user_id, news_id=news_id))
    await db.commit()
    return True


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id,
        )
    )
    await db.commit()
    return False
