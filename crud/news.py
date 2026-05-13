from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import NewsArticle, NewsCategory


async def get_active_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
) -> list[NewsCategory]:
    statement = (
        select(NewsCategory)
        .where(NewsCategory.is_active.is_(True))
        .order_by(NewsCategory.sort_order, NewsCategory.id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_news_list(
    db: AsyncSession,
    category_id: int,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[dict], int]:
    offset = (page - 1) * page_size

    total_statement = (
        select(func.count())
        .select_from(NewsArticle)
        .where(
            NewsArticle.category_id == category_id,
            NewsArticle.is_active.is_(True),
        )
    )
    total = await db.scalar(total_statement)

    list_statement = (
        select(NewsArticle, NewsCategory.name.label("category"))
        .join(NewsCategory, NewsArticle.category_id == NewsCategory.id, isouter=True)
        .where(
            NewsArticle.category_id == category_id,
            NewsArticle.is_active.is_(True),
        )
        .order_by(NewsArticle.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(list_statement)

    articles = [
        _article_list_item(article=article, category=category)
        for article, category in result.all()
    ]

    return articles, total or 0


async def get_news_detail(db: AsyncSession, article_id: int) -> dict | None:
    await db.execute(
        update(NewsArticle)
        .where(
            NewsArticle.id == article_id,
            NewsArticle.is_active.is_(True),
        )
        .values(views=NewsArticle.views + 1)
    )
    await db.commit()

    detail_statement = (
        select(NewsArticle, NewsCategory.name.label("category"))
        .join(NewsCategory, NewsArticle.category_id == NewsCategory.id, isouter=True)
        .where(
            NewsArticle.id == article_id,
            NewsArticle.is_active.is_(True),
        )
    )
    result = await db.execute(detail_statement)
    row = result.first()

    if row is None:
        return None

    article, category = row
    related_statement = (
        select(NewsArticle)
        .where(
            NewsArticle.category_id == article.category_id,
            NewsArticle.id != article.id,
            NewsArticle.is_active.is_(True),
        )
        .order_by(NewsArticle.id.desc())
        .limit(3)
    )
    related_result = await db.execute(related_statement)

    return _article_detail_item(
        article=article,
        category=category,
        related_articles=list(related_result.scalars().all()),
    )


def _article_list_item(article: NewsArticle, category: str | None) -> dict:
    return {
        "id": article.id,
        "category_id": article.category_id,
        "category": category,
        "title": article.title,
        "description": article.description,
        "content": article.content,
        "views": article.views,
        "created_at": article.created_at,
    }


def _article_detail_item(
    article: NewsArticle,
    category: str | None,
    related_articles: list[NewsArticle],
) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "image": None,
        "author": category,
        "publishTime": article.created_at,
        "categoryId": article.category_id,
        "views": article.views,
        "relatedNews": [_related_article_item(article) for article in related_articles],
    }


def _related_article_item(article: NewsArticle) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "image": None,
    }
