from pydantic import BaseModel, ConfigDict, Field


class FavoriteCheck(BaseModel):


    is_favorite: bool
