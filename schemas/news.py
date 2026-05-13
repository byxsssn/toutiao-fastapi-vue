from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sort_order: int
    is_active: bool
    created_at: datetime


class CategoryListResponse(BaseModel):
    code: int
    message: str
    data: list[NewsCategoryOut]


class NewsArticleOut(BaseModel):
    id: int
    category_id: int
    category: str | None
    title: str
    description: str
    content: str
    views: int
    created_at: datetime


class NewsListData(BaseModel):
    list: list[NewsArticleOut]
    total: int
    hasMore: bool


class NewsListResponse(BaseModel):
    code: int
    message: str
    data: NewsListData


class RelatedNewsOut(BaseModel):
    id: int
    title: str
    image: str | None


class NewsDetailOut(BaseModel):
    id: int
    title: str
    content: str
    image: str | None
    author: str | None
    publishTime: datetime
    categoryId: int
    views: int
    relatedNews: list[RelatedNewsOut]


class NewsDetailResponse(BaseModel):
    code: int
    message: str
    data: NewsDetailOut

class UserUpdateInfo(BaseModel):
    nikename: str | None = None
    avatar: str | None = None
    gender: str | None = None
    bio: str | None = None
    phone: str | None = None
