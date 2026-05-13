from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    gender: str | None = None


class UserAuthResponse(BaseModel):
    token: str
    userinfo: UserResponse


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    phone: str | None = None
    gender: str | None = None


class UserChangePassword(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    old_password: str = Field(..., description="旧密码", alias="oldPassword")
    new_password: str = Field(..., min_length=6, description="新密码", alias="newPassword")
