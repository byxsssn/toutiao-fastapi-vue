from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.news import router as news_router
from routers.users import router as users_router
from routers.favorite import router as favorite_router
from utils.exception_handlers import register_exception_handlers

app = FastAPI(title="Toutiao Backend")
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router, prefix="/news", tags=["news"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(favorite_router, prefix="/favorites", tags=["favorites"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
