from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from crud.news import get_active_categories, get_news_detail, get_news_list
from schemas.news import CategoryListResponse, NewsDetailResponse, NewsListResponse

router = APIRouter()


@router.get("/", response_model=CategoryListResponse)
async def categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    categories = await get_active_categories(db, skip=skip, limit=limit)
    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories,
    }


@router.get("/list", response_model=NewsListResponse)
async def news_list(
    category_id: int = Query(alias="categoryId"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, alias="pageSize", ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    articles, total = await get_news_list(
        db,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )

    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": articles,
            "total": total,
            "hasMore": page * page_size < total,
        },
    }


@router.get("/detail", response_model=NewsDetailResponse)
async def news_detail(
    article_id: int = Query(alias="id"),
    db: AsyncSession = Depends(get_db),
):
    article = await get_news_detail(db, article_id=article_id)

    if article is None:
        raise HTTPException(status_code=404, detail="新闻不存在")

    return {
        "code": 200,
        "message": "success",
        "data": article,
    }
