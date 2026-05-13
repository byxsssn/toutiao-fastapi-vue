from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from crud.users import (
    authenticate_user,
    create_user_with_token,
    get_user_by_username,
    refresh_user_token,
    update_user_profile,
    change_user_password
)
from schemas.users import UserAuthResponse, UserLogin, UserRegister, UserResponse, UserUpdate, UserChangePassword
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter()


@router.post("/")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user, token = await create_user_with_token(db, user_data)
    response_data = UserAuthResponse(
        token=token,
        userinfo=UserResponse.model_validate(new_user),
    )
    return success_response(data=response_data, message="注册成功")


@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = await refresh_user_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        userinfo=UserResponse.model_validate(user),
    )
    return success_response(data=response_data, message="登录成功")


@router.get("/info")
async def get_my_info(current_user=Depends(get_current_user)):
    return success_response(data=UserResponse.model_validate(current_user), message="获取用户信息成功")


@router.patch("/info")
async def update_my_info(
    user_update: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await update_user_profile(db, current_user.id, user_update)
    return success_response(data=UserResponse.model_validate(updated_user), message="更新用户信息成功")

@router.put("/password")
async def change_password(
    password_data: UserChangePassword,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    old_password = password_data.old_password
    new_password = password_data.new_password
    token = await change_user_password(db, user, old_password, new_password)
    response_data = UserAuthResponse(
        token=token,
        userinfo=UserResponse.model_validate(user),
    )
    return success_response(data=response_data, message="密码修改成功")
