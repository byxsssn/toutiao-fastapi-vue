from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import Token, User
from schemas.users import UserRegister, UserUpdate
from utils.security import get_hashed_password, verify_password


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


def _new_token_value() -> str:
    return str(uuid.uuid4())


def _new_token_expires() -> datetime:
    return datetime.now() + timedelta(days=7)


async def create_user_with_token(
    db: AsyncSession,
    user: UserRegister,
) -> tuple[User, str]:
    hashed_password = get_hashed_password(user.password)
    new_user = User(
        username=user.username,
        password=hashed_password,
    )

    try:
        db.add(new_user)
        await db.flush()

        token = _new_token_value()
        db.add(
            Token(
                user_id=new_user.id,
                token=token,
                expires=_new_token_expires(),
            )
        )

        await db.commit()
        await db.refresh(new_user)
        return new_user, token
    except Exception:
        await db.rollback()
        raise


async def refresh_user_token(db: AsyncSession, user_id: int) -> str:
    token = _new_token_value()
    expires = _new_token_expires()

    result = await db.execute(select(Token).where(Token.user_id == user_id))
    existing_token = result.scalar_one_or_none()

    try:
        if existing_token:
            existing_token.token = token
            existing_token.expires = expires
        else:
            db.add(Token(user_id=user_id, token=token, expires=expires))

        await db.commit()
        return token
    except Exception:
        await db.rollback()
        raise


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None

    return user


async def get_user_by_token(db: AsyncSession, token_value: str) -> User | None:
    result = await db.execute(
        select(User)
        .join(Token, User.id == Token.user_id)
        .where(Token.token == token_value, Token.expires > datetime.now())
    )
    return result.scalar_one_or_none()


async def update_user_profile(
    db: AsyncSession,
    user_id: int,
    update_data: UserUpdate,
) -> User:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    values = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in values.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

async def change_user_password(
    db: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
) -> str:
    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")

    token = _new_token_value()
    expires = _new_token_expires()
    result = await db.execute(select(Token).where(Token.user_id == user.id))
    existing_token = result.scalar_one_or_none()

    try:
        user.password = get_hashed_password(new_password)
        if existing_token:
            existing_token.token = token
            existing_token.expires = expires
        else:
            db.add(Token(user_id=user.id, token=token, expires=expires))

        await db.commit()
        return token
    except Exception:
        await db.rollback()
        raise
