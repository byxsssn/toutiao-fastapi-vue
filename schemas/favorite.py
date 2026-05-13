from pydantic import BaseModel, ConfigDict, Field


class FavoriteCheck(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_favorite: bool = Field(..., alias="isFavorite")


class FavoriteAdd(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    news_id: int = Field(..., alias="newsId")
